CREATE OR REPLACE TABLE `thub-10b72.marketing_demo.fact_campaign_metrics_features` AS
WITH base AS (
  SELECT
    campaign_id,
    metric_date,
    spend,
    attributed_revenue,
    conversions,
    cac,
    roas
  FROM `thub-10b72.marketing_demo.fact_campaign_metrics`
),

rolling AS (
  SELECT
    campaign_id,
    metric_date,

    -- Rolling 7-day ROAS
    AVG(roas) OVER (
      PARTITION BY campaign_id
      ORDER BY metric_date
      ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_7d_roas,

    -- Rolling 7-day spend
    AVG(spend) OVER (
      PARTITION BY campaign_id
      ORDER BY metric_date
      ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_7d_spend,

    -- Rolling 7-day conversions
    AVG(conversions) OVER (
      PARTITION BY campaign_id
      ORDER BY metric_date
      ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_7d_conversions,

    -- Rolling 7-day volatility (stddev of ROAS)
    STDDEV(roas) OVER (
      PARTITION BY campaign_id
      ORDER BY metric_date
      ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_7d_volatility
  FROM base
),

joined AS (
  SELECT
    b.*,
    r.rolling_7d_roas,
    r.rolling_7d_spend,
    r.rolling_7d_conversions,
    r.rolling_7d_volatility
  FROM base b
  JOIN rolling r
    USING (campaign_id, metric_date)
),

target AS (
  SELECT
    campaign_id,
    metric_date,
    roas AS next_day_roas
  FROM base
),

final AS (
  SELECT
    j.campaign_id,
    j.metric_date,
    j.spend,
    j.attributed_revenue,
    j.conversions,
    j.cac,
    j.roas,
    j.rolling_7d_roas,
    j.rolling_7d_spend,
    j.rolling_7d_conversions,
    j.rolling_7d_volatility,

    -- Target: next day's ROAS
    t.next_day_roas
  FROM joined j
  LEFT JOIN target t
    ON j.campaign_id = t.campaign_id
   AND DATE_ADD(j.metric_date, INTERVAL 1 DAY) = t.metric_date
)

SELECT * FROM final
ORDER BY campaign_id, metric_date;
