
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from tenacity import retry, stop_after_attempt, wait_exponential
from tools.tracing import start_span, end_span
import requests


@retry(
    stop=stop_after_attempt(3),   # Try up to 3 times total
    wait=wait_exponential(        
        multiplier=1,
        min=2,
        max=10
    )
)
def fetch_url(url: str):
    span = start_span("fetch_url", {"url": url})
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()

        end_span(
            span,
            status="ok",
            output={"status_code": r.status_code, "len": len(r.text)}
        )
        return r.text

    except Exception as e:
        end_span(span, status="error", error=e)
        raise

if __name__ == "__main__":
    url = "https://example.com"
    html = fetch_url(url)
    print(f"Fetched {len(html)} characters from {url}")
