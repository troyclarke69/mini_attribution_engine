"""BigQuery client and write helpers for the attribution engine."""

from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Any, Mapping, Sequence

from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

LOGGER = logging.getLogger(__name__)
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "local-demo-project")
DATASET_ID = os.getenv("BQ_DATASET", "marketing_demo")


def get_bq_client() -> bigquery.Client:
    """Return a BigQuery client using the configured GCP project."""
    return bigquery.Client(project=PROJECT_ID)


def _table_id(table_name: str) -> str:
    """Build a fully qualified BigQuery table identifier."""
    return f"{PROJECT_ID}.{DATASET_ID}.{table_name}"


def _insert_rows(table_name: str, rows: Sequence[Mapping[str, Any]]) -> None:
    """Insert rows into a BigQuery table and raise on insert errors."""
    if not rows:
        LOGGER.info("No rows to write to %s", table_name)
        return
    errors = get_bq_client().insert_rows_json(_table_id(table_name), list(rows))
    if errors:
        raise RuntimeError(f"BigQuery insert errors for {table_name}: {errors}")
    LOGGER.info("Inserted %d rows into %s", len(rows), table_name)


def write_ad_spend(rows: Sequence[Mapping[str, Any]]) -> None:
    """Write normalized advertising spend rows."""
    _insert_rows("fact_ad_spend", rows)


def write_orders(rows: Sequence[Mapping[str, Any]]) -> None:
    """Write normalized order rows."""
    _insert_rows("fact_orders", rows)


def write_events(rows: Sequence[Mapping[str, Any]]) -> None:
    """Write normalized event rows."""
    _insert_rows("fact_events", rows)


def write_attribution(rows: Sequence[Mapping[str, Any]]) -> None:
    """Write order attribution rows."""
    _insert_rows("fact_attribution", rows)


def write_campaign_metrics(rows: Sequence[Mapping[str, Any]]) -> None:
    """Write campaign metric rows."""
    _insert_rows("fact_campaign_metrics", rows)


def update_freshness(source: str, timestamp: datetime) -> None:
    """Upsert the latest successful processing timestamp for a source."""
    query = f"""
    MERGE `{_table_id('data_health')}` AS target
    USING (SELECT @source AS source, @timestamp AS latest_timestamp) AS incoming
    ON target.source = incoming.source
    WHEN MATCHED THEN UPDATE SET latest_timestamp = incoming.latest_timestamp,
        status = 'healthy', inserted_at = CURRENT_TIMESTAMP()
    WHEN NOT MATCHED THEN INSERT (source, latest_timestamp, status)
        VALUES (incoming.source, incoming.latest_timestamp, 'healthy')
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("source", "STRING", source),
            bigquery.ScalarQueryParameter("timestamp", "TIMESTAMP", timestamp),
        ]
    )
    get_bq_client().query(query, job_config=job_config).result()
