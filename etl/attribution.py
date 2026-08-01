"""Last-touch attribution processing and campaign metrics."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any

from dotenv import load_dotenv
from google.cloud import bigquery

from etl.bq import DATASET_ID, PROJECT_ID, update_freshness, write_attribution, write_campaign_metrics

load_dotenv()
LOGGER = logging.getLogger(__name__)


def run_last_touch_attribution() -> list[dict[str, Any]]:
    """Attribute each order to its latest customer event within seven days."""
    client = bigquery.Client(project=PROJECT_ID)
    query = f"""
    WITH ranked_events AS (
      SELECT o.order_id, o.customer_id, o.order_ts, o.revenue, e.campaign_id,
             e.event_ts,
             ROW_NUMBER() OVER (PARTITION BY o.order_id ORDER BY e.event_ts DESC) AS rank
      FROM `{PROJECT_ID}.{DATASET_ID}.fact_orders` o
      LEFT JOIN `{PROJECT_ID}.{DATASET_ID}.fact_events` e
        ON o.customer_id = e.customer_id
       AND e.event_ts BETWEEN TIMESTAMP_SUB(o.order_ts, INTERVAL 7 DAY) AND o.order_ts
    )
    SELECT order_id, customer_id, campaign_id, event_ts AS touch_ts, revenue,
           CURRENT_TIMESTAMP() AS inserted_at
    FROM ranked_events
    WHERE rank = 1
    """
    return [dict(row) for row in client.query(query).result()]


def compute_summary_metrics(attribution_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Compute spend, revenue, ROAS, and CAC by campaign from BigQuery."""
    client = bigquery.Client(project=PROJECT_ID)
    query = f"""
    SELECT spend.campaign_id, CURRENT_DATE() AS metric_date,
           spend.spend, COALESCE(SUM(attr.revenue), 0) AS attributed_revenue,
           SAFE_DIVIDE(COALESCE(SUM(attr.revenue), 0), spend.spend) AS roas,
           SAFE_DIVIDE(spend.spend, COUNT(DISTINCT attr.order_id)) AS cac,
           COUNT(DISTINCT attr.order_id) AS conversions,
           CURRENT_TIMESTAMP() AS inserted_at
    FROM `{PROJECT_ID}.{DATASET_ID}.fact_ad_spend` spend
    LEFT JOIN `{PROJECT_ID}.{DATASET_ID}.fact_attribution` attr
      ON spend.campaign_id = attr.campaign_id AND spend.date = DATE(attr.touch_ts)
    GROUP BY spend.campaign_id, spend.spend
    """
    return [dict(row) for row in client.query(query).result()]


def write_attribution_results() -> None:
    """Run attribution, persist its results, and refresh attribution status."""
    rows = run_last_touch_attribution()
    write_attribution(rows)
    metrics = compute_summary_metrics(rows)
    write_campaign_metrics(metrics)
    update_freshness("attribution", datetime.now(timezone.utc))
    LOGGER.info("Wrote %d attribution rows and %d campaign metrics", len(rows), len(metrics))
