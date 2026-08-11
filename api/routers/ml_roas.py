from fastapi import APIRouter
from pydantic import BaseModel
import joblib
import os
import numpy as np

# ---------------------------------------------------------
# Load model once at startup
# ---------------------------------------------------------

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "ml", "model_roas.pkl")

try:
    model = joblib.load(MODEL_PATH)
    print(f"Loaded ROAS model from {MODEL_PATH}")
except Exception as e:
    print(f"Failed to load ROAS model: {e}")
    model = None


# ---------------------------------------------------------
# Request schema
# ---------------------------------------------------------

class ROASPredictionRequest(BaseModel):
    spend: float
    attributed_revenue: float
    conversions: int
    cac: float
    roas: float
    events_count: int
    rolling_7d_roas: float
    rolling_7d_spend: float
    rolling_7d_conversions: float
    rolling_7d_volatility: float


# ---------------------------------------------------------
# Response schema
# ---------------------------------------------------------

class ROASPredictionResponse(BaseModel):
    predicted_next_day_roas: float


# ---------------------------------------------------------
# Router
# ---------------------------------------------------------

router = APIRouter(prefix="/ml", tags=["ml"])


@router.post("/predict/roas", response_model=ROASPredictionResponse)
def predict_roas(payload: ROASPredictionRequest):
    """
    Predict next-day ROAS using the trained RandomForest model.
    """

    if model is None:
        return ROASPredictionResponse(predicted_next_day_roas=-1.0)

    # Convert request to model input
    features = np.array([
        payload.spend,
        payload.attributed_revenue,
        payload.conversions,
        payload.cac,
        payload.roas,
        payload.events_count,
        payload.rolling_7d_roas,
        payload.rolling_7d_spend,
        payload.rolling_7d_conversions,
        payload.rolling_7d_volatility,
    ]).reshape(1, -1)

    # Run prediction
    pred = model.predict(features)[0]

    return ROASPredictionResponse(predicted_next_day_roas=float(pred))
