"""Last-touch attribution processing and campaign metrics."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any

from dotenv import load_dotenv

from etl.bq import DATASET_ID, PROJECT_ID, get_bq_client, update_freshness, write_attribution, write_campaign_metrics

load_dotenv()
LOGGER = logging.getLogger(__name__)

def run_last_touch_attribution() -> list[dict[str, Any]]:
    """Attribute each order to its latest customer event within seven days."""
    client = get_bq_client()

    query = f"""
    WITH ranked_events AS (
      SELECT
          o.order_id,
          o.customer_id,
          o.order_ts,
          o.revenue,
          e.campaign_id,
          e.event_ts,
          ROW_NUMBER() OVER (
              PARTITION BY o.order_id
              ORDER BY e.event_ts DESC
          ) AS rank
      FROM `{PROJECT_ID}.{DATASET_ID}.fact_orders` o
      LEFT JOIN `{PROJECT_ID}.{DATASET_ID}.fact_events` e
        ON o.customer_id = e.customer_id
       AND e.event_ts BETWEEN TIMESTAMP_SUB(o.order_ts, INTERVAL 7 DAY)
                          AND o.order_ts
    )
    SELECT
        order_id,
        customer_id,
        campaign_id,
        event_ts AS touch_ts,
        revenue,
        CURRENT_TIMESTAMP() AS inserted_at
    FROM ranked_events
    WHERE rank = 1
    """

    results = []
    for row in client.query(query).result():
        d = dict(row)

        # Convert datetime/date fields to ISO strings for JSON serialization
        for key, value in d.items():
            if hasattr(value, "isoformat"):
                d[key] = value.isoformat()

        results.append(d)

    return results

def compute_summary_metrics(attribution_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Compute spend, revenue, ROAS, and CAC by campaign from BigQuery."""
    client = get_bq_client()

    query = f"""
    SELECT
        ad.campaign_id,
        ad.date AS metric_date,
        ad.spend,
        COALESCE(SUM(attr.revenue), 0) AS attributed_revenue,
        SAFE_DIVIDE(COALESCE(SUM(attr.revenue), 0), ad.spend) AS roas,
        SAFE_DIVIDE(ad.spend, COUNT(DISTINCT attr.order_id)) AS cac,
        COUNT(DISTINCT attr.order_id) AS conversions,
        CURRENT_TIMESTAMP() AS inserted_at
    FROM `{PROJECT_ID}.{DATASET_ID}.fact_ad_spend` ad
    LEFT JOIN `{PROJECT_ID}.{DATASET_ID}.fact_attribution` attr
        ON ad.campaign_id = attr.campaign_id
        AND ad.date = DATE(attr.touch_ts)
    GROUP BY ad.campaign_id, ad.date, ad.spend
    """

    results = []
    for row in client.query(query).result():
        d = dict(row)

        # Convert datetime/date fields to ISO strings for JSON serialization
        for key, value in d.items():
            if hasattr(value, "isoformat"):
                d[key] = value.isoformat()

        results.append(d)

    return results

def write_attribution_results() -> None:
    """Run attribution, persist its results, and refresh attribution status."""
    rows = run_last_touch_attribution()
    write_attribution(rows)
    metrics = compute_summary_metrics(rows)
    write_campaign_metrics(metrics)
    update_freshness("attribution", datetime.now(timezone.utc))
    LOGGER.info("Wrote %d attribution rows and %d campaign metrics", len(rows), len(metrics))
