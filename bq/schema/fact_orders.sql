CREATE TABLE IF NOT EXISTS `thub-10b72.marketing_demo.fact_orders` (
  order_id STRING NOT NULL,
  customer_id STRING NOT NULL,
  order_ts TIMESTAMP NOT NULL,
  order_date DATE NOT NULL,
  revenue FLOAT64 NOT NULL,
  currency STRING,
  inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY order_date
CLUSTER BY customer_id
OPTIONS (
  partition_expiration_days = 180
);
