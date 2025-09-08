# indexer.py
import os
from typing import List, Dict
import chromadb
from chromadb import Settings
from sentence_transformers import SentenceTransformer
import openai
import uuid

# -------------------- Initialize -------------------- #
# OpenAI API key from environment
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not set. Please set OPENAI_API_KEY in env or Streamlit secrets.")

openai.api_key = OPENAI_API_KEY

# ChromaDB setup
client = chromadb.Client(Settings())
COLLECTION_NAME = "documents"

if COLLECTION_NAME not in [c.name for c in client.list_collections()]:
    collection = client.create_collection(name=COLLECTION_NAME)
else:
    collection = client.get_collection(name=COLLECTION_NAME)

# Embedding model
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# -------------------- Core Functions -------------------- #
def add_documents_from_text(text, source="uploaded_document"):
    embedding = embed_model.encode([text])
    collection.add(
        documents=[text],
        embeddings=embedding,
        metadatas=[{"source": source}],
        ids=[str(uuid.uuid4())]   # required unique id
    )

def top_k_retrieve(query: str, k: int = 5) -> List[Dict]:
    """Retrieve top-k relevant documents from the collection for a query."""
    if not collection.count():
        return []

    embedding = embed_model.encode([query]).tolist()
    results = collection.query(query_embeddings=embedding, n_results=k)
    hits = []
    for doc, meta, score in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
        hits.append({
            "document": doc,
            "metadata": meta,
            "score": score
        })
    return hits

def generate_answer(question: str, context_hits: List[Dict]) -> str:
    """Generate answer using OpenAI GPT-4 (or GPT-3.5) given question + context."""
    context_text = "\n\n".join([h['document'][:2000] for h in context_hits])  # limit length for token budget
    prompt = (
        f"Answer the following question based on the provided context.\n\n"
        f"Context:\n{context_text}\n\nQuestion: {question}\nAnswer:"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # you can use "gpt-4" if available
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.2
        )
        answer = response['choices'][0]['message']['content'].strip()
        return answer
    except Exception as e:
        return f"Error generating answer: {e}"

def reset_collection() -> str:
    """Delete all documents in the collection and recreate it."""
    global collection
    client.delete_collection(COLLECTION_NAME)
    collection = client.create_collection(name=COLLECTION_NAME)
    return "✅ Collection has been reset."
