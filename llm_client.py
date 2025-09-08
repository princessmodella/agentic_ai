import os
import requests

HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL = "gpt2-medium"

headers = {"Authorization": f"Bearer {HF_API_KEY}"}

def query_hf(prompt):
    response = requests.post(
        f"https://api-inference.huggingface.co/models/{HF_MODEL}",
        headers=headers,
        json={"inputs": prompt}
    )
    response.raise_for_status()  # will raise 401 if unauthorized
    return response.json()
