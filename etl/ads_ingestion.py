"""Mock advertising API ingestion and normalization."""

from __future__ import annotations

import logging
import random
from datetime import date, datetime, timedelta, timezone
from typing import Any

from etl.bq import update_freshness, write_ad_spend

LOGGER = logging.getLogger(__name__)
CAMPAIGNS = ["search_brand", "social_prospecting", "video_awareness", "email_reengagement"]


def fetch_ads_raw() -> list[dict[str, Any]]:
    """Return mock daily advertising records for several campaigns."""
    today = date.today()
    return [
        {
            "campaign_id": campaign,
            "date": today.isoformat(),
            "spend": round(random.uniform(80.0, 450.0), 2),
            "impressions": random.randint(3000, 25000),
            "clicks": random.randint(100, 1800),
            "source": "mock_ads_api",
        }
        for campaign in CAMPAIGNS
    ]


def normalize_ads(raw: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalize raw ad records to the fact_ad_spend schema."""
    inserted_at = datetime.now(timezone.utc).isoformat()
    return [
        {
            "campaign_id": str(row["campaign_id"]),
            "date": date.fromisoformat(str(row["date"])).isoformat(),
            "spend": float(row["spend"]),
            "impressions": int(row["impressions"]),
            "clicks": int(row["clicks"]),
            "source": str(row.get("source", "unknown")),
            "inserted_at": inserted_at,
        }
        for row in raw
    ]


def write_ads_to_bq(normalized: list[dict[str, Any]]) -> None:
    """Write normalized advertising records and update source freshness."""
    write_ad_spend(normalized)
    update_freshness("ads", datetime.now(timezone.utc))
    LOGGER.info("Processed %d ad records", len(normalized))
