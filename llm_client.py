# llm_client.py
import os
import logging
import requests
from dotenv import load_dotenv, find_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load .env (prints path)
env_path = find_dotenv()
if env_path:
    load_dotenv(env_path)
    logger.info(".env loaded from: %s", env_path)
else:
    logger.warning(".env not found by find_dotenv()")

# Required ENV variables
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_MODEL = os.getenv("HF_MODEL")

# Hard fallback only if not set
if not HF_MODEL:
    HF_MODEL = "bigscience/bloom-560m"
    logger.warning("HF_MODEL not set in .env, defaulting to %s", HF_MODEL)

if HF_API_TOKEN:
    logger.info("HF_API_TOKEN loaded: %s...", HF_API_TOKEN[:8])
else:
    logger.warning("HF_API_TOKEN not set. Add HF_API_TOKEN to your .env at project root.")

# Hugging Face client availability
HAS_HF_CLIENT = False
try:
    from huggingface_hub.inference import InferenceClient
    HAS_HF_CLIENT = True
except ImportError:
    logger.info("huggingface_hub InferenceClient not available; will use REST only.")

def _parse_json_response(resp):
    """Helper to normalize Hugging Face REST responses into {text, raw}."""
    try:
        d = resp.json()
    except ValueError:
        return {"error": "Non-JSON response from HF", "raw": resp.text}

    if isinstance(d, list) and d and "generated_text" in d[0]:
        return {"text": d[0]["generated_text"], "raw": d}
    if isinstance(d, dict) and "generated_text" in d:
        return {"text": d["generated_text"], "raw": d}
    if isinstance(d, dict) and "error" in d:
        return {"error": d["error"], "raw": d}
    return {"text": str(d), "raw": d}

def query_hf(prompt: str, model: str | None = None, timeout: int = 30):
    """
    Query Hugging Face Inference API.
    Returns:
      - success: {"text": "...", "raw": <raw-json>}
      - failure: {"error": "...", "code": "...", "detail": "..."}
    """
    if not HF_API_TOKEN:
        return {"error": "Missing HF_API_TOKEN (set it in .env at project root).", "code": "NO_TOKEN"}

    model = model or HF_MODEL

    # ✅ Skip InferenceClient if using bloom (avoid StopIteration)
    if HAS_HF_CLIENT and "bloom" not in model.lower():
        try:
            client = InferenceClient(model=model, token=HF_API_TOKEN)
            resp = client.text_generation(prompt, max_new_tokens=200, do_sample=True, temperature=0.7)
            return {"text": resp if isinstance(resp, str) else str(resp), "raw": resp}
        except Exception as e:
            logger.exception("InferenceClient error - falling back to REST: %s", e)

    # REST fallback
    api_url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    try:
        resp = requests.post(api_url, headers=headers, json={"inputs": prompt}, timeout=timeout)
    except requests.exceptions.Timeout:
        return {"error": "Request timed out contacting Hugging Face.", "code": "TIMEOUT"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Network/request error: {e}", "code": "REQUEST_ERR"}

    if resp.status_code == 200:
        parsed = _parse_json_response(resp)
        return {"text": parsed.get("text", ""), "raw": parsed.get("raw")} if "error" not in parsed else {
            "error": parsed["error"], "code": "MODEL_ERROR", "detail": parsed.get("raw")
        }
    if resp.status_code == 401:
        return {"error": "Unauthorized (401). Token invalid or lacks permission.", "code": "401", "detail": resp.text}
    if resp.status_code == 404:
        return {"error": f"Model not found (404): {model}. Update HF_MODEL in .env.", "code": "404", "detail": resp.text}
    if resp.status_code == 429:
        return {"error": "Rate limited (429). Try again later or switch models.", "code": "429", "detail": resp.text}
    if 500 <= resp.status_code < 600:
        return {"error": f"Hugging Face server error {resp.status_code}.", "code": str(resp.status_code), "detail": resp.text}
    return {"error": f"Unexpected HTTP status {resp.status_code}", "code": str(resp.status_code), "detail": resp.text}

def test_models(models: list | None = None, test_prompt: str = "Hello"):
    """Quick check if multiple models are reachable."""
    if not HF_API_TOKEN:
        return [{"model": None, "ok": False, "error": "NO_TOKEN"}]
    models = models or [HF_MODEL]
    results = []
    for m in models:
        try:
            if HAS_HF_CLIENT and "bloom" not in m.lower():
                client = InferenceClient(model=m, token=HF_API_TOKEN)
                resp = client.text_generation(test_prompt, max_new_tokens=10)
                results.append({"model": m, "ok": True, "snippet": str(resp)[:300]})
            else:
                r = requests.post(f"https://api-inference.huggingface.co/models/{m}",
                                  headers={"Authorization": f"Bearer {HF_API_TOKEN}"},
                                  json={"inputs": test_prompt}, timeout=8)
                results.append({"model": m, "ok": r.ok, "status_code": r.status_code, "snippet": r.text[:300]})
        except Exception as e:
            results.append({"model": m, "ok": False, "error": str(e)})
    return results
