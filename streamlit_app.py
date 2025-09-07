# streamlit_app.py
import os
import io
import streamlit as st
from reportlab.pdfgen import canvas
import fitz  # PyMuPDF
import docx
from docx import Document

# --- Handle OpenAI API Key ---
# On Streamlit Cloud, store in Secrets. Locally, use environment variable or .env
if "OPENAI_API_KEY" not in os.environ:
    try:
        os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass

# --- Fallback for streamlit_option_menu ---
try:
    from streamlit_option_menu import option_menu
except ModuleNotFoundError:
    def option_menu(title, options, icons=None, menu_icon=None, default_index=0):
        """Fallback sidebar menu using native Streamlit radio."""
        return st.sidebar.radio(title, options, index=default_index)

# --- Import local modules that rely on OPENAI_API_KEY ---
from indexer import add_documents_from_text, top_k_retrieve, generate_answer, reset_collection

st.set_page_config(page_title="Deep RAG Engine", page_icon="🤖", layout="wide")

# ---------------- Utility: Download Buttons ---------------- #
def download_buttons(content: str, filename_prefix: str = "report"):
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
    
    # TXT
    txt_data = io.BytesIO(content.encode("utf-8"))
    with col1:
        st.download_button(
            "⬇️ TXT",
            data=txt_data,
            file_name=f"{filename_prefix}.txt",
            mime="text/plain"
        )

    # PDF
    pdf_data = io.BytesIO()
    c = canvas.Canvas(pdf_data)
    text_obj = c.beginText(40, 800)
    for line in content.split("\n"):
        text_obj.textLine(line)
    c.drawText(text_obj)
    c.save()
    pdf_data.seek(0)
    with col2:
        st.download_button(
            "⬇️ PDF",
            data=pdf_data,
            file_name=f"{filename_prefix}.pdf",
            mime="application/pdf"
        )

    # DOCX
    doc = Document()
    for line in content.split("\n"):
        doc.add_paragraph(line)
    docx_data = io.BytesIO()
    doc.save(docx_data)
    docx_data.seek(0)
    with col3:
        st.download_button(
            "⬇️ DOCX",
            data=docx_data,
            file_name=f"{filename_prefix}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    # Copy to clipboard
    with col4:
        st.text_area("📋 Copy", content, height=120)

# ---------------- Sidebar ---------------- #
with st.sidebar:
    selected = option_menu(
        "Deep RAG Engine",
        ["Home", "Ask Question", "Upload & Summarize", "Admin"],
        icons=["house", "question-circle", "file-earmark-text", "gear"],
        menu_icon="robot"
    )

# ---------------- Home ---------------- #
if selected == "Home":
    st.title("🤖 Deep RAG Engine")
    try:
        st.image("banner.webp", width='stretch' if hasattr(st, "experimental") else None)
    except Exception:
        st.info("Banner image not found.")
    st.write(
        "Ask questions, index web pages or documents, and generate reports. Use the menu to get started."
    )

# ---------------- Ask Question ---------------- #
elif selected == "Ask Question":
    st.title("💬 Ask a Question")
    question = st.text_input("Type your question here")
    with st.expander("Options"):
        k = st.number_input("How many context hits to retrieve (k)", min_value=1, max_value=10, value=4)

    if st.button("Get Answer") and question.strip():
        with st.spinner("Retrieving context..."):
            hits = top_k_retrieve(question, k=k)
        context_text = "\n\n".join(
            [f"[{i+1}] {h['document'][:1000]} (source: {h['metadata'].get('source','n/a')})"
             for i, h in enumerate(hits)]
        ) if hits else "No documents found in the index."

        with st.spinner("Generating answer from OpenAI..."):
            answer = generate_answer(question, hits)
        st.subheader("📝 Answer")
        st.write(answer)
        st.markdown("---")
        st.subheader("Retrieved Context (top results)")
        st.write(context_text)
        download_buttons(answer, "answer")

# ---------------- Upload & Summarize ---------------- #
elif selected == "Upload & Summarize":
    st.title("📂 Upload & Summarize")
    uploaded_files = st.file_uploader(
        "Upload PDF, TXT, or DOCX (multiple allowed)",
        type=["pdf","txt","docx"],
        accept_multiple_files=True
    )

    if uploaded_files:
        combined_text = ""
        for f in uploaded_files:
            if f.type == "application/pdf":
                pdf = fitz.open(stream=f.read(), filetype="pdf")
                for page in pdf:
                    combined_text += page.get_text()
            elif f.type == "text/plain":
                combined_text += f.read().decode("utf-8")
            elif f.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc = docx.Document(f)
                for p in doc.paragraphs:
                    combined_text += p.text + "\n"
            combined_text += "\n\n"

        if combined_text.strip():
            add_documents_from_text(combined_text, source="uploaded_document")
            st.success("Document(s) added to index.")
            st.subheader("Summary (from retrieval + OpenAI):")
            hits = top_k_retrieve("Summarize this document", k=5)
            answer = generate_answer("Summarize this document", hits)
            st.write(answer)
            download_buttons(answer, "document_summary")
        else:
            st.error("No readable text found in the uploaded file(s).")

# ---------------- Admin ---------------- #
elif selected == "Admin":
    st.title("⚙️ Admin")
    if st.button("Reset (delete) collection"):
        msg = reset_collection()
        st.success(msg)
    st.info(
        "Keep your OpenAI key in Streamlit secrets or environment variables. Do NOT paste it here."
    )
