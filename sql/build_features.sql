WITH base AS (
  SELECT
    metric_date AS date,
    campaign_id,
    spend,
    attributed_revenue,
    conversions,
    cac,
    roas
  FROM `thub-10b72.marketing_demo.campaign_metrics`
),

events AS (
  SELECT
    DATE(event_ts) AS date,
    campaign_id,
    COUNT(*) AS events_count
  FROM `thub-10b72.marketing_demo.fact_events`
  GROUP BY date, campaign_id
),

joined AS (
  SELECT
    b.date,
    b.campaign_id,
    b.spend,
    b.attributed_revenue,
    b.conversions,
    b.cac,
    b.roas,
    COALESCE(e.events_count, 0) AS events_count
  FROM base b
  LEFT JOIN events e
    ON b.date = e.date
   AND b.campaign_id = e.campaign_id
)

SELECT
  *,
  AVG(roas) OVER (
    PARTITION BY campaign_id
    ORDER BY date
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
  ) AS rolling_7d_roas,

  AVG(spend) OVER (
    PARTITION BY campaign_id
    ORDER BY date
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
  ) AS rolling_7d_spend,

  AVG(conversions) OVER (
    PARTITION BY campaign_id
    ORDER BY date
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
  ) AS rolling_7d_conversions,

  STDDEV(roas) OVER (
    PARTITION BY campaign_id
    ORDER BY date
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
  ) AS rolling_7d_volatility

FROM joined
ORDER BY date, campaign_id;
