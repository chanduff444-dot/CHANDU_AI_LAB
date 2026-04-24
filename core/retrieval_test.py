import chromadb
from sentence_transformers import SentenceTransformer

# -------- CONFIG -------- #

CHROMA_PATH = "data/vector_store"
COLLECTION_NAME = "chandu_docs"

# -------- INITIALIZE -------- #

print("🚀 Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

print("🗄 Connecting to persistent Chroma DB...")
client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_collection(name=COLLECTION_NAME)

print("✅ Ready.\n")

# -------- QUERY LOOP -------- #

while True:
    query = input("Ask something (or type 'exit'): ")

    if query.lower() == "exit":
        break

    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    print("\n🔎 Top Matches:\n")

    for i, doc in enumerate(results["documents"][0]):
        print(f"Result {i+1}:")
        print(doc)
        print("-" * 50)
