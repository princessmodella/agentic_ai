# indexer.py
import os
from typing import List, Dict
import chromadb
from chromadb import Settings
from sentence_transformers import SentenceTransformer
import openai
import uuid

# Init Chroma
client = chromadb.Client()
collection = client.get_or_create_collection("documents")

# Load embedding model
EMBED_MODEL = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def embed_text(text: str):
    return EMBED_MODEL.encode(text).tolist()

def add_document(doc_id: str, text: str):
    vector = embed_text(text)
    collection.add(ids=[doc_id], metadatas=[{"text": text}], embeddings=[vector])

def query_vector_db(query: str, top_k: int = 3):
    vector = embed_text(query)
    results = collection.query(query_embeddings=[vector], n_results=top_k)
    # returns list of document texts
    return [m["text"] for m in results['metadatas'][0]]
