from __future__ import annotations

import logging
from datetime import date
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from google.cloud import bigquery

from api.models.anomaly import AnomalyAlert, AnomalyPoint
from etl.bq import DATASET_ID, PROJECT_ID, get_bq_client

LOGGER = logging.getLogger(__name__)
router = APIRouter(prefix="/anomalies", tags=["anomalies"])


def _serialize_row(row: bigquery.table.Row) -> dict[str, Any]:
    return {key: (value.isoformat() if hasattr(value, "isoformat") else value) for key, value in dict(row).items()}


def _query_metric_series(metric: str, campaign_id: str | None, date_from: date | None, date_to: date | None) -> list[dict[str, Any]]:
    clauses: list[str] = []
    params: list[bigquery.ScalarQueryParameter] = []
    if campaign_id:
        clauses.append("campaign_id = @campaign_id")
        params.append(bigquery.ScalarQueryParameter("campaign_id", "STRING", campaign_id))
    if date_from:
        clauses.append("metric_date >= CAST(@date_from AS DATE)")
        params.append(bigquery.ScalarQueryParameter("date_from", "STRING", date_from.isoformat()))
    if date_to:
        clauses.append("metric_date <= CAST(@date_to AS DATE)")
        params.append(bigquery.ScalarQueryParameter("date_to", "STRING", date_to.isoformat()))

    where_sql = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    query = f"""
    SELECT CAST(metric_date AS STRING) AS date, {metric}
    FROM `{PROJECT_ID}.{DATASET_ID}.fact_campaign_metrics`
    {where_sql}
    ORDER BY metric_date ASC
    """
    try:
        rows = get_bq_client().query(query, job_config=bigquery.QueryJobConfig(query_parameters=params)).result()
        return [_serialize_row(row) for row in rows]
    except Exception as exc:
        LOGGER.exception("Could not query anomaly series for %s", metric)
        raise HTTPException(status_code=503, detail="Anomaly series temporarily unavailable") from exc


def _detect_anomalies(series: list[dict[str, Any]], field: str) -> list[AnomalyAlert]:
    values = [float(item[field]) for item in series if item.get(field) is not None]
    if len(values) < 2:
        return []

    mean = sum(values) / len(values)
    stddev = (sum((x - mean) ** 2 for x in values) / len(values)) ** 0.5
    median = sorted(values)[len(values) // 2]
    deviations = [abs(x - median) for x in values]
    mad = sum(deviations) / len(deviations) if deviations else 0

    lower_iqr = sorted(values)[max(0, len(values) // 4)]
    upper_iqr = sorted(values)[min(len(values) - 1, 3 * len(values) // 4)]
    iqr = upper_iqr - lower_iqr

    alerts: list[AnomalyAlert] = []
    for item in series:
        value = float(item[field])
        z_score = (value - mean) / stddev if stddev else 0
        modified_z = 0 if mad == 0 else 0.6745 * (value - median) / mad
        iqr_outlier = value < lower_iqr - 1.5 * iqr or value > upper_iqr + 1.5 * iqr
        percent_change = 0.0
        if alerts:
            prev = float(alerts[-1].value)
            percent_change = (value - prev) / prev if prev else 0.0
        severity = "low"
        if abs(z_score) >= 3 or abs(modified_z) >= 3 or iqr_outlier or abs(percent_change) >= 0.25:
            severity = "high"
        elif abs(z_score) >= 2 or abs(modified_z) >= 2 or abs(percent_change) >= 0.15:
            severity = "medium"

        alerts.append(
            AnomalyAlert(
                date=item["date"],
                metric=field,
                value=value,
                z_score=z_score,
                modified_z_score=modified_z,
                iqr_outlier=iqr_outlier,
                percent_change=percent_change,
                severity=severity,
            )
        )
    return alerts


def _build_response(metric: str, campaign_id: str | None, date_from: date | None, date_to: date | None) -> list[AnomalyAlert]:
    series = _query_metric_series(metric, campaign_id, date_from, date_to)
    return _detect_anomalies(series, metric)


@router.get("/roas", response_model=list[AnomalyAlert])
def anomalies_roas(
    campaign_id: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
) -> list[AnomalyAlert]:
    return _build_response("roas", campaign_id, date_from, date_to)


@router.get("/cac", response_model=list[AnomalyAlert])
def anomalies_cac(
    campaign_id: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
) -> list[AnomalyAlert]:
    return _build_response("cac", campaign_id, date_from, date_to)
