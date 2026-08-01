CREATE TABLE IF NOT EXISTS `${GCP_PROJECT_ID}.marketing_demo.fact_events` (
  event_id STRING NOT NULL,
  customer_id STRING NOT NULL,
  event_ts TIMESTAMP NOT NULL,
  event_date DATE NOT NULL,
  event_type STRING,
  campaign_id STRING,
  source STRING,
  inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY event_date
CLUSTER BY campaign_id, customer_id;
