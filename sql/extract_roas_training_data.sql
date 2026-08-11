WITH features AS (
  SELECT
    date,
    campaign_id,
    spend,
    attributed_revenue,
    conversions,
    cac,
    roas,
    events_count,
    rolling_7d_roas,
    rolling_7d_spend,
    rolling_7d_conversions,
    rolling_7d_volatility
  FROM `thub-10b72.marketing_demo.features_campaign_daily`
),

lagged AS (
  SELECT
    f.*,
    LEAD(roas, 1) OVER (
      PARTITION BY campaign_id
      ORDER BY date
    ) AS target_next_day_roas
  FROM features f
)

SELECT *
FROM lagged
WHERE target_next_day_roas IS NOT NULL
ORDER BY campaign_id, date;
