import os
import openai
from huggingface_hub import InferenceClient


openai.api_key = os.getenv("OPENAI_API_KEY")
hf_client = InferenceClient(api_key=os.getenv("HF_API_KEY"))


def query_gpt(prompt):
    try:
        # Try OpenAI first
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as e:
        print("OpenAI failed, falling back to Hugging Face:", e)

        # Fallback to Hugging Face
        try:
            response = hf_client.text_generation(
                "google/flan-t5-large",
                prompt,
                max_new_tokens=300
            )
            return response
        except Exception as hf_e:
            return f"Both OpenAI and Hugging Face failed: {hf_e}"

def query_gpt(question: str, context: str, api_key: str):
    
    openai.api_key = api_key
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Answer this question based on context:\nContext: {context}\nQuestion: {question}",
        max_tokens=200
    )
    return response.choices[0].text.strip()
