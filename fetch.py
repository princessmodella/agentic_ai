# fetcher.py
import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
def fetch_text(url: str, timeout: int = 10) -> str:
    r = requests.get(url, timeout=timeout, headers={"User-Agent":"Mozilla/5.0 (compatible)"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    # get body text, fallback to whole page
    body = soup.body.get_text(separator="\n") if soup.body else soup.get_text(separator="\n")
    return body.strip()
