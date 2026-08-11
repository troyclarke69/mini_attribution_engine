from fastapi.testclient import TestClient

from api.main import app
import api.routers.metrics as metrics_router


class FakeRow(dict):
    def __getitem__(self, key):
        return dict.__getitem__(self, key)


class FakeClient:
    def query(self, query, job_config=None):
        class _Result:
            def result(self):
                if "fact_campaign_metrics" in query and "COUNT(*)" in query:
                    return [FakeRow({"total_count": 1})]
                if "fact_campaign_metrics" in query and "CAST(metric_date AS STRING)" in query:
                    return [
                        FakeRow({"date": "2026-08-01", "roas": 4.5}),
                        FakeRow({"date": "2026-08-02", "roas": 3.2}),
                    ]
                if "fact_campaign_metrics" in query:
                    return [
                        FakeRow({
                            "campaign_id": "camp-1",
                            "metric_date": "2026-08-10",
                            "spend": 500.0,
                            "attributed_revenue": 2500.0,
                            "roas": 5.0,
                            "cac": 50.0,
                            "conversions": 10,
                        })
                    ]
                if "fact_orders" in query:
                    return [
                        FakeRow({
                            "order_id": "o-1",
                            "customer_id": "customer-1",
                            "order_ts": "2026-08-01T12:00:00",
                            "order_date": "2026-08-01",
                            "revenue": 120.0,
                            "currency": "USD",
                        })
                    ]
                if "fact_events" in query:
                    return [
                        FakeRow({
                            "event_id": "e-1",
                            "customer_id": "customer-1",
                            "event_ts": "2026-08-01T09:00:00",
                            "event_date": "2026-08-01",
                            "event_type": "click",
                            "campaign_id": "camp-1",
                            "source": "web",
                        })
                    ]
                if "fact_attribution" in query:
                    return [
                        FakeRow({
                            "order_id": "o-1",
                            "customer_id": "customer-1",
                            "campaign_id": "camp-1",
                            "touch_ts": "2026-08-01T10:00:00",
                            "revenue": 120.0,
                        })
                    ]
                if "fact_ad_spend" in query:
                    return [
                        FakeRow({
                            "campaign_id": "camp-1",
                            "date": "2026-08-10",
                            "spend": 500.0,
                            "impressions": 1000,
                            "clicks": 200,
                            "source": "google",
                        })
                    ]
                return []

        return _Result()


metrics_router.get_bq_client = lambda: FakeClient()
client = TestClient(app)

summary = client.get('/metrics/summary')
roas = client.get('/metrics/trend/roas?campaign_id=camp-1')
orders = client.get('/raw/orders?customer_id=customer-1&limit=10&offset=0')
print({
    'summary_status': summary.status_code,
    'summary_spend': summary.json().get('spend'),
    'roas_status': roas.status_code,
    'roas_first': roas.json()[0].get('roas') if roas.json() else None,
    'orders_status': orders.status_code,
    'orders_count': orders.json().get('count'),
})
