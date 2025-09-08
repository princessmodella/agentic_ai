import requests
import os

HF_API_TOKEN = os.getenv("HF_API_TOKEN")  # Make sure you set this in your .env
DEFAULT_MODEL = "gpt2"  # fallback if gpt2-medium not available

def query_hf(prompt: str, model: str = "gpt2-medium"):
    API_URL = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt}, timeout=30)
        
        # Handle errors gracefully
        if response.status_code == 404:
            print(f"[WARN] Model {model} not found. Falling back to {DEFAULT_MODEL}.")
            return query_hf(prompt, model=DEFAULT_MODEL)
        elif response.status_code == 401:
            return {"error": "Unauthorized. Check your Hugging Face token."}
        elif response.status_code >= 500:
            return {"error": f"Server error {response.status_code}. Try again later."}
        
        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Try again."}
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
