# rag_query.py
from llm_client import query_hf

def query_rag(question: str):
    prompt = f"Answer the following question in detail:\n\n{question}\n\n"
    result = query_hf(prompt)

    # If result is an error dict from llm_client, convert to user-friendly text
    if isinstance(result, dict) and "error" in result:
        code = result.get("code", "UNKNOWN")
        message = result.get("error", result.get("detail", "Unknown error"))
        # Extra hint for common issues
        hint = ""
        if code == "NO_TOKEN":
            hint = " Make sure HF_API_TOKEN is set inside .env at project root and restart Streamlit."
        elif code == "401":
            hint = " Your token may be invalid. Recreate token at https://huggingface.co/settings/tokens and update .env."
        elif code == "NO_MODEL":
            hint = " The model you requested and fallbacks were not found; set HF_MODEL in .env to a valid model."
        return f"⚠️ Error (code={code}): {message}{hint}"

    # Success path: result should be a dict with 'text'
    if isinstance(result, dict) and "text" in result:
        return result["text"]

    # If something else came back, stringify it
    return str(result)
