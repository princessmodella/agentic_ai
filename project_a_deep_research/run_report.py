# run_report.py
import sys
from project_a_deep_research.rag_quick import top_k_retrieve, write_report
from tools.tracing import start_span, end_span


def main(query: str):
    """Main entry: run retrieval + report writing with tracing."""
    root_span = start_span("run_report", {"query": query})
    try:
        # Step 1: Retrieval
        retrieval_span = start_span("retrieval", {"query": query})
        hits = top_k_retrieve(query, k=3)
        end_span(retrieval_span, status="ok", output={"hits": len(hits)})

        # Step 2: Report Writing
        report_span = start_span("report", {"query": query, "n_hits": len(hits)})
        path = write_report(query, hits)
        end_span(report_span, status="ok", output={"report_path": path})

        # Wrap up
        end_span(root_span, status="ok", output={"report": path})
        print(f"\n✅ Report generated: {path}")
        print("Check the 'reports/' folder for your markdown file.\n")

    except Exception as e:
        end_span(root_span, status="error", error=e)
        print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_report.py 'your research question'")
    else:
        main(sys.argv[1])
