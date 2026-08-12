# Mini Marketing Attribution Engine

# IMPORTANT NOTES ON ML

* Training must be done in docker - local is not set up (missing google bigquery & python deps for creds, etc) *
So run in docker bash:

docker compose up --build
docker exec -it mini_attribution_engine-fastapi-1 bash
**In docker bash:**
train:
python -m ml.train_roas_model
inspect:
python -m ml.inspect_features_importance

* ****************************************************************************

A demo pipeline that ingests mock ads, clickstream events, and orders, stores normalized facts in BigQuery, applies seven-day last-touch attribution, and exposes campaign performance through FastAPI and a React dashboard.

## Overview

This project combines ETL, attribution, API exposure, and dashboarding in a single demo stack.

The core flow is:

- mock ingestion and normalization in `etl/`
- BigQuery fact tables and schema definitions in `bq/`
- Airflow orchestration in `airflow/`
- FastAPI analytics endpoints in `api/`
- a lightweight React UI in `frontend/`

## Drill-down + charts expansion that adds:

- raw-data API endpoints for ad spend, orders, events, and attribution rows
- time-series trend endpoints for ROAS (Return on Ad Spend), CAC (Customer Acquisition Cost), conversions, and spend/revenue
- a richer dashboard with campaign filters and date-range controls
- reusable chart and table components for deeper investigation

This keeps the original attribution architecture intact while making the data easier to inspect at the campaign and customer level.

## Project layout

- `etl/`: mock ingestion, normalization, BigQuery writes, and attribution logic
- `bq/schema/`: table definitions for fact and data health tables
- `bq/models/`: reusable SQL for normalization and attribution
- `sql/`: trend SQL templates for chart endpoints
- `airflow/dags/`: orchestration for ingestion and attribution jobs (Directed Acyclic Graph)
- `api/`: FastAPI app, router logic, and metrics endpoints
- `frontend/`: React dashboard with raw-data and chart views
- `k8s/`: Kubernetes deployment manifests for the API

## Local setup

1. Copy `.env.example` to `.env` and set your project ID and Google credentials path.
2. Create the `marketing_demo` dataset in BigQuery.
3. Apply the schema definitions in `bq/schema/`.
4. Initialize Airflow metadata before starting the stack:

```powershell
docker compose -f airflow/docker-compose-init.yaml up --build
```

5. Start the full stack:

```powershell
docker compose down
docker compose up --build
```

> `AIRFLOW__CORE__EXECUTOR` is intentionally set to `SequentialExecutor`, so the airflow worker may not show as fully running in Docker Compose.

6. Restart behavior: metadata persists in `airflow/airflow.db` and logs remain under `airflow/logs`.

The main services are:

- dashboard: `http://localhost:3000`
- FastAPI docs: `http://localhost:8000/docs`
- Airflow UI: `http://localhost:8080`

Deployments:
Fly: https://mini-attribution-engine.fly.dev
Netlify: https://miniattributionengine.netlify.dev

## API endpoints

### Summary and campaign metrics

- `GET /metrics/summary` returns aggregate spend, attributed revenue, ROAS, CAC, conversions, and campaign rows
- `GET /metrics/campaign/{id}` returns the latest metric row for a single campaign
- `GET /metrics/trend/roas` returns a daily ROAS series
- `GET /metrics/trend/cac` returns a daily CAC series
- `GET /metrics/trend/conversions` returns a daily conversion series
- `GET /metrics/trend/spend-revenue` returns daily spend and attributed revenue values
- `GET /anomalies/roas` returns ROAS anomaly alerts based on historical z-score, MAD, IQR, and percent-change scoring
- `GET /anomalies/cac` returns CAC anomaly alerts using the same detection logic

### Raw drill-down endpoints

- `GET /raw/ad-spend` returns raw ad spend rows with filters, pagination, and ordering
- `GET /raw/orders` returns raw order rows for a customer or date window
- `GET /raw/events` returns raw clickstream or event rows with campaign/customer filters
- `GET /raw/attribution` returns raw attribution rows with touch-date filters

All raw endpoints support:

- filtering by campaign, customer, or date range
- `limit` and `offset` pagination
- `order_by` sorting
- ISO-safe serialization of date/time values

## Dashboard capabilities

The front-end has been extended with two main views:

### Overview

Shows total KPIs and performance summary cards for the latest campaign metrics.

### Raw Data

Allows users to inspect underlying records across:

- ad spend
- orders
- events
- attribution touches

Features include:

- paging controls
- date filters
- campaign/customer filters
- expandable row details
- empty-state handling

### Charts & Trends

The dashboard includes time-series visualizations for:

- ROAS trend
- CAC trend
- conversions trend
- spend vs revenue comparison

Each chart supports:

- campaign selection
- date-range filtering
- hover tooltips
- trend investigation from a selected date window

## SQL for chart queries

The chart endpoints use trend SQL templates under `sql/`:

- `sql/trend_roas.sql`
- `sql/trend_cac.sql`
- `sql/trend_conversions.sql`
- `sql/trend_spend_revenue.sql`

These queries return date-indexed metric values suitable for the dashboard’s chart components.

## Validation

The project includes API regression coverage for the main summary, trend, and raw-data routes.

Suggested validation commands:

```powershell
cd C:\Projects\mini_attribution_engine
C:/Python313/python.exe -m pytest tests/test_api_endpoints.py -q
```

Frontend validation:

```powershell
cd C:\Projects\mini_attribution_engine\frontend
npm run build
```

## Kubernetes

Build and publish the FastAPI image as `mini-attribution-api:latest`, then apply the manifests:

```powershell
kubectl apply -f k8s/
```

The deployment uses two replicas, a ClusterIP service, an optional ingress, a ConfigMap, and a CPU-based HPA. Airflow remains in Docker Compose.
