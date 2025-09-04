# project_a_deep_research/browse_and_index.py
from typing import List, Dict
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from sentence_transformers import SentenceTransformer
import chromadb
import hashlib
import time
from tools.tracing import start_span, end_span

MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 800  # characters per chunk (simple and understandable)

def fetch_text_playwright(url: str, max_wait: int = 20000) -> str:
    """Fetch rendered page text using Playwright (suitable for JS-driven pages)."""
    span = start_span("fetch_text_playwright", {"url": url})
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=max_wait)
            # get main textual body; best-effort
            body = page.text_content("body") or ""
            browser.close()
        end_span(span, status="ok", output={"len": len(body)})
        return body
    except PlaywrightTimeoutError as e:
        end_span(span, status="error", error=e)
        raise
    except Exception as e:
        end_span(span, status="error", error=e)
        raise

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> List[str]:
    """Split text into chunks of chunk_size characters.
    This is a simple deterministic approach friendly to interviewers.
    """
    text = text.strip()
    if not text:
        return []
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def index_url(url: str, collection_name: str = "webdocs", model_name: str = MODEL,
              max_chunks: int = 50) -> Dict:
    """Fetch a URL, chunk it and index chunks into Chroma. Returns a summary dict."""
    span = start_span("index_url", {"url": url})
    try:
        raw = fetch_text_playwright(url)
        if not raw.strip():
            raise ValueError("Fetched text empty")

        chunks = chunk_text(raw, CHUNK_SIZE)[:max_chunks]
        model = SentenceTransformer(model_name)
        embs = [model.encode(c).tolist() for c in chunks]

        client = chromadb.Client()
        col = client.get_or_create_collection(collection_name)

        # create deterministic ids so repeated indexing doesn't create duplicates
        base = hashlib.sha1(url.encode()).hexdigest()[:8]
        ids = [f"{base}__{i}" for i in range(len(chunks))]
        metas = [{"url": url, "index": i} for i in range(len(chunks))]

        col.add(documents=chunks, embeddings=embs, ids=ids, metadatas=metas)
        end_span(span, status="ok", output={"n_chunks": len(chunks)})
        return {"url": url, "indexed_chunks": len(chunks), "ids": ids}
    except Exception as e:
        end_span(span, status="error", error=e)
        raise
