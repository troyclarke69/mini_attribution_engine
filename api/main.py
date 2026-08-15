"""FastAPI entrypoint."""
import asyncio
import logging
import base64
import os
from contextlib import asynccontextmanager

# --- GCP Credentials (Fly + local Docker Compose) ---
creds_b64 = os.getenv("GCP_CREDS")
if creds_b64:
    creds_json = base64.b64decode(creds_b64).decode("utf-8")
    os.makedirs("/app/gcp", exist_ok=True)
    with open("/app/gcp/service-account.json", "w") as f:
        f.write(creds_json)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/app/gcp/service-account.json"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers.health import router as health_router
from api.routers.metrics import raw_router, router as metrics_router
from api.routers.ml_roas import router as ml_roas_router
from api.routers.anomalies import router as anomalies_router

from etl.bq import get_bq_client
from ml.data_loader import get_latest_feature_row_for_prediction
from ml.model_store import get_model

# --- App setup ---
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Kick off the expensive first-use work (loading the 20MB model pickle,
    # constructing the BigQuery client) in background threads as soon as
    # uvicorn has opened its listening socket, instead of leaving it to
    # whichever unlucky request happens to be first. This runs *after* the
    # socket is bound (so Fly's cold-start reachability check still passes
    # immediately) but *before* most real traffic arrives, so the first
    # /predict_next_day_roas call after a cold start doesn't have to pay
    # ~5-10s of joblib/BigQuery setup cost inline and risk timing out.
    async def _warm_up():
        try:
            await asyncio.to_thread(get_model)
            await asyncio.to_thread(get_bq_client)
            LOGGER.info("Warm-up complete: model and BigQuery client are ready")
        except Exception:
            LOGGER.exception("Warm-up failed; will fall back to lazy load on first request")

    asyncio.create_task(_warm_up())
    yield


app = FastAPI(title="Mini Marketing Attribution Engine", version="1.0.0", lifespan=lifespan)

FEATURE_ORDER = [
    "spend",
    "attributed_revenue",
    "conversions",
    "cac",
    "roas",
    "rolling_7d_roas",
    "rolling_7d_spend",
    "rolling_7d_conversions",
    "rolling_7d_volatility",
]

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# --- Routers ---
app.include_router(metrics_router)
app.include_router(raw_router)
app.include_router(health_router)
app.include_router(ml_roas_router)
app.include_router(anomalies_router)

# --- Root ---
@app.get("/")
def root() -> dict[str, str]:
    return {"service": "mini-attribution-engine", "status": "running"}

# --- Prediction endpoint ---
@app.get("/predict_next_day_roas")
def predict_next_day_roas():
    model = get_model()

    df = get_latest_feature_row_for_prediction()
    X = df[FEATURE_ORDER]

    pred = model.predict(X)[0]
    return {"predicted_next_day_roas": float(pred)}
