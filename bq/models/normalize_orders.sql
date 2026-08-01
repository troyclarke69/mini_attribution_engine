SELECT
  CAST(order_id AS STRING) AS order_id,
  CAST(customer_id AS STRING) AS customer_id,
  TIMESTAMP(order_ts) AS order_ts,
  DATE(order_ts) AS order_date,
  SAFE_CAST(revenue AS FLOAT64) AS revenue,
  COALESCE(currency, 'USD') AS currency,
  CURRENT_TIMESTAMP() AS inserted_at
FROM `${GCP_PROJECT_ID}.marketing_demo.raw_orders`;
