"""FastAPI application entrypoint."""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers.health import router as health_router
from api.routers.metrics import raw_router, router as metrics_router
from api.routers.ml_roas import router as ml_roas_router
from etl.bq import get_bq_client
import joblib
from ml.data_loader import get_latest_feature_row

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="Mini Marketing Attribution Engine", version="1.0.0")

model = joblib.load("ml/model_roas.pkl")

print("MODEL FEATURES:", model.feature_names_in_)

# MUST BE IN SYNC WITH model.feature_names_in_ (otherwise, the model will throw an error)
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

try:
    bq_client = get_bq_client()
except Exception:
    bq_client = None

# Existing routers
app.include_router(metrics_router)
app.include_router(raw_router)
app.include_router(health_router)
app.include_router(ml_roas_router)

@app.get("/")
def root() -> dict[str, str]:
    """Return a small service descriptor."""
    return {"service": "mini-attribution-engine", "status": "running"}

@app.get("/predict_next_day_roas")
def predict_next_day_roas():
    df = get_latest_feature_row()

    # Drop non-feature columns
    X = df.drop(columns=["metric_date", "target_next_day_roas"])

    # Enforce correct column order
    X = X[FEATURE_ORDER]

    pred = model.predict(X)[0]

    return {"predicted_next_day_roas": float(pred)}
