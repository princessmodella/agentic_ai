import os
import requests
from dotenv import load_dotenv

# Load .env
load_dotenv()



HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_MODEL = os.getenv("HF_MODEL", "gpt2")  # fallback to gpt2 if not set

print("HF_API_TOKEN loaded:", HF_API_TOKEN[:10] + "..." if HF_API_TOKEN else "❌ None")

if not HF_API_TOKEN:
    raise ValueError("❌ Missing Hugging Face token! Set HF_API_TOKEN in your .env file.")

def query_hf(prompt: str, model: str = None):
    model = model or HF_MODEL
    API_URL = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
    response.raise_for_status()
    return response.json()
