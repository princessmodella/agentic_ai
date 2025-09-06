import fitz  # PyMuPDF
import docx
import requests
from bs4 import BeautifulSoup

def fetch_web(url):
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        # Remove scripts/styles
        for s in soup(['script','style']):
            s.extract()
        return soup.get_text(separator="\n")
    except Exception as e:
        return ""

def fetch_pdf(file_path_or_stream):
    text = ""
    pdf_doc = fitz.open(stream=file_path_or_stream, filetype="pdf")
    for page in pdf_doc:
        text += page.get_text()
    return text

def fetch_txt(file_stream):
    return file_stream.read().decode("utf-8")

def fetch_docx(file_stream):
    doc = docx.Document(file_stream)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text
