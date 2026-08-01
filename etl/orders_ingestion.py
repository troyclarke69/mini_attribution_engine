"""Mock orders API ingestion and normalization."""

from __future__ import annotations

import logging
import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from etl.bq import update_freshness, write_orders

LOGGER = logging.getLogger(__name__)


def fetch_orders_raw() -> list[dict[str, Any]]:
    """Return mock orders from the previous seven days."""
    now = datetime.now(timezone.utc)
    return [
        {
            "order_id": f"ord_{uuid.uuid4().hex[:10]}",
            "customer_id": f"customer_{random.randint(1, 25):03d}",
            "order_ts": (now - timedelta(days=random.uniform(0, 6))).isoformat(),
            "revenue": round(random.uniform(25.0, 300.0), 2),
            "currency": "USD",
        }
        for _ in range(20)
    ]


def normalize_orders(raw: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalize raw orders to the fact_orders schema."""
    inserted_at = datetime.now(timezone.utc).isoformat()
    return [
        {
            "order_id": str(row["order_id"]),
            "customer_id": str(row["customer_id"]),
            "order_ts": datetime.fromisoformat(str(row["order_ts"])).isoformat(),
            "order_date": datetime.fromisoformat(str(row["order_ts"])).date().isoformat(),
            "revenue": float(row["revenue"]),
            "currency": str(row.get("currency", "USD")),
            "inserted_at": inserted_at,
        }
        for row in raw
    ]


def write_orders_to_bq(normalized: list[dict[str, Any]]) -> None:
    """Write normalized orders and update source freshness."""
    write_orders(normalized)
    update_freshness("orders", datetime.now(timezone.utc))
    LOGGER.info("Processed %d orders", len(normalized))
