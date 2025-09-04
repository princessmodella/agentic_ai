# project_a_deep_research/rag_quick.py
import os
import hashlib
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from typing import List, Tuple, Union
from sentence_transformers import SentenceTransformer
import chromadb
from tools.tracing import start_span, end_span
from project_a_deep_research.browse_and_index import fetch_text_playwright


# Global settings
MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION_NAME = "webdocs"

# Load model once (not every query)
_model = SentenceTransformer(MODEL_NAME)

def ensure_collection() -> chromadb.Collection:
    """Get or create the ChromaDB collection."""
    client = chromadb.Client()
    return client.get_or_create_collection(COLLECTION_NAME)

def add_url_to_collection(url: str) -> None:
    """Fetch a URL, embed its content, and add to ChromaDB."""
    col = ensure_collection()
    text = fetch_text_playwright(url)
    if not text.strip():
        return
    emb = _model.encode(text).tolist()
    doc_id = hashlib.sha1(url.encode()).hexdigest()
    col.add(
        documents=[text],
        embeddings=[emb],
        ids=[doc_id],
        metadatas=[{"url": url}]
    )

def top_k_retrieve(query: str, k: int = 3) -> List[Tuple[str, dict]]:
    """
    Return top-k (document_chunk, metadata) for a query or URL.
    - If input looks like a URL, fetch & index it before querying.
    - Otherwise, treat it as a plain text query.
    """
    span = start_span("top_k_retrieve", {"query": query, "k": k})
    try:
        # Detect URL input
        if query.startswith("http://") or query.startswith("https://"):
            add_url_to_collection(query)
            search_text = f"Content from {query}"
        else:
            search_text = query

        q_emb = _model.encode(search_text).tolist()
        col = ensure_collection()
        res = col.query(query_embeddings=[q_emb], n_results=k)
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        hits = list(zip(docs, metas))

        # Fallback if no results
        if not hits:
            hits = [("No relevant documents found.", {"url": "none"})]

        end_span(span, status="ok", output={"n_results": len(hits)})
        return hits
    except Exception as e:
        end_span(span, status="error", error=e)
        raise

def write_report(query: str, hits: List[Tuple[str, dict]]) -> str:
    """
    Write a Markdown report summarizing retrieved documents.
    Returns path to the saved file.
    """
    span = start_span("write_report", {"query": query, "n_hits": len(hits)})
    try:
        md = f"# Research Report: {query}\n\n"
        md += "## Summary\n\n"
        for i, (doc, meta) in enumerate(hits, start=1):
            src = meta.get("url", "unknown")
            snippet = (doc[:300] + "...") if doc else ""
            md += f"### {i}. Source: {src}\n\n{snippet}\n\n"

        md += "## Sources\n"
        for i, (_, meta) in enumerate(hits, start=1):
            md += f"{i}. {meta.get('url', 'unknown')}\n"

        os.makedirs("reports", exist_ok=True)
        slug = hashlib.sha1(query.encode()).hexdigest()[:8]
        path = f"reports/report_{slug}.md"
        with open(path, "w", encoding="utf-8") as f:
            f.write(md)

        end_span(span, status="ok", output={"path": path})
        return path
    except Exception as e:
        end_span(span, status="error", error=e)
        raise
