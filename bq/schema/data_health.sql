CREATE TABLE IF NOT EXISTS `thub-10b72.marketing_demo.data_health` (
  source STRING NOT NULL,
  latest_timestamp TIMESTAMP,
  status STRING,
  inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(latest_timestamp)
CLUSTER BY source;
