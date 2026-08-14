"""FastAPI entrypoint."""
import logging
import base64
import os

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
import joblib
from ml.data_loader import get_latest_feature_row

# --- App setup ---
logging.basicConfig(level=logging.INFO)
app = FastAPI(title="Mini Marketing Attribution Engine", version="1.0.0")

# --- Load model ---
model = joblib.load("ml/model_roas.pkl")
print("MODEL FEATURES:", model.feature_names_in_)

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

# --- BigQuery client ---
try:
    bq_client = get_bq_client()
except Exception:
    bq_client = None

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
    df = get_latest_feature_row()

    X = df.drop(columns=["metric_date", "target_next_day_roas"])
    X = X[FEATURE_ORDER]

    pred = model.predict(X)[0]
    return {"predicted_next_day_roas": float(pred)}
