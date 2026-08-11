"""Campaign metrics and drill-down endpoints."""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from google.cloud import bigquery

from api.models.campaign_metrics import CampaignMetric, SummaryMetrics
from etl.bq import DATASET_ID, PROJECT_ID, get_bq_client

LOGGER = logging.getLogger(__name__)
router = APIRouter(prefix="/metrics", tags=["metrics"])
raw_router = APIRouter(prefix="/raw", tags=["raw"])


def _as_iso(value: Any) -> Any:
    """Convert BigQuery value objects to JSON-serializable strings."""
    if value is None:
        return None
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def _serialize_row(row: bigquery.table.Row) -> dict[str, Any]:
    """Convert a BigQuery row into a plain dictionary."""
    return {key: _as_iso(value) for key, value in dict(row).items()}


def _row_to_metric(row: bigquery.table.Row) -> CampaignMetric:
    """Convert a BigQuery row to a validated metric model."""
    return CampaignMetric(
        campaign_id=str(row["campaign_id"]),
        metric_date=row["metric_date"],
        spend=float(row["spend"] or 0),
        attributed_revenue=float(row["attributed_revenue"] or 0),
        roas=float(row["roas"] or 0),
        cac=float(row["cac"] or 0),
        conversions=int(row["conversions"] or 0),
    )


