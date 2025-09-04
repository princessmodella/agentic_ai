import os
import traceback
from flask import Flask, request, render_template
from urllib.parse import urlparse
import ipaddress
from pyngrok import ngrok

from project_a_deep_research.browse_and_index import index_url
from project_a_deep_research.rag_quick import top_k_retrieve, write_report
from tools.tracing import start_span, end_span

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

ALLOWED_SCHEMES = {"http", "https"}
DISALLOWED_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0"}

def validate_url(u: str):
    parsed = urlparse(u)
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise ValueError("URL scheme must be http/https")
    host = parsed.hostname
    if not host or host.lower() in DISALLOWED_HOSTS:
        raise ValueError("Local URLs not allowed")
    try:
        ip = ipaddress.ip_address(host)
        if ip.is_private or ip.is_loopback:
            raise ValueError("Private IP addresses not allowed")
    except ValueError:
        pass

@app.route("/", methods=["GET", "POST"])
def index():
    answer = None
    report_path = None
    error = None
    try:
        if request.method == "POST":
            mode = request.form.get("mode", "query")
            text = request.form.get("text", "").strip()
            extra_question = request.form.get("question", "").strip()
            
            if mode == "url":
                url = text
                validate_url(url)
                span = start_span("handle_url_submit", {"url": url})
                try:
                    info = index_url(url)
                    question = extra_question or f"Summarize {url}"
                    hits = top_k_retrieve(question)
                    if not hits:
                        hits = [(f"Indexed {info.get('indexed_chunks',0)} chunks from {url}", {"url": url})]
                    report_path = write_report(question, hits)
                    answer = {
                        "summary": "\n\n".join([f"{i+1}. {h[0][:300]}... ({h[1].get('url')})" for i, h in enumerate(hits)]),
                        "indexed": info.get("indexed_chunks", 0),
                    }
                    end_span(span, status="ok", output={"indexed": info.get("indexed_chunks", 0)})
                except Exception as e:
                    end_span(span, status="error", error=e)
                    raise
            else:
                query = text or extra_question
                hits = top_k_retrieve(query)
                report_path = write_report(query, hits)
                answer = {
                    "summary": "\n\n".join([f"{i+1}. {h[0][:300]}... ({h[1].get('url')})" for i, h in enumerate(hits)]),
                    "indexed": len(hits),
                }
    except Exception as e:
        error = str(e)
        tb = traceback.format_exc()
        span_e = start_span("server_error", {"error": error})
        end_span(span_e, status="error", output={"traceback": tb[:1000]})
    return render_template("index.html", answer=answer, report_path=report_path, error=error)

if __name__ == "__main__":
    public_url = ngrok.connect(5000).public_url
    print(f" * ngrok tunnel running -> {public_url}")
    app.run(host="127.0.0.1", port=5000, debug=True)
