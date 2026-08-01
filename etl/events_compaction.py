"""Mock clickstream compaction and normalization."""

from __future__ import annotations

import logging
import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from etl.bq import update_freshness, write_events

LOGGER = logging.getLogger(__name__)
CAMPAIGNS = ["search_brand", "social_prospecting", "video_awareness", "email_reengagement"]
EVENT_TYPES = ["page_view", "click", "landing", "add_to_cart"]


def compact_events_raw() -> list[dict[str, Any]]:
    """Return mock clickstream events across the previous seven days."""
    now = datetime.now(timezone.utc)
    return [
        {
            "event_id": f"evt_{uuid.uuid4().hex[:10]}",
            "customer_id": f"customer_{random.randint(1, 25):03d}",
            "event_ts": (now - timedelta(days=random.uniform(0, 7))).isoformat(),
            "event_type": random.choice(EVENT_TYPES),
            "campaign_id": random.choice(CAMPAIGNS),
            "source": "mock_clickstream",
        }
        for _ in range(100)
    ]


def normalize_events(raw: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalize and deduplicate raw events by event identifier."""
    inserted_at = datetime.now(timezone.utc).isoformat()
    normalized: dict[str, dict[str, Any]] = {}
    for row in raw:
        event_ts = datetime.fromisoformat(str(row["event_ts"]))
        normalized[str(row["event_id"])] = {
            "event_id": str(row["event_id"]),
            "customer_id": str(row["customer_id"]),
            "event_ts": event_ts.isoformat(),
            "event_date": event_ts.date().isoformat(),
            "event_type": str(row["event_type"]),
            "campaign_id": str(row["campaign_id"]),
            "source": str(row.get("source", "unknown")),
            "inserted_at": inserted_at,
        }
    return list(normalized.values())


def write_events_to_bq(normalized: list[dict[str, Any]]) -> None:
    """Write compacted events and update source freshness."""
    write_events(normalized)
    update_freshness("events", datetime.now(timezone.utc))
    LOGGER.info("Processed %d events", len(normalized))
