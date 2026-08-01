# Mini Marketing Attribution Engine

A demo pipeline that ingests mock ads, clickstream events, and orders, stores normalized facts in BigQuery, applies seven-day last-touch attribution, and exposes campaign performance through FastAPI and a React dashboard.

## Layout

- `etl/`: mock ingestion, normalization, BigQuery writes, and attribution.
- `bq/schema/`: partitioned and clustered BigQuery table definitions.
- `bq/models/`: reusable normalization and attribution SQL.
- `airflow/dags/`: hourly, quarter-hourly, and ten-minute orchestration.
- `api/`: FastAPI metrics and freshness endpoints.
- `frontend/`: lightweight React dashboard.
- `k8s/`: FastAPI-only Kubernetes deployment.

## Local setup

1. Copy `.env.example` to `.env` and set `GCP_PROJECT_ID` plus a service account path.
2. Create the `marketing_demo` dataset and run the six files in `bq/schema/` after replacing `${GCP_PROJECT_ID}` with your project ID.
3. Start the full local stack:

```powershell
docker compose up --build
```

The dashboard is at `http://localhost:3000`, FastAPI docs at `http://localhost:8000/docs`, and Airflow at `http://localhost:8080`.

## API

- `GET /metrics/summary` returns aggregate spend, attributed revenue, ROAS, CAC, conversions, and campaign rows.
- `GET /metrics/campaign/{id}` returns the latest row for one campaign.
- `GET /health` returns freshness status from `data_health`.

## Kubernetes

Build and publish the FastAPI image as `mini-attribution-api:latest`, then apply the manifests:

```powershell
kubectl apply -f k8s/
```

The deployment uses two replicas, a ClusterIP service, an optional ingress, a ConfigMap, and a CPU-based HPA. Airflow remains in Docker Compose.
