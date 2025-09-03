import os
import hashlib
from sentence_transformers import SentenceTransformer
import chromadb

MODEL_PATH = "all-MiniLM-L6-v2"

def top_k_retrieve(query, k=3):
    model = SentenceTransformer(MODEL_PATH)
    q_emb = model.encode(query).tolist()

    client = chromadb.Client()
    try:
        collection = client.get_collection("webdocs")
    except chromadb.errors.NotFoundError:
        collection = client.get_or_create_collection("webdocs")

    # If collection is empty, add sample docs
    if len(collection.get()["documents"]) == 0:
        print("No documents found. Indexing sample documents...")
        sample_docs = [
            "Playwright automates browsers for web scraping.",
            "LangGraph helps build agent workflows."
        ]
        embeddings = [model.encode(d).tolist() for d in sample_docs]
        collection.add(
            documents=sample_docs,
            embeddings=embeddings,
            ids=["doc1", "doc2"],
            metadatas=[{"url": "https://playwright.dev"}, {"url": "https://langgraph.com"}]
        )
        print("Sample documents indexed!")

    result = collection.query(query_embeddings=[q_emb], n_results=k)
    docs = result.get("documents", [[]])[0]
    metas = result.get("metadatas", [[]])[0]
    return list(zip(docs, metas))

def simple_summarize(hits):
    summary = "## Summary\n\n"
    for i, (doc, meta) in enumerate(hits):
        url = meta.get("url", "unknown")
        snippet = (doc[:300] + "...") if doc else ""
        summary += f"- Source {i+1}: {url} — {snippet}\n\n"
    return summary

def write_report(query, hits):
    report = f"# Research Report: {query}\n\n"
    report += simple_summarize(hits)
    report += "\n## Sources\n"
    for i, (_, meta) in enumerate(hits):
        report += f"{i+1}. {meta.get('url','unknown')}\n"

    os.makedirs("reports", exist_ok=True)
    slug = hashlib.sha1(query.encode()).hexdigest()[:8]
    path = f"reports/report_{slug}.md"

    with open(path, "w", encoding="utf-8") as f:
        f.write(report)

    return path

if __name__ == "__main__":
    query_text = "What is Playwright?"
    hits = top_k_retrieve(query_text)
    if hits:
        path = write_report(query_text, hits)
        print("Report saved to", path)
    else:
        print("No hits found even after indexing sample documents.")
