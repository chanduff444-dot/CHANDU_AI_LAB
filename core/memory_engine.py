# ============================================
# CHANDU AI LAB - IMPORTANCE WEIGHTED MEMORY
# Phase 2 - Cognitive Memory Layer
# ============================================

import chromadb
from sentence_transformers import SentenceTransformer
import uuid
import time

MEMORY_PATH = "data/memory_store"
MEMORY_COLLECTION = "chandu_memory"

print("🧠 Initializing Importance-Weighted Memory Engine...")

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path=MEMORY_PATH)

try:
    collection = client.get_collection(MEMORY_COLLECTION)
except:
    collection = client.create_collection(MEMORY_COLLECTION)

print("✅ Memory Engine Ready.\n")


# ============================================
# IMPORTANCE SCORING HEURISTIC
# ============================================

def compute_importance(user_input: str) -> float:
    lower = user_input.lower()

    # Emotional signals increase importance
    emotional_keywords = [
        "struggle", "confused", "difficult", "important",
        "goal", "plan", "decision", "problem"
    ]

    if any(word in lower for word in emotional_keywords):
        return 0.8

    # Technical depth boost
    if any(word in lower for word in [
        "derive", "proof", "architecture",
        "optimization", "complexity"
    ]):
        return 0.9

    return 0.5  # default baseline


# ============================================
# STORE MEMORY
# ============================================

def store_memory(user_input: str, response: str):

    memory_text = f"""
User: {user_input}
Assistant: {response}
"""

    importance = compute_importance(user_input)

    embedding = embedding_model.encode(memory_text).tolist()

    collection.add(
        documents=[memory_text],
        embeddings=[embedding],
        metadatas=[{
            "importance": importance,
            "timestamp": time.time()
        }],
        ids=[str(uuid.uuid4())]
    )


# ============================================
# RETRIEVE MEMORY (Weighted)
# ============================================

def retrieve_memory(query: str, top_k=5):

    query_embedding = embedding_model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas"]
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    if not documents:
        return ""

    scored_memories = []

    for doc, meta in zip(documents, metadatas):

        # Handle old memories with no metadata
        if meta is None:
            importance = 0.5
        else:
            importance = meta.get("importance", 0.5)

        scored_memories.append((doc, importance))

    # Sort by importance descending
    scored_memories.sort(key=lambda x: x[1], reverse=True)

    top_memories = [doc for doc, _ in scored_memories[:3]]

    return "\n\n".join(top_memories)
