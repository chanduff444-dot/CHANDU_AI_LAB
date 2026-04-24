# ============================================
# CHANDU AI LAB - RAG ENGINE (CONTROLLED)
# Phase 2 Personality-Stable Version
# ============================================

import chromadb
from sentence_transformers import SentenceTransformer
from core.router import generate_response, choose_model
from core.logger import log_interaction
from core.difficulty_engine import escalate_response
from core.skill_map import update_skill_progress


# -------- CONFIG -------- #

CHROMA_PATH = "data/vector_store"
COLLECTION_NAME = "chandu_docs"

RETRIEVAL_TRIGGERS = [
    "from my notes",
    "from my pdf",
    "based on my material",
    "in my notes",
    "from uploaded",
    "according to my"
]

# -------- INITIALIZE -------- #

print("🚀 Loading embedding model for RAG...")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

print("🗄 Connecting to persistent Chroma DB...")
client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_collection(name=COLLECTION_NAME)

print("✅ RAG Engine Ready.\n")


# ============================================
# RETRIEVAL DECISION
# ============================================

def should_use_retrieval(query: str) -> bool:
    lower_query = query.lower()
    return any(trigger in lower_query for trigger in RETRIEVAL_TRIGGERS)


# ============================================
# RETRIEVE CONTEXT
# ============================================

def retrieve_context(query: str, top_k=3) -> str:
    query_embedding = embedding_model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    documents = results["documents"][0]
    return "\n\n".join(documents)


# ============================================
# STRICT SYSTEM INSTRUCTION
# ============================================

SYSTEM_INSTRUCTION = """
You are Chandu AI Lab, an analytical and technical AI system.

Core Behavior Rules:
- Provide structured, logical, and precise responses.
- Focus on knowledge delivery and problem-solving.
- Do NOT provide emotional counseling unless explicitly asked.
- Do NOT assume crisis unless clearly stated.
- Maintain professional and grounded tone.
- Avoid generic therapy advice.
"""


# ============================================
# MAIN RAG GENERATION FUNCTION
# ============================================

def rag_generate(query: str) -> str:

    retrieval_used = should_use_retrieval(query)
    selected_model = choose_model(query)

    # -----------------------------
    # Retrieval Path
    # -----------------------------
    if retrieval_used:
        print("🔎 Retrieval triggered.")

        context = retrieve_context(query)

        enriched_prompt = f"""
{SYSTEM_INSTRUCTION}

Use the following context from my uploaded materials:

{context}

Now answer the user query clearly and structurally:

{query}
"""

        response = generate_response(enriched_prompt)

    # -----------------------------
    # Direct Generation Path
    # -----------------------------
    else:
        print("⚡ No retrieval needed. Direct model response.")

        enriched_prompt = f"""
{SYSTEM_INSTRUCTION}

User Query:
{query}

Provide a structured and analytical response.
"""

        response = generate_response(enriched_prompt)

    # -----------------------------
    # Logging
    # -----------------------------
    log_interaction(
        query=query,
        response=response,
        model_used=selected_model,
        retrieval_used=retrieval_used
    )

    # -----------------------------
    # Skill Progress Update
    # -----------------------------
    update_skill_progress(query)

    # -----------------------------
    # Difficulty Escalation Layer
    # -----------------------------
    final_response = escalate_response(response, query)

    return final_response
