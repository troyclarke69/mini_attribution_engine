CREATE TABLE IF NOT EXISTS `${GCP_PROJECT_ID}.marketing_demo.data_health` (
  source STRING NOT NULL,
  latest_timestamp TIMESTAMP,
  status STRING,
  inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(latest_timestamp)
CLUSTER BY source;
