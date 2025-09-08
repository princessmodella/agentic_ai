import requests
from bs4 import BeautifulSoup

def fetch_url(url: str) -> str:
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        return ""
    soup = BeautifulSoup(response.text, "html.parser")
    # Remove scripts/styles
    for script in soup(["script", "style"]):
        script.decompose()
    return soup.get_text(separator=" ", strip=True)
