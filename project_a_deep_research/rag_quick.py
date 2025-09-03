from sentence_transformers import SentenceTransformer
import chromadb

def main():
    model = SentenceTransformer("all-MiniLM-L6-v2")
    client = chromadb.Client()
    col = client.get_or_create_collection("demo_collection")

    docs = [
        "LangGraph helps build workflows.",
        "Playwright extracts text from websites."
    ]

    embeddings = [model.encode(doc).tolist() for doc in docs]

    try:
        col.add(documents=docs, embeddings=embeddings, ids=["d1", "d2"])
    except Exception:
        pass

    query_embedding = model.encode("What is Playwright?").tolist()
    results = col.query(query_embeddings=[query_embedding], n_results=2)

    print("Documents found:", results.get("documents"))

if __name__ == "__main__":
    main()
