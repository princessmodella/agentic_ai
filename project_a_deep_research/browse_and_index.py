# project_a_deep_research/browse_and_index.py
from playwright.sync_api import sync_playwright
from sentence_transformers import SentenceTransformer
import chromadb, time
from project_a_deep_research.fetch_with_retry import fetch_url

MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 800

# Fetch page text using Playwright
def fetch_text_playwright(url: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=30000)
        body = page.text_content("body") or ""
        browser.close()
    return body

# Split text into chunks
def chunk_text(text: str, chunk_size=CHUNK_SIZE):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

# Fetch, chunk, and store in ChromaDB
def index_url(url: str):
    start = time.time()

    text = fetch_text_playwright(url)
    if not text.strip():
        text = fetch_url(url)  # fallback for static pages

    chunks = chunk_text(text)
    model = SentenceTransformer(MODEL)

    client = chromadb.Client()
    col = client.get_or_create_collection("webdocs")

    embs = [model.encode(c).tolist() for c in chunks]
    ids = [f"{url}__{i}" for i in range(len(chunks))]
    metas = [{"url": url} for _ in range(len(chunks))]

    col.add(documents=chunks, embeddings=embs, ids=ids, metadatas=metas)

    print(f"Indexed {len(chunks)} chunks for {url} in {time.time()-start:.2f}s")

if __name__ == "__main__":
    index_url("https://example.com")
