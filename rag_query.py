# rag_query.py

import os
import openai
from huggingface_hub import InferenceClient

from llm_client import query_hf

def query_rag(question: str):
    prompt = f"Answer the following question in detail:\n\n{question}\n\n"
    result = query_hf(prompt)

    if isinstance(result, dict) and "error" in result:
        return f"⚠️ Error: {result['error']}"
    
    # Hugging Face returns a list of dicts with "generated_text"
    try:
        return result[0]["generated_text"]
    except Exception:
        return "⚠️ Unexpected response format from model."
