from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from graphs.ceo_graph import ceo_graph
from state.state import HierarchicalState

ROOT = Path(__file__).parent
app = FastAPI(title="AI Product Launch Team")
app.mount("/static", StaticFiles(directory=ROOT), name="static")


def initial_state(request: str) -> HierarchicalState:
    return {
        "user_request": request,
        "current_agent": "CEO",
        "handoff_history": [],
        "marketing_directive": None,
        "finance_directive": None,
        "marketing_decomposition": None,
        "finance_decomposition": None,
        "research_output": None,
        "content_output": None,
        "marketing_report": None,
        "cost_output": None,
        "pricing_output": None,
        "finance_report": None,
        "final_response": None,
        "errors": [],
    }


def dump(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if isinstance(value, dict):
        return {key: dump(item) for key, item in value.items()}
    if isinstance(value, list):
        return [dump(item) for item in value]
    return value


def events(request: str) -> Iterator[str]:
    for event in ceo_graph.stream(initial_state(request), stream_mode="updates", subgraphs=True):
        if isinstance(event, tuple):
            namespace, update = event
            node = ".".join(namespace) or "CEO"
        else:
            update = event
            node = "CEO"
        yield f"data: {json.dumps({'node': node, 'state': dump(update)})}\n\n"
    yield "data: {\"node\":\"complete\"}\n\n"


@app.get("/")
def index() -> FileResponse:
    return FileResponse(ROOT / "index.html")


@app.get("/api/run")
def run(request: str = Query(min_length=1)) -> StreamingResponse:
    return StreamingResponse(events(request), media_type="text/event-stream")
