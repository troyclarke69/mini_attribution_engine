SELECT
  ad.campaign_id,
  ad.date AS metric_date,
  ad.spend,
  COALESCE(SUM(attribution.revenue), 0) AS attributed_revenue,
  SAFE_DIVIDE(COALESCE(SUM(attribution.revenue), 0), ad.spend) AS roas,
  SAFE_DIVIDE(ad.spend, COUNT(DISTINCT attribution.order_id)) AS cac,
  COUNT(DISTINCT attribution.order_id) AS conversions,
  CURRENT_TIMESTAMP() AS inserted_at
FROM `${GCP_PROJECT_ID}.marketing_demo.fact_ad_spend` ad
LEFT JOIN `${GCP_PROJECT_ID}.marketing_demo.fact_attribution` attribution
  ON ad.campaign_id = attribution.campaign_id
 AND ad.date = DATE(attribution.touch_ts)
GROUP BY ad.campaign_id, ad.date, ad.spend;
