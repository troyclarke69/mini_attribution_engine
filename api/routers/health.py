"""Data freshness health endpoint."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from google.cloud import bigquery

from api.models.campaign_metrics import HealthStatus
from etl.bq import DATASET_ID, PROJECT_ID, get_bq_client

LOGGER = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


@router.get("/health", response_model=list[HealthStatus])
def get_health() -> list[HealthStatus]:
    """Return the latest status row for each ingestion source."""
    query = f"""
    SELECT source, CAST(latest_timestamp AS STRING) AS latest_timestamp, status
    FROM `{PROJECT_ID}.{DATASET_ID}.data_health`
    QUALIFY ROW_NUMBER() OVER (PARTITION BY source ORDER BY latest_timestamp DESC) = 1
    ORDER BY source
    """
    try:
        rows = get_bq_client().query(query).result()
        return [HealthStatus(**dict(row)) for row in rows]
    except Exception as exc:
        LOGGER.exception("Could not query data health")
        raise HTTPException(status_code=503, detail="Health data is temporarily unavailable") from exc
