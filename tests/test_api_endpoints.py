from types import SimpleNamespace

from fastapi.testclient import TestClient

from api.main import app


class FakeRow(dict):
    def __getitem__(self, key):
        return dict.__getitem__(self, key)


class FakeResult(list):
    def __iter__(self):
        return super().__iter__()


class FakeClient:
    def query(self, query, job_config=None):
        class FakeQueryResult:
            def result(self):
                if "COUNT(*)" in query:
                    return [FakeRow({"total_count": 1})]
                if "fact_campaign_metrics" in query and "CAST(metric_date AS STRING)" in query:
                    return [
                        FakeRow({"date": "2026-08-01", "roas": 4.5}),
                        FakeRow({"date": "2026-08-02", "roas": 3.2}),
                    ]
                if "fact_campaign_metrics" in query:
                    return [
                        FakeRow(
                            {
                                "campaign_id": "camp-1",
                                "metric_date": "2026-08-10",
                                "spend": 500.0,
                                "attributed_revenue": 2500.0,
                                "roas": 5.0,
                                "cac": 50.0,
                                "conversions": 10,
                            }
                        )
                    ]
                if "fact_orders" in query:
                    return [
                        FakeRow(
                            {
                                "order_id": "o-1",
                                "customer_id": "customer-1",
                                "order_ts": "2026-08-01T12:00:00",
                                "order_date": "2026-08-01",
                                "revenue": 120.0,
                                "currency": "USD",
                            }
                        )
                    ]
                if "fact_events" in query:
                    return [
                        FakeRow(
                            {
                                "event_id": "e-1",
                                "customer_id": "customer-1",
                                "event_ts": "2026-08-01T09:00:00",
                                "event_date": "2026-08-01",
                                "event_type": "click",
                                "campaign_id": "camp-1",
                                "source": "web",
                            }
                        )
                    ]
                if "fact_attribution" in query:
                    return [
                        FakeRow(
                            {
                                "order_id": "o-1",
                                "customer_id": "customer-1",
                                "campaign_id": "camp-1",
                                "touch_ts": "2026-08-01T10:00:00",
                                "revenue": 120.0,
                            }
                        )
                    ]
                if "fact_ad_spend" in query:
                    return [
                        FakeRow(
                            {
                                "campaign_id": "camp-1",
                                "date": "2026-08-10",
                                "spend": 500.0,
                                "impressions": 1000,
                                "clicks": 200,
                                "source": "google",
                            }
                        )
                    ]
                return []

        return FakeQueryResult()


client = TestClient(app)


def test_metrics_summary(monkeypatch):
    monkeypatch.setattr("api.routers.metrics.get_bq_client", lambda: FakeClient())
    response = client.get("/metrics/summary")
    assert response.status_code == 200
    payload = response.json()
    assert payload["spend"] == 500.0
    assert payload["campaigns"][0]["campaign_id"] == "camp-1"


def test_roas_trend_endpoint(monkeypatch):
    monkeypatch.setattr("api.routers.metrics.get_bq_client", lambda: FakeClient())
    response = client.get("/metrics/trend/roas?campaign_id=camp-1")
    assert response.status_code == 200
    assert response.json()[0]["roas"] == 4.5


def test_raw_orders_endpoint(monkeypatch):
    monkeypatch.setattr("api.routers.metrics.get_bq_client", lambda: FakeClient())
    response = client.get("/raw/orders?customer_id=customer-1&limit=10&offset=0")
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 1
    assert payload["rows"][0]["customer_id"] == "customer-1"
