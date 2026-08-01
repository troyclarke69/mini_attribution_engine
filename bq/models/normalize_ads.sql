SELECT
  CAST(campaign_id AS STRING) AS campaign_id,
  DATE(date) AS date,
  SAFE_CAST(spend AS FLOAT64) AS spend,
  SAFE_CAST(impressions AS INT64) AS impressions,
  SAFE_CAST(clicks AS INT64) AS clicks,
  source,
  CURRENT_TIMESTAMP() AS inserted_at
FROM `${GCP_PROJECT_ID}.marketing_demo.raw_ads`;
