# rag_query.py
from llm_client import query_hf

def query_rag(question: str):
    prompt = f"Answer the following question in detail:\n\n{question}\n\n"
    result = query_hf(prompt)

    if isinstance(result, dict) and "error" in result:
        code = result.get("code", "UNKNOWN")
        detail = result.get("detail", "")
        hint = ""
        if code == "NO_TOKEN":
            hint = " Ensure .env contains HF_API_TOKEN and restart Streamlit."
        elif code == "401":
            hint = " Your token may be invalid; regenerate at https://huggingface.co/settings/tokens."
        elif code == "404":
            hint = " The model in HF_MODEL doesn't exist on the API; try HF_MODEL=bigscience/bloom-560m or gpt2."
        return f"⚠️ Error (code={code}): {result.get('error')} {hint} {detail}"

    if isinstance(result, dict) and "text" in result:
        return result["text"]

    # Fallback
    return str(result)
