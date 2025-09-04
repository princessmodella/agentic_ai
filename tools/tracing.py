# tools/tracing.py
import os
import json
import time
import uuid
import traceback
from typing import Any, Dict, Optional

TRACE_DIR = "traces"  # Default folder for saving spans

def start_span(name: str, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Start a new tracing span.

    Args:
        name: Name of the span (e.g., 'query', 'indexing').
        meta: Optional dictionary of extra metadata.

    Returns:
        span (dict): A dictionary representing the span.
    """
    return {
        "trace_id": str(uuid.uuid4()),
        "span_id": str(uuid.uuid4()),
        "name": name,
        "start_ts": time.time(),
        "meta": meta or {}
    }

def end_span(
    span: Dict[str, Any],
    status: str = "ok",
    output: Optional[Any] = None,
    error: Optional[BaseException] = None
) -> str:
    """
    End a tracing span, record duration, and save to file.

    Args:
        span: The span dictionary returned by start_span().
        status: Status string, defaults to "ok".
        output: Optional output summary to attach.
        error: Optional exception object.

    Returns:
        str: Path to the saved trace JSON file.
    """
    end_time = time.time()
    span.update({
        "end_ts": end_time,
        "duration_s": round(end_time - span["start_ts"], 4),  # rounded for clarity
        "status": status,
    })

    if output is not None:
        # Save only first 800 chars so file doesn’t explode
        span["output_summary"] = str(output)[:800]

    if error is not None:
        span["error"] = {
            "type": type(error).__name__,
            "message": str(error),
            "traceback": traceback.format_exc(limit=3)  # short traceback
        }

    # Save span JSON
    os.makedirs(TRACE_DIR, exist_ok=True)
    path = os.path.join(TRACE_DIR, f"{span['span_id']}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(span, f, indent=2)

    return path
