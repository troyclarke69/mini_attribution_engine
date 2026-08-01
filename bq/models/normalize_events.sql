SELECT DISTINCT
  CAST(event_id AS STRING) AS event_id,
  CAST(customer_id AS STRING) AS customer_id,
  TIMESTAMP(event_ts) AS event_ts,
  DATE(event_ts) AS event_date,
  event_type,
  CAST(campaign_id AS STRING) AS campaign_id,
  source,
  CURRENT_TIMESTAMP() AS inserted_at
FROM `${GCP_PROJECT_ID}.marketing_demo.raw_events`;
