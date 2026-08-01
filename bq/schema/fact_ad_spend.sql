CREATE TABLE IF NOT EXISTS `${GCP_PROJECT_ID}.marketing_demo.fact_ad_spend` (
  campaign_id STRING NOT NULL,
  date DATE NOT NULL,
  spend FLOAT64 NOT NULL,
  impressions INT64,
  clicks INT64,
  source STRING,
  inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY date
CLUSTER BY campaign_id;
