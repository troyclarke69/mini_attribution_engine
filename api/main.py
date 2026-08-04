"""FastAPI application entrypoint."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers.health import router as health_router
from api.routers.metrics import router as metrics_router
from etl.bq import get_bq_client

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="Mini Marketing Attribution Engine", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

try:
    bq_client = get_bq_client()
except Exception:
    bq_client = None

app.include_router(metrics_router)
app.include_router(health_router)


@app.get("/")
def root() -> dict[str, str]:
    """Return a small service descriptor."""
    return {"service": "mini-attribution-engine", "status": "running"}
