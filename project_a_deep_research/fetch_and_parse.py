# fetch_and_parse.py
import os
import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv
import openai
from tools.tracing import start_span, end_span

load_dotenv()
openai.api_key = os.getenv("OPENAI_sk-proj-y5Sh5Pe7w-b-pgar8j624gJ5y1lL-EOmGQIkl0YV0Y8l60Bg_spkABPaN_Gzf5YbYTg9xMvPpMT3BlbkFJZnSwJ6ua95VtzuvchyTgk6Q1N8hmOnIyY3Hoj8SPiJOCGRco97PjVK3Qjl-9ag12ZivZQrBOsA")

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def fetch_url(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.text

def process_url(url):
    span = start_span("fetch_and_parse", {"url": url})
    try:
        html = fetch_url(url)
        soup = BeautifulSoup(html, "lxml")

        title = soup.find("title").get_text() if soup.find("title") else "No title"
        headings = [h.get_text() for h in soup.find_all(["h1", "h2"])]
        links = [a["href"] for a in soup.find_all("a", href=True)]

        summary = ""
        if openai.api_key:
            prompt = f"Summarize page:\nTitle: {title}\nHeadings: {headings}\nLinks: {links[:10]}\n"
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt,
                max_tokens=150
            )
            summary = response.choices[0].text.strip()

        output = {
            "title": title,
            "headings": headings,
            "links": links,
            "summary": summary,
        }

        end_span(span, status="ok", output=output)
        return output
    except Exception as e:
        end_span(span, status="error", error=e)
        return None
