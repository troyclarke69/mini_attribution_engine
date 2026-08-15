"""Lazy, cached loader for the trained ROAS model.

Loading this pickle is expensive (large file + scikit-learn/joblib import
overhead). It used to run twice at process *import* time - once in
api/main.py and once in api/routers/ml_roas.py - which blocked uvicorn from
even opening its listening socket until both finished. That's what caused
the ~25s window on cold start where Fly's proxy got "connection refused".

Both call sites now import get_model() from here instead of loading the
pickle themselves, and the cost is only paid once, on the first request
that actually needs a prediction.
"""
from __future__ import annotations

import functools
import os

import joblib

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model_roas.pkl")


@functools.lru_cache(maxsize=1)
def get_model():
    model = joblib.load(MODEL_PATH)
    print(f"Loaded ROAS model from {MODEL_PATH}")
    return model
