WITH ranked_events AS (
  SELECT
    o.order_id,
    o.customer_id,
    o.revenue,
    e.campaign_id,
    e.event_ts AS touch_ts,
    ROW_NUMBER() OVER (PARTITION BY o.order_id ORDER BY e.event_ts DESC) AS event_rank
  FROM `${GCP_PROJECT_ID}.marketing_demo.fact_orders` o
  LEFT JOIN `${GCP_PROJECT_ID}.marketing_demo.fact_events` e
    ON e.customer_id = o.customer_id
   AND e.event_ts BETWEEN TIMESTAMP_SUB(o.order_ts, INTERVAL 7 DAY) AND o.order_ts
)
SELECT order_id, customer_id, campaign_id, touch_ts, revenue, CURRENT_TIMESTAMP() AS inserted_at
FROM ranked_events
WHERE event_rank = 1;
