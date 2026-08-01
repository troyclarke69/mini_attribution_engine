SELECT
  spend.campaign_id,
  spend.date AS metric_date,
  spend.spend,
  COALESCE(SUM(attribution.revenue), 0) AS attributed_revenue,
  SAFE_DIVIDE(COALESCE(SUM(attribution.revenue), 0), spend.spend) AS roas,
  SAFE_DIVIDE(spend.spend, COUNT(DISTINCT attribution.order_id)) AS cac,
  COUNT(DISTINCT attribution.order_id) AS conversions,
  CURRENT_TIMESTAMP() AS inserted_at
FROM `${GCP_PROJECT_ID}.marketing_demo.fact_ad_spend` spend
LEFT JOIN `${GCP_PROJECT_ID}.marketing_demo.fact_attribution` attribution
  ON spend.campaign_id = attribution.campaign_id
 AND spend.date = DATE(attribution.touch_ts)
GROUP BY spend.campaign_id, spend.date, spend.spend;
