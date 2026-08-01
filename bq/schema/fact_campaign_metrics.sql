CREATE TABLE IF NOT EXISTS `${GCP_PROJECT_ID}.marketing_demo.fact_campaign_metrics` (
  campaign_id STRING NOT NULL,
  metric_date DATE NOT NULL,
  spend FLOAT64 NOT NULL,
  attributed_revenue FLOAT64 NOT NULL,
  roas FLOAT64,
  cac FLOAT64,
  conversions INT64,
  inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY metric_date
CLUSTER BY campaign_id;
