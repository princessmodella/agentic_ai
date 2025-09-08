import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load environment variables
load_dotenv()

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_MODEL = os.getenv("HF_MODEL", "bigscience/bloom-560m")

# Debug check
print("HF_API_TOKEN loaded:", HF_API_TOKEN[:10] + "..." if HF_API_TOKEN else "❌ NOT FOUND")
print("HF_MODEL:", HF_MODEL)

# Create Hugging Face inference client
client = InferenceClient(model=HF_MODEL, token=HF_API_TOKEN)

def query_hf(prompt: str):
    """Query Hugging Face model and return text response"""
    try:
        response = client.text_generation(
            prompt,
            max_new_tokens=200,
            temperature=0.7,
            do_sample=True
        )
        return {"text": response}
    except Exception as e:
        return {"error": str(e)}
