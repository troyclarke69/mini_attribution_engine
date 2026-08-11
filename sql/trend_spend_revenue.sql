SELECT
  CAST(metric_date AS STRING) AS date,
  spend,
  attributed_revenue
FROM `${GCP_PROJECT_ID}.marketing_demo.fact_campaign_metrics`
WHERE (@campaign_id IS NULL OR campaign_id = @campaign_id)
  AND (@date_from IS NULL OR metric_date >= CAST(@date_from AS DATE))
  AND (@date_to IS NULL OR metric_date <= CAST(@date_to AS DATE))
ORDER BY metric_date ASC;
