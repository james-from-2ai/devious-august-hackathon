"""FastAPI entrypoint. You should not need to edit this file.

    POST /advise   the scored endpoint
    GET  /health   liveness, used by make submit before it spends an attempt

All the logic worth changing lives in handler.py.
"""

import os
import time

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.handler import advise
from app.models import AdviseRequest, AdviseResponse, HealthResponse

BLOCK = int(os.environ.get("BLOCK", "1"))
TEAM = os.environ.get("TEAM_NAME", "unnamed")

app = FastAPI(title="Agricultural Advisory Service", version="1.0.0")


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", block=BLOCK, team=TEAM)


@app.post("/advise", response_model=AdviseResponse)
async def advise_endpoint(request: AdviseRequest) -> AdviseResponse:
    return await advise(request)


@app.exception_handler(Exception)
async def unhandled(request, exc):
    """Never return a bare 500 with a stack trace.

    The scorer treats an unparseable response as SCHEMA_ERROR and scores 0.
    A shaped error response at least tells you what broke without costing
    you the rest of the run.
    """
    return JSONResponse(
        status_code=500,
        content={"error": type(exc).__name__, "detail": str(exc)[:500],
                 "ts": int(time.time())},
    )
