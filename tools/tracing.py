import os, json , time , uuid


def start_span(name, meta=None):
    return {
        "trace_id": str(uuid.uuid4()),
        "span_id": str(uuid.uuid4()),
        "name": name,
        "start_ts": time.time(),
        "meta": meta or {}
    }

def end_span(span, status="ok", output=None, error=None):
    span.update({
        "end_ts": time.time(),
        "duration_s": time.time() - span["start_ts"],
        "status": status,
    })
    if output: span["output_summary"] = str(output)[:800]
    if error: span["error"] = {"type": type(error).__name__, "message": str(error)}

    os.makedirs("traces", exist_ok=True)
    path = f"traces/{span['span_id']}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(span, f, indent=2)
    return path
