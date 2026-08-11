# ⭐ **MASTER PROMPT — Mini Attribution Engine 
(BigQuery + Docker + Lightweight Kubernetes)**  
*(Optimized for Copilot in VS Code)*

> **Copilot: You are assisting in building a complete “Mini Marketing Attribution Engine” using Python, Airflow, BigQuery, FastAPI, Docker, and a lightweight Kubernetes deployment for the FastAPI backend.  
> Follow these instructions exactly when generating code.  
> Maintain consistent naming, folder structure, imports, and BigQuery usage across all files.  
> Generate full files, not snippets.**

---

## **1. Project Overview**

Build a full demo system that:

- Ingests mock marketing data (ads, clickstream events, orders)  
- Normalizes and stores it in **BigQuery**  
- Runs a **last‑touch attribution model**  
- Computes campaign metrics (ROAS, CAC, attributed revenue)  
- Exposes metrics via a **FastAPI backend**  
- Provides a minimal **React dashboard**  
- Uses **Airflow** for orchestration  
- Uses **Docker Compose** for local development  
- Deploys **FastAPI** to Kubernetes (lightweight showcase)

---

## **2. Repository Structure**

Copilot: create files exactly as listed.

```
mini_attribution_engine/
    airflow/
        dags/
            ads_ingestion_dag.py
            orders_ingestion_dag.py
            events_compaction_dag.py
            attribution_dag.py
        docker-compose.yaml
        requirements.txt
    etl/
        ads_ingestion.py
        orders_ingestion.py
        events_compaction.py
        attribution.py
        bq.py
    bq/
        schema/
            fact_ad_spend.sql
            fact_orders.sql
            fact_events.sql
            fact_attribution.sql
            fact_campaign_metrics.sql
            data_health.sql
        models/
            normalize_ads.sql
            normalize_orders.sql
            normalize_events.sql
            attribution_last_touch.sql
            campaign_metrics.sql
    api/
        main.py
        routers/
            metrics.py
            health.py
        models/
            campaign_metrics.py
    frontend/
        src/
            App.jsx
            components/
                CampaignTable.jsx
                SummaryCards.jsx
        package.json
    k8s/
        fastapi-deployment.yaml
        fastapi-service.yaml
        fastapi-ingress.yaml
        fastapi-configmap.yaml
        fastapi-hpa.yaml
```

---

## **3. BigQuery Layer**

**Dataset:** `marketing_demo`

Copilot: generate SQL schema files for all tables using:

- `STRING`, `INT64`, `FLOAT64`, `TIMESTAMP`, `DATE`, `BOOL`
- Partition by `date` or `event_ts`
- Cluster by `campaign_id`, `customer_id`
- Add `inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()`

Tables:

- `fact_ad_spend`  
- `fact_orders`  
- `fact_events`  
- `fact_attribution`  
- `fact_campaign_metrics`  
- `data_health`

---

## **4. BigQuery Client Module**

Copilot: create `etl/bq.py` with:

- `get_bq_client()` using `google-cloud-bigquery`
- helper functions:
  - `write_ad_spend(rows)`
  - `write_orders(rows)`
  - `write_events(rows)`
  - `write_attribution(rows)`
  - `write_campaign_metrics(rows)`
  - `update_freshness(source, timestamp)`
- Use parameterized queries or `InsertJob` API
- Use environment variables for GCP project + dataset

---

## **5. ETL Modules**

Copilot: generate full Python files.

### **ads_ingestion.py**
- `fetch_ads_raw()` → mock API call  
- `normalize_ads(raw)`  
- `write_ads_to_bq(normalized)`

### **orders_ingestion.py**
Same pattern.

### **events_compaction.py**
- `compact_events_raw()`  
- `normalize_events()`  
- `write_events_to_bq()`

### **attribution.py**
Implement **last‑touch attribution**:

- For each order:
  - find most recent event for same customer within 7‑day lookback  
  - join to campaign  
  - write row to `fact_attribution`

Compute:

- ROAS  
- CAC  
- attributed revenue  
- write to `fact_campaign_metrics`

Use SQL models in `bq/models/`.

---

## **6. Airflow DAGs**

Copilot: generate full DAG files using:

- `PythonOperator`
- `BigQueryInsertJobOperator`
- XCom for passing data

Schedules:

- ads: hourly  
- orders: every 15 minutes  
- events: every 10 minutes  
- attribution: hourly  

### **ads_ingestion_dag.py**
Tasks:
- `fetch_ads_raw`
- `normalize_ads`
- `write_ads_to_bq`
- `update_ads_freshness`

### **orders_ingestion_dag.py**
Same pattern.

### **events_compaction_dag.py**
Tasks:
- `compact_events_raw`
- `normalize_events`
- `write_events_to_bq`
- `update_events_freshness`

### **attribution_dag.py**
Tasks:
- `wait_for_sources_fresh`
- `run_last_touch_attribution`
- `compute_summary_metrics`
- `write_attribution_to_bq`
- `update_attribution_freshness`

---

## **7. FastAPI Backend**

Copilot: generate full files.

### **api/main.py**
- Initialize FastAPI  
- Include routers  
- Create BigQuery client  

### **metrics.py**
Endpoints:

- `GET /metrics/summary`  
- `GET /metrics/campaign/{id}`  

### **health.py**
Endpoint:

- `GET /health` → read from `data_health`

---

## **8. React Frontend**

Copilot: scaffold minimal dashboard.

Components:

- `SummaryCards.jsx`  
- `CampaignTable.jsx`  

Features:

- Fetch metrics from FastAPI  
- Display ROAS, CAC, spend, attributed revenue

---

## **9. Coding Style Requirements**

Copilot: follow these rules:

- Python 3.10+  
- Type hints everywhere  
- Docstrings for all functions  
- Use `logging` module  
- No hardcoded credentials  
- Use environment variables for GCP project + dataset  
- Use `.env` + `python-dotenv`  

---

## **10. Mock Data**

Copilot: generate mock data for:

- 3–5 campaigns  
- random clickstream events  
- random orders  
- timestamps across several days  

---

## **11. Deliverables**

Copilot: produce:

- All Python modules  
- All Airflow DAGs  
- All BigQuery schema files  
- FastAPI backend  
- React frontend scaffolding  
- Docker Compose for Airflow + FastAPI + frontend  
- Kubernetes manifests for FastAPI  
- README.md with run instructions

---

## **12. Containerization & Deployment Requirements**

### **Docker (required)**  
Copilot: generate Dockerfiles for:

- Airflow  
- FastAPI backend  
- React frontend  

Copilot: generate `docker-compose.yaml` with services:

- `airflow-webserver`  
- `airflow-scheduler`  
- `airflow-worker`  
- `fastapi`  
- `frontend`  

### **Kubernetes (lightweight showcase)**  
Copilot: generate manifests in `k8s/`:

```
k8s/
    fastapi-deployment.yaml
    fastapi-service.yaml
    fastapi-ingress.yaml
    fastapi-configmap.yaml
    fastapi-hpa.yaml
```

Requirements:

- Deployment: 2 replicas  
- Service: ClusterIP  
- Ingress: optional  
- ConfigMap: environment variables (GCP project, dataset)  
- HPA: scale on CPU or request count  

Airflow stays in Docker Compose.  
Only FastAPI is deployed to Kubernetes.
