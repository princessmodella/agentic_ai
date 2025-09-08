# utils.py
import re
from typing import List

import os
from fetch import fetch_url

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def save_file(uploaded_file):
    file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def summarize_file(file_path: str):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    # Use HF LLM to summarize
    from llm_client import query_hf
    summary = query_hf(f"Summarize this text concisely:\n\n{text}\n\nSummary:")
    return summary
