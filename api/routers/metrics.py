"""Campaign metrics endpoints."""

from __future__ import annotations

import logging
from datetime import date

from fastapi import APIRouter, HTTPException
from google.cloud import bigquery

from api.models.campaign_metrics import CampaignMetric, SummaryMetrics
from etl.bq import DATASET_ID, PROJECT_ID, get_bq_client

LOGGER = logging.getLogger(__name__)
router = APIRouter(prefix="/metrics", tags=["metrics"])


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
