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

1. Copy `.env.example` to `.env` and set `GCP_PROJECT_ID` plus your service account path.
2. Create the `marketing_demo` dataset in BigQuery.
3. Apply the SQL table definitions in `bq/schema/` with your project ID.
4. Initialize Airflow metadata inside Docker before starting the full stack:

```powershell
docker compose -f airflow/docker-compose-init.yaml up --build
```

5. Once `airflow db init` succeeds, bring the stack up:

```powershell
docker compose down
docker compose up --build
```

6. If you make a clean restart later, the metadata database will persist in `airflow/airflow.db` and logs in `airflow/logs`.

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
