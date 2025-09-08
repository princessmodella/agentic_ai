# rag_query.py

import os
import openai
from huggingface_hub import InferenceClient

from indexer import query_vector_db
from llm_client import query_hf

def query_rag(question: str):
    docs = query_vector_db(question)
    context = "\n".join(docs)
    prompt = f"Use the following context to answer the question:\n\n{context}\n\nQuestion: {question}\nAnswer:"
    answer = query_hf(prompt)
    return answer
