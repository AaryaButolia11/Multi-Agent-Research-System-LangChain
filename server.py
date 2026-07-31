"""
Self-contained FastAPI backend — the frontend HTML is embedded below, so the
root route never depends on a file on disk. No static/ folder needed.

    GET /               -> serves the embedded single-page app
    GET /research?topic -> Server-Sent Events stream of the graph running live

A MetricsCallback is attached per request, so the final "done" event carries
token / cost / latency figures for the run.

Run:
    uvicorn server:app --reload
    then open  http://127.0.0.1:8000
"""

import json

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse

from graph import graph, initial_state
from metrics import MetricsCallback

app = FastAPI(title="ResearchMind")


def sse(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"


@app.get("/")
async def index():
    return HTMLResponse(INDEX_HTML)


@app.get("/favicon.ico")
async def favicon():
    return HTMLResponse("", status_code=204)


@app.get("/research")
async def research(request: Request, topic: str, quality_bar: int = 8, max_revisions: int = 3):
    async def event_stream():
        state = initial_state(topic, quality_bar, max_revisions)
        cb = MetricsCallback()
        yield sse({"event": "start", "topic": topic, "quality_bar": quality_bar})

        final: dict = {}
        try:
            async for step in graph.astream(state, config={"callbacks": [cb]}):
                if await request.is_disconnected():
                    break
                for node, update in step.items():
                    final.update(update)
                    if node == "search":
                        yield sse({"event": "search", "count": len(update.get("urls", [])),
                                   "urls": update.get("urls", [])})
                    elif node == "read":
                        yield sse({"event": "read", "chars": len(update.get("sources", ""))})
                    elif node == "gap_search":
                        yield sse({"event": "gap",
                                   "queries": update.get("gap_queries", []),
                                   "new_urls": update.get("new_urls", []),
                                   "new_sources": update.get("new_source_count", 0)})
                    elif node == "write":
                        yield sse({"event": "write", "revision": update.get("revision"),
                                   "report": update.get("report", "")})
                    elif node == "critic":
                        yield sse({"event": "critic", "score": update.get("score"),
                                   "critique": update.get("critique"),
                                   "history": update.get("score_history", [])})
            yield sse({"event": "done",
                       "revisions": final.get("revision"),
                       "history": final.get("score_history", []),
                       "best_score": final.get("best_score"),
                       "report": final.get("best_report") or final.get("report", ""),
                       "critique": final.get("critique"),
                       "metrics": cb.summary()})
        except Exception as exc:
            yield sse({"event": "error", "message": str(exc)})

    return StreamingResponse(event_stream(), media_type="text/event-stream")
