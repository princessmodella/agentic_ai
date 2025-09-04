from flask import Flask, render_template, request, send_file
from project_a_deep_research.fetch_and_parse import process_url
import os

app = Flask(__name__)

os.makedirs("reports", exist_ok=True)
os.makedirs("data/json", exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    url = ""
    error_msg = ""
    if request.method == "POST":
        url = request.form.get("url")
        if url:
            try:
            
                result = process_url(url)
            except Exception as e:
                error_msg = str(e)
    return render_template("index.html", result=result, url=url, error_msg=error_msg)

@app.route("/download/<report_name>")
def download(report_name):
    path = os.path.join("reports", report_name)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "Report not found.", 404

if __name__ == "__main__":
    app.run(debug=True)
