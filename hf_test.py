import os
import sys
from transformers import pipeline
from fetch import fetch_web
import PyPDF2
from langchain.document_loaders import PyPDFLoader
from langchain.chains.summarize import load_summarize_chain
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

# Load models
print("Loading models...")
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
generator = pipeline("text-generation", model="gpt2")
print("Models loaded successfully.\n")

# PDF Summarization
def summarize_pdf(pdf_path):
    if not os.path.exists(pdf_path):
        print(f"PDF not found: {pdf_path}")
        return ""

    print(f"Extracting text from {pdf_path}...")
    loader = PyPDFLoader(pdf_path)
    documents = loader.load_and_split()
    print("Text extracted, summarizing now...")

    chain = load_summarize_chain(summarizer, chain_type="map_reduce")
    summary = chain.run(documents)
    print("PDF Summary:\n", summary, "\n")
    return summary

# Text Generation
def generate_text(prompt):
    print(f"Generating text for prompt:\n{prompt}\n")
    generated = generator(prompt, max_length=200, num_return_sequences=1)
    text_out = generated[0]['generated_text']
    print("Generated Text:\n", text_out, "\n")
    return text_out

# Web Search & Summarize
def search_and_summarize(query):
    print(f"Fetching web results for: {query}")
    content = fetch_web(query)
    if not content:
        print("No web content found.")
        return ""

    print("Summarizing fetched content...")
    summary = summarizer(content, max_length=200, min_length=50, do_sample=False)
    summary_text = summary[0]['summary_text']
    print("Web Summary:\n", summary_text, "\n")
    return summary_text

# Main Execution
if __name__ == "__main__":
    # Example PDF summarization
    pdf_summary = summarize_pdf("example.pdf")

    # Generate text based on PDF summary
    generate_text(f"Based on the PDF summary, write a short report:\n{pdf_summary}")

    # Optional web search + summarize
    web_summary = search_and_summarize("Latest AI breakthroughs 2025")
