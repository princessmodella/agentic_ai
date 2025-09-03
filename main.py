from project_a_deep_research.fetch_with_retry import fetch_url

if __name__ == "__main__":
    url = "https://www.example.com"
    try:
        html = fetch_url(url)
        print("✅ Successfully fetched page")
        print("Page length:", len(html))
    except Exception as e:
        print("❌ Failed to fetch:", e)
