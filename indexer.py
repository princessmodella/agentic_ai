import chromadb
from sentence_transformers import SentenceTransformer

# Initialize ChromaDB and embedding model
client = chromadb.Client()
collection_name = "documents"

if collection_name not in [c.name for c in client.list_collections()]:
    collection = client.create_collection(name=collection_name)
else:
    collection = client.get_collection(name=collection_name)

embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# Add text to the collection
def add_to_collection(text: str):
    embeddings = embed_model.encode([text]).tolist()
    collection.add(documents=[text], embeddings=embeddings)

# Retrieve most relevant documents
def retrieve(query: str, top_k: int = 5):
    embedding = embed_model.encode([query]).tolist()
    results = collection.query(query_embeddings=embedding, n_results=top_k)
    docs = results["documents"][0] if results["documents"] else []
    return docs

# Reset collection (delete all stored documents)
def reset_collection():
    global collection
    client.delete_collection(collection_name)
    collection = client.create_collection(name=collection_name)
    return "✅ Collection has been reset."
