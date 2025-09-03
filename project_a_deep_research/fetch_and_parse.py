# project_a_deep_research/fetch_and_parse.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import os
import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv
import openai
from tools.tracing import start_span, end_span

# --- Load OpenAI API key ---
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- Retry settings for fetching ---
@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def fetch_url(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()  # raise error for bad status
    return response.text

# --- Main processing function ---
def process_url(url):
    span = start_span("fetch_and_parse", {"url": url})
    try:
        html = fetch_url(url)
        soup = BeautifulSoup(html, "lxml")

        # Extract structured info
        title = soup.find("title").get_text() if soup.find("title") else "No title"
        headings = [h.get_text() for h in soup.find_all(["h1", "h2"])]
        links = [a["href"] for a in soup.find_all("a", href=True)]

        # Optional: summarize page using OpenAI
        summary = ""
        if openai.api_key:
            prompt = f"Summarize the following page:\nTitle: {title}\nHeadings: {headings}\nLinks: {links[:10]}\n"
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
            "summary": summary
        }

        path = end_span(span, status="ok", output=output)
        print(f"Processed {url}. Trace saved at {path}")
        return output

    except Exception as e:
        path = end_span(span, status="error", error=e)
        print(f"Error processing {url}. Trace saved at {path}")
        return None

# --- Entry point ---
if __name__ == "__main__":
    urls = [
        "https://example.com",  # replace with any URLs you want to test
    ]
    for url in urls:
        result = process_url(url)
        print(result)
