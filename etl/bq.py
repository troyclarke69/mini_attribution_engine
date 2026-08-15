"""BigQuery client and write helpers for the attribution engine."""

from __future__ import annotations

import functools
import logging
import os
import json
import base64
from datetime import datetime
from typing import Any, Mapping, Sequence

from dotenv import load_dotenv
from google.cloud import bigquery
from google.oauth2 import service_account

load_dotenv()

LOGGER = logging.getLogger(__name__)

# Project + dataset from environment
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "local-demo-project")
DATASET_ID = os.getenv("BQ_DATASET", "marketing_demo")


# ---------------------------------------------------------------------------
#  FIXED: Unified credential loader using GCP_CREDS (base64)
# ---------------------------------------------------------------------------
@functools.lru_cache(maxsize=1)
def get_bq_client() -> bigquery.Client:
    """Return a BigQuery client using explicit service-account credentials."""

    creds_b64 = os.getenv("GCP_CREDS")
    if not creds_b64:
        raise RuntimeError("GCP_CREDS environment variable is missing")

    # Decode Base64 → JSON dict
    creds_json = json.loads(base64.b64decode(creds_b64))

    # Build credentials object
    credentials = service_account.Credentials.from_service_account_info(creds_json)

    # Create BigQuery client with explicit credentials
    return bigquery.Client(
        project=creds_json["project_id"],
        credentials=credentials,
    )


# ---------------------------------------------------------------------------
#  Helpers
# ---------------------------------------------------------------------------
def _table_id(table_name: str) -> str:
    """Build a fully qualified BigQuery table identifier."""
    return f"{PROJECT_ID}.{DATASET_ID}.{table_name}"


def _insert_rows(table_name: str, rows: Sequence[Mapping[str, Any]]) -> None:
    """Load rows into a BigQuery table via a batch JSON load job."""
    if not rows:
        LOGGER.info("No rows to write to %s", table_name)
        return

    client = get_bq_client()
    table_id = _table_id(table_name)

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )

    job = client.load_table_from_json(list(rows), table_id, job_config=job_config)
    job.result()

    LOGGER.info("Inserted %d rows into %s", len(rows), table_name)


# ---------------------------------------------------------------------------
#  Public write helpers
# ---------------------------------------------------------------------------
def write_ad_spend(rows: Sequence[Mapping[str, Any]]) -> None:
    _insert_rows("fact_ad_spend", rows)


def write_orders(rows: Sequence[Mapping[str, Any]]) -> None:
    _insert_rows("fact_orders", rows)


def write_events(rows: Sequence[Mapping[str, Any]]) -> None:
    _insert_rows("fact_events", rows)


def write_attribution(rows: Sequence[Mapping[str, Any]]) -> None:
    _insert_rows("fact_attribution", rows)


def write_campaign_metrics(rows: Sequence[Mapping[str, Any]]) -> None:
    _insert_rows("fact_campaign_metrics", rows)


# ---------------------------------------------------------------------------
#  Freshness updater
# ---------------------------------------------------------------------------
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

    client = get_bq_client()
    client.query(query, job_config=job_config).result()
