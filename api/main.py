"""FastAPI application entrypoint."""

import logging

from fastapi import FastAPI

from api.routers.health import router as health_router
from api.routers.metrics import router as metrics_router
from etl.bq import get_bq_client

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="Mini Marketing Attribution Engine", version="1.0.0")

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
