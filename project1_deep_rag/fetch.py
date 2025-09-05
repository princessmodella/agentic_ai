import requests
from bs4 import BeautifulSoup

def fetch_url(url: str):
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        return soup.get_text()
    except:
        return ""

def fetch_web(query: str):
    # Simple placeholder: in real, integrate search API
    return f"Fetched content for '{query}'"
