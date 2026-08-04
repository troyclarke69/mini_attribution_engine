CREATE TABLE IF NOT EXISTS `thub-10b72.marketing_demo.fact_attribution` (
  order_id STRING NOT NULL,
  customer_id STRING NOT NULL,
  campaign_id STRING,
  touch_ts TIMESTAMP,
  revenue FLOAT64 NOT NULL,
  inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(touch_ts)
CLUSTER BY campaign_id, customer_id;
