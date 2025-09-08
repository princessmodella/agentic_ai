import os
import requests

HF_TOKEN = os.getenv("HF_API_TOKEN")
HF_MODEL = os.getenv("HF_MODEL", "gpt2-medium")
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

def query_hf(prompt: str, max_new_tokens: int = 200):
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": max_new_tokens}}
    response = requests.post(HF_API_URL, headers=HEADERS, json=payload, timeout=60)
    response.raise_for_status()
    result = response.json()
    if isinstance(result, list) and "generated_text" in result[0]:
        return result[0]["generated_text"]
    return str(result)
