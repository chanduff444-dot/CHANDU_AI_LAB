import os
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb

# ---------------- CONFIG ---------------- #

DATASET_PATH = "datasets"
CHROMA_PATH = "data/vector_store"
COLLECTION_NAME = "chandu_docs"

# -------------- INITIALIZATION ----------- #

print("🚀 Initializing embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

print("🗄 Initializing persistent Chroma database...")
client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(name=COLLECTION_NAME)


# -------------- TEXT CHUNKING ------------ #

def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap

    return chunks


# -------------- PDF INGESTION ------------ #

def ingest_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        text = ""

        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted

        if not text.strip():
            print(f"⚠ No readable text in {file_path}")
            return

        chunks = chunk_text(text)

        for i, chunk in enumerate(chunks):
            embedding = model.encode(chunk).tolist()

            unique_id = f"{file_path}_{i}"

            collection.upsert(
                documents=[chunk],
                embeddings=[embedding],
                ids=[unique_id]
            )

        print(f"✅ Ingested: {file_path}")

    except Exception as e:
        print(f"❌ Error processing {file_path}")
        print(e)


# -------------- MAIN --------------------- #

def main():
    print("🔍 Scanning datasets folder...")

    for root, dirs, files in os.walk(DATASET_PATH):
        for file in files:
            if file.lower().endswith(".pdf"):
                full_path = os.path.join(root, file)
                ingest_pdf(full_path)

    print("🎉 Ingestion complete.")


if __name__ == "__main__":
    main()
