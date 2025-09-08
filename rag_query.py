# rag_query.py

import os
import openai
from huggingface_hub import InferenceClient

# Load API keys from environment
openai.api_key = os.getenv("OPENAI_API_KEY")
hf_client = InferenceClient(api_key=os.getenv("HF_API_KEY"))

def query_gpt(prompt: str) -> str:
    """
    Try answering using OpenAI first.
    If OpenAI quota fails, fallback to Hugging Face.
    """
    # First: OpenAI
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # fast + cheap
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"[OpenAI ERROR] {e}")
        print("⚠️ Falling back to Hugging Face...")

        # Fallback: Hugging Face
        try:
            response = hf_client.text_generation(
                model="google/flan-t5-large",
                prompt=prompt,
                max_new_tokens=300,
                temperature=0.7,
            )
            # Some HF models return dict, some return str
            if isinstance(response, str):
                return response.strip()
            elif isinstance(response, dict) and "generated_text" in response:
                return response["generated_text"].strip()
            else:
                return str(response)

        except Exception as hf_e:
            print(f"[HF ERROR] {hf_e}")
            return "❌ Sorry, both OpenAI and Hugging Face failed. Try again later."
