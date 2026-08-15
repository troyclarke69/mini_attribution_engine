# Mini Marketing Attribution Engine
**************************************************

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

1. Copy `.env.example` to `.env`, fill in `GCP_PROJECT_ID`, and set `GCP_CREDS` (see [Credentials](#credentials) below).
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

## Credentials

Every service that talks to BigQuery - the FastAPI app, Airflow's ingestion
DAGs, and the local ML training/inspection scripts under `ml/` - authenticates
through a single environment variable, `GCP_CREDS`: the service account JSON,
base64-encoded, read from `.env` (or from a Fly secret in production). Nothing
reads `GOOGLE_APPLICATION_CREDENTIALS` or a mounted key file directly anymore
(see the Changelog at the bottom for why that changed).

To generate the value from a service account key file:

```powershell
$creds = Get-Content .\gcp\service-account.json -Raw
$creds_b64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($creds))
Write-Output $creds_b64
```

Paste the result into `.env` as `GCP_CREDS=<value>`. For the Fly deployment,
set the same variable as a secret instead of committing it:

```powershell
fly secrets set GCP_CREDS="<value>"
```

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




$creds = Get-Content .\gcp\service-account.json -Raw
$creds_b64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($creds))

# IMPORTANT NOTES ON ML DEV/TESTING

* Training must be done in docker - local is not set up (missing google bigquery & python deps for creds, etc) *

bash:
docker compose up --build
docker exec -it mini_attribution_engine-fastapi-1 bash

* AFTER RETRAIN - Validate the output
python - <<EOF
from ml.data_loader import get_latest_feature_row
df = get_latest_feature_row()
print(df)
EOF

* PREDICTION
python - <<EOF
from ml.data_loader import get_latest_feature_row
import joblib

FEATURE_ORDER = [
    "spend",
    "attributed_revenue",
    "conversions",
    "cac",
    "roas",
    "rolling_7d_roas",
    "rolling_7d_spend",
    "rolling_7d_conversions",
    "rolling_7d_volatility",
]

row = get_latest_feature_row()
X = row.drop(columns=["metric_date", "target_next_day_roas"])
X = X[FEATURE_ORDER]

model = joblib.load("ml/model_roas.pkl")
print("Prediction:", model.predict(X)[0])
EOF

* Inspect Feature table
python - <<EOF
from etl.bq import get_bq_client
client = get_bq_client()

query = """
SELECT *
FROM `thub-10b72.marketing_demo.fact_campaign_metrics_features`
ORDER BY metric_date DESC
LIMIT 5
"""

df = client.query(query).to_dataframe()
print(df)
EOF


**In docker bash:**
train:
python -m ml.train_roas_model
inspect:
python -m ml.inspect_features_importance
## Changelog

### 2026-08-15

- Fixed the Fly deploy build failure caused by a stale `context = "api"` in
  `fly.toml` (a no-op that masked a mismatched `.dockerignore`/Dockerfile
  layout after a credential reorg moved files around).
- Fixed the Airflow Docker Compose build failure (`.dockerignore` was
  excluding `dags/`/`airflow/`, which the Airflow Dockerfile needs since it
  shares the root build context).
- Fixed the "site offline until refresh" cold start: the ROAS model and
  BigQuery client were loaded eagerly at import time (and the model pickle
  was loaded twice), blocking `uvicorn` from opening its socket. Both are
  now lazily loaded and cached, with a background warm-up on startup.
- Added 180-day partition expiration to the BigQuery fact tables.
- Fixed the ROAS prediction card getting stuck on "Loading..." then showing
  "0.000": added an explicit error state with a Retry button instead of
  relying on a browser refresh, and moved the fetch to only happen when the
  Charts & Trends tab is opened.
- Unified all BigQuery authentication (FastAPI, Airflow DAGs, local ML
  scripts) onto a single `GCP_CREDS` base64 environment variable, replacing
  the old `GOOGLE_APPLICATION_CREDENTIALS` mounted-key-file pattern. Removed
  the now-dead code and config left over from before that change.
- Fixed duplicate/inflated BigQuery data: `fact_attribution` and
  `fact_campaign_metrics` are full recomputes each run, but were being
  appended instead of replaced. Both now use `WRITE_TRUNCATE`.
- Fixed the ROAS prediction being stuck at a stale value: the query backing
  it filtered on `next_day_roas IS NOT NULL`, which the truly-latest row can
  never satisfy (tomorrow hasn't happened yet). Added a dedicated query for
  live serving that doesn't filter on the target column.
- Fixed charts and anomaly detection rendering as undeduplicated,
  unaggregated "messy blobs": multiple campaigns' individual rows for the
  same date were being plotted/analyzed as separate points instead of one
  aggregated line per date. Also fixed a bug where the spend/revenue trend
  silently dropped the revenue series entirely.
