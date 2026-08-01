"""Pydantic models for campaign metrics responses."""

from datetime import date

from pydantic import BaseModel, Field


class CampaignMetric(BaseModel):
    """A campaign's spend and attribution performance for a day."""

    campaign_id: str
    metric_date: date
    spend: float = Field(ge=0)
    attributed_revenue: float = Field(ge=0)
    roas: float = Field(ge=0)
    cac: float = Field(ge=0)
    conversions: int = Field(ge=0)


class SummaryMetrics(BaseModel):
    """Aggregated performance across all campaigns."""

    spend: float
    attributed_revenue: float
    roas: float
    cac: float
    conversions: int
    campaigns: list[CampaignMetric]


class HealthStatus(BaseModel):
    """Latest processing status for one data source."""

    source: str
    latest_timestamp: str | None
    status: str
