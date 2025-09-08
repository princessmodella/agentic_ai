# ---- lazy imports to avoid crashing the app in minimal Cloud env ----
def try_import(name):
    try:
        module = __import__(name)
        return module
    except Exception:
        return None

# explicitly import modules you use that are heavy
torch = try_import("torch")
sentence_transformers = try_import("sentence_transformers")
transformers = try_import("transformers")
chromadb = try_import("chromadb")
faiss = try_import("faiss")
onnxruntime = try_import("onnxruntime")
bs4 = try_import("bs4")
openai = try_import("openai")
reportlab = try_import("reportlab")
fitz = try_import("fitz")  # PyMuPDF
docx = try_import("docx")
# streamlit_app.py
import os
import io
import streamlit as st
from reportlab.pdfgen import canvas
import fitz  # PyMuPDF
import docx
from docx import Document
# put this at the top of streamlit_app.py (before any OpenAI call)
import os, sys
import streamlit as st

from rag_query import query_rag
from utils import save_file, summarize_file

st.set_page_config(page_title="Deep RAG Engine", layout="wide")

menu = ["Home", "Ask Question", "Upload & Summarize", "Admin"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Home":
    st.title("Deep RAG Engine")
    st.write("Welcome! Ask questions or summarize uploaded documents.")

elif choice == "Ask Question":
    st.subheader("💬 Ask a Question")
    question = st.text_area("Type your question here")
    if st.button("Get Answer"):
        if question.strip() != "":
            with st.spinner("Generating answer..."):
                answer = query_rag(question)
                st.success(answer)
        else:
            st.warning("Please enter a question.")

elif choice == "Upload & Summarize":
    st.subheader("📄 Upload & Summarize Files")
    uploaded_file = st.file_uploader("Choose a file", type=["txt", "md"])
    if uploaded_file:
        file_path = save_file(uploaded_file)
        with st.spinner("Summarizing..."):
            summary = summarize_file(file_path)
        st.success(summary)

elif choice == "Admin":
    st.subheader("⚙️ Admin Panel")
    st.write("Manage your documents and settings here.")