def _query_metrics(campaign_id: str | None = None) -> list[CampaignMetric]:
    """Query the latest campaign metrics, optionally filtered by campaign."""
    query = f"""
    SELECT campaign_id, metric_date, spend, attributed_revenue, roas, cac, conversions
    FROM `{PROJECT_ID}.{DATASET_ID}.fact_campaign_metrics`
    WHERE (@campaign_id IS NULL OR campaign_id = @campaign_id)
    QUALIFY ROW_NUMBER() OVER (PARTITION BY campaign_id ORDER BY metric_date DESC) = 1
    ORDER BY attributed_revenue DESC
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("campaign_id", "STRING", campaign_id)]
    )
    return [_row_to_metric(row) for row in get_bq_client().query(query, job_config=job_config).result()]


def _build_date_filter(field_name: str, start: date | None, end: date | None) -> tuple[list[str], list[bigquery.ScalarQueryParameter]]:
    """Construct date-range query clauses with valid parameter handling."""
    clauses: list[str] = []
    params: list[bigquery.ScalarQueryParameter] = []
    if start is not None:
        clauses.append(f"{field_name} >= CAST(@date_from AS DATE)")
        params.append(bigquery.ScalarQueryParameter("date_from", "STRING", start.isoformat()))
    if end is not None:
        clauses.append(f"{field_name} <= CAST(@date_to AS DATE)")
        params.append(bigquery.ScalarQueryParameter("date_to", "STRING", end.isoformat()))
    return clauses, params


def _build_raw_response(
    table_name: str,
    select_columns: str,
    field_filters: dict[str, str | None],
    date_field: str,
    order_by: str,
    limit: int,
    offset: int,
    date_from: date | None,
    date_to: date | None,
) -> dict[str, Any]:
    """Execute a filtered, paginated raw-data query."""
    allowed_orders = {
        "date": "date",
        "spend": "spend",
        "order_ts": "order_ts",
        "revenue": "revenue",
        "event_ts": "event_ts",
        "touch_ts": "touch_ts",
        "order_date": "order_date",
        "event_date": "event_date",
    }
    if order_by not in allowed_orders:
        raise HTTPException(status_code=400, detail=f"Unsupported sort field: {order_by}")

    clauses: list[str] = []
    params: list[bigquery.ScalarQueryParameter] = []
    for key, value in field_filters.items():
        if value is None or value == "":
            continue
        clauses.append(f"{key} = @{key}")
        params.append(bigquery.ScalarQueryParameter(key, "STRING", str(value)))

    if date_from is not None or date_to is not None:
        if date_from is not None:
            clauses.append(f"{date_field} >= CAST(@date_from AS DATE)")
            params.append(bigquery.ScalarQueryParameter("date_from", "STRING", date_from.isoformat()))
        if date_to is not None:
            clauses.append(f"{date_field} <= CAST(@date_to AS DATE)")
            params.append(bigquery.ScalarQueryParameter("date_to", "STRING", date_to.isoformat()))

    where_sql = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    data_query = f"""
    SELECT {select_columns}
    FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
    {where_sql}
    ORDER BY {allowed_orders[order_by]} DESC
    LIMIT @limit OFFSET @offset
    """
    count_query = f"""
    SELECT COUNT(*) AS total_count
    FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
    {where_sql}
    """
    params.extend([
        bigquery.ScalarQueryParameter("limit", "INT64", limit),
        bigquery.ScalarQueryParameter("offset", "INT64", offset),
    ])
    total_rows = get_bq_client().query(count_query, job_config=bigquery.QueryJobConfig(query_parameters=params)).result()
    total_count = sum(int(row["total_count"]) for row in total_rows)
    rows = get_bq_client().query(data_query, job_config=bigquery.QueryJobConfig(query_parameters=params)).result()
    return {"rows": [_serialize_row(row) for row in rows], "count": total_count}


@router.get("/summary", response_model=SummaryMetrics)
def get_summary() -> SummaryMetrics:
    """Return aggregate spend, revenue, ROAS, CAC, and campaign rows."""
    try:
        campaigns = _query_metrics()
    except Exception as exc:
        LOGGER.exception("Could not query campaign summary")
        raise HTTPException(status_code=503, detail="Metrics are temporarily unavailable") from exc
    spend = sum(row.spend for row in campaigns)
    revenue = sum(row.attributed_revenue for row in campaigns)
    conversions = sum(row.conversions for row in campaigns)
    return SummaryMetrics(
        spend=spend,
        attributed_revenue=revenue,
        roas=revenue / spend if spend else 0,
        cac=spend / conversions if conversions else 0,
        conversions=conversions,
        campaigns=campaigns,
    )


@router.get("/campaign/{id}", response_model=CampaignMetric)
def get_campaign(id: str) -> CampaignMetric:
    """Return the latest metric row for a campaign."""
    try:
        rows = _query_metrics(id)
    except Exception as exc:
        LOGGER.exception("Could not query campaign %s", id)
        raise HTTPException(status_code=503, detail="Metrics are temporarily unavailable") from exc
    if not rows:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return rows[0]


def _query_trend(metric_column: str, label: str, campaign_id: str | None, date_from: date | None, date_to: date | None) -> list[dict[str, Any]]:
    """Return a date-indexed metric trend using campaign filters."""
    clauses: list[str] = []
    params: list[bigquery.ScalarQueryParameter] = []
    if campaign_id is not None:
        clauses.append("campaign_id = @campaign_id")
        params.append(bigquery.ScalarQueryParameter("campaign_id", "STRING", campaign_id))
    if date_from is not None:
        clauses.append("metric_date >= CAST(@date_from AS DATE)")
        params.append(bigquery.ScalarQueryParameter("date_from", "STRING", date_from.isoformat()))
    if date_to is not None:
        clauses.append("metric_date <= CAST(@date_to AS DATE)")
        params.append(bigquery.ScalarQueryParameter("date_to", "STRING", date_to.isoformat()))

    where_sql = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    query = f"""
    SELECT CAST(metric_date AS STRING) AS date, {metric_column} AS {label}
    FROM `{PROJECT_ID}.{DATASET_ID}.fact_campaign_metrics`
    {where_sql}
    ORDER BY metric_date ASC
    """
    try:
        rows = get_bq_client().query(query, job_config=bigquery.QueryJobConfig(query_parameters=params)).result()
        return [_serialize_row(row) for row in rows]
    except Exception as exc:
        LOGGER.exception("Could not query %s trend", label)
        raise HTTPException(status_code=503, detail=f"{label} trend is temporarily unavailable") from exc


@router.get("/trend/roas")
def get_roas_trend(
    campaign_id: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
) -> list[dict[str, Any]]:
    """Return daily ROAS values."""
    return _query_trend("roas", "roas", campaign_id, date_from, date_to)


@router.get("/trend/cac")
def get_cac_trend(
    campaign_id: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
) -> list[dict[str, Any]]:
    """Return daily CAC values."""
    return _query_trend("cac", "cac", campaign_id, date_from, date_to)


@router.get("/trend/conversions")
def get_conversion_trend(
    campaign_id: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
) -> list[dict[str, Any]]:
    """Return daily conversion counts."""
    return _query_trend("conversions", "conversions", campaign_id, date_from, date_to)


@router.get("/trend/spend-revenue")
def get_spend_revenue_trend(
    campaign_id: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
) -> list[dict[str, Any]]:
    """Return daily spend and attributed revenue values."""
    return _query_trend("spend, attributed_revenue", "spend", campaign_id, date_from, date_to)


@raw_router.get("/ad-spend")
def get_raw_ad_spend(
    campaign_id: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    limit: int = Query(default=25, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    order_by: str = Query(default="date"),
) -> dict[str, Any]:
    """Return ad spend rows with pagination."""
    return _build_raw_response(
        "fact_ad_spend",
        "campaign_id, date, spend, impressions, clicks, source, inserted_at",
        {"campaign_id": campaign_id},
        "date",
        order_by,
        limit,
        offset,
        date_from,
        date_to,
    )


@raw_router.get("/orders")
def get_raw_orders(
    customer_id: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    limit: int = Query(default=25, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    order_by: str = Query(default="order_date"),
) -> dict[str, Any]:
    """Return order rows with pagination."""
    return _build_raw_response(
        "fact_orders",
        "order_id, customer_id, order_ts, order_date, revenue, currency, inserted_at",
        {"customer_id": customer_id},
        "order_date",
        order_by,
        limit,
        offset,
        date_from,
        date_to,
    )


@raw_router.get("/events")
def get_raw_events(
    campaign_id: str | None = Query(default=None),
    customer_id: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    limit: int = Query(default=25, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    order_by: str = Query(default="event_ts"),
) -> dict[str, Any]:
    """Return event rows with pagination."""
    return _build_raw_response(
        "fact_events",
        "event_id, customer_id, event_ts, event_date, event_type, campaign_id, source, inserted_at",
        {"campaign_id": campaign_id, "customer_id": customer_id},
        "event_date",
        order_by,
        limit,
        offset,
        date_from,
        date_to,
    )


@raw_router.get("/attribution")
def get_raw_attribution(
    campaign_id: str | None = Query(default=None),
    touch_date_from: date | None = Query(default=None),
    touch_date_to: date | None = Query(default=None),
    limit: int = Query(default=25, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    order_by: str = Query(default="touch_ts"),
) -> dict[str, Any]:
    """Return attribution rows with pagination."""
    return _build_raw_response(
        "fact_attribution",
        "order_id, customer_id, campaign_id, touch_ts, revenue, inserted_at",
        {"campaign_id": campaign_id},
        "DATE(touch_ts)",
        order_by,
        limit,
        offset,
        touch_date_from,
        touch_date_to,
    )
