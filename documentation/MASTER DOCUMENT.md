# 📘 **Mini Attribution Engine — Master Technical Documentation**

A complete end‑to‑end explanation of how the system ingests data, computes attribution, generates marketing KPIs, detects anomalies, and predicts next‑day ROAS.

This document is designed for: 
- Future contributors  
- Curious engineers  
- Analysts reviewing the outputs 
- the author  

It includes architecture, formulas, code snippets, and plain‑English interpretations of every metric.

---

# 🏗️ **1. System Architecture Overview**

The Mini Attribution Engine consists of five major layers:





## **1.1 Data Storage — BigQuery**
BigQuery stores all raw and enriched marketing data:

- `fact_ad_spend`  
- `fact_orders`  
- `fact_events`  
- `fact_attribution`  
- `fact_campaign_metrics`  
- `fact_campaign_metrics_features` (training + inference features)

These tables contain:
- daily spend  
- conversions  
- attributed revenue  
- ROAS  
- CAC  
- rolling 7‑day aggregates  
- volatility measures  
- next‑day ROAS (training target)

---

## **1.2 ETL Layer (Python + Airflow)**
Airflow orchestrates ingestion and attribution:

- ads ingestion (hourly)  
- orders ingestion (15 min)  
- events compaction (10 min)  
- attribution + metrics (hourly)

ETL responsibilities:
- normalize raw data  
- compute last‑touch attribution  
- calculate daily KPIs  
- generate rolling windows  
- produce training DataFrames  
- produce latest feature row for inference

---

## **1.3 ML Pipeline (RandomForestRegressor)**
Training script:

```bash
python -m ml.train_roas_model
```

Model:
```python
RandomForestRegressor(
    n_estimators=200,
    max_depth=12,
    random_state=42
)
```

Outputs:
- `ml/model_roas.pkl`  
- feature importance report  
- training diagnostics  

---

## **1.4 FastAPI Backend**
FastAPI exposes analytics + ML endpoints:

- `/metrics/summary`  
- `/metrics/trend/*`  
- `/raw/*`  
- `/anomalies/*`  
- `/predict_next_day_roas`

It loads the model at startup and performs inference on demand.

---

## **1.5 React Dashboard**
The dashboard displays:

- summary KPIs  
- ROAS/CAC trends  
- anomaly alerts  
- raw drill‑down tables  
- predicted next‑day ROAS  

It fetches data from FastAPI and renders charts using Recharts.

---

# 📊 **2. Core Marketing Metrics Explained**

## **2.1 ROAS — Return on Ad Spend**
\[
ROAS = \frac{\text{Attributed Revenue}}{\text{Spend}}
\]

Plain English:
> ROAS tells you how much revenue you earned for every dollar spent.

Example:
- Spend = \$100  
- Attributed Revenue = \$450  
- ROAS = 4.5  
→ Every \$1 produced \$4.50 in revenue.

---

## **2.2 CAC — Customer Acquisition Cost**
\[
CAC = \frac{\text{Spend}}{\text{Conversions}}
\]

Plain English:
> CAC tells you how much it costs to acquire one conversion.

Example:
- Spend = \$250  
- Conversions = 10  
- CAC = \$25  

---

## **2.3 Conversions**
In your system:
> A conversion is a completed purchase attributed to a campaign.

Conversions come from:
- `orders`  
- attribution joins with `events`  

---

## **2.4 Attributed Revenue**
Revenue assigned to a campaign via **last‑touch attribution**:

- find the most recent event for the same customer  
- within a 7‑day lookback  
- assign the order to that campaign  

---

# 🔍 **3. ROAS Anomaly Detection (Plain English)**

Your “Recent ROAS Alerts” panel shows **campaigns whose ROAS deviated significantly** from their expected range.

Each alert corresponds to a **different campaign**.

Example alert values:
- 13.516  
- 23.454  
- 29.779  
- 13.712  
- 21.294  

Interpretation:
- **High ROAS (23–30)** → unusually efficient spend  
- **Low ROAS (~13)** → underperformance or spend inefficiency  
- **Deviation** is measured using:
  - z‑score  
  - modified z‑score (MAD)  
  - IQR  
  - percent‑change  
  - rolling deviation  

These alerts help you identify:
- sudden spikes  
- sudden drops  
- volatility bursts  
- attribution timing effects  
- spend anomalies  

---

# 🔮 **4. Predicted Next‑Day ROAS (How It Works)**

The prediction endpoint:

```python
@app.get("/predict_next_day_roas")
def predict_next_day_roas():
    df = get_latest_feature_row()
    X = df.drop(columns=["metric_date", "target_next_day_roas"])
    X = X[FEATURE_ORDER]
    pred = model.predict(X)[0]
    return {"predicted_next_day_roas": float(pred)}
```

### ✔ It recalculates **every time the page is loaded**  
But…

### ✔ It uses the **latest feature row in BigQuery**  
So the prediction only changes when:
- your ETL pipeline ingests a new day  
- rolling windows update  
- volatility changes  
- spend/conversions change  

This is exactly what you want:
> Dynamic inference, static until new data arrives.

---

# 🧠 **5. ML Feature Engineering**

Your model uses **nine engineered features**:

```python
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
```

These capture:
- daily performance  
- rolling stability  
- volatility  
- trend direction  

---

# 📈 **6. Trend Analytics**

Your trend endpoints expose:

- ROAS trend  
- CAC trend  
- conversions trend  
- spend vs revenue trend  

These are used for:
- seasonality detection  
- performance monitoring  
- anomaly overlays  
- campaign comparison  

---

# 🚨 **7. Anomaly Detection Logic (Technical)**

Your anomaly engine uses multiple detectors:

### **1. Z‑score**
```python
z = (value - mean) / std
```

### **2. Modified Z‑score (MAD)**
More robust for marketing data.

### **3. IQR**
Flags outliers beyond Q1/Q3.

### **4. Rolling deviation**
Compares today vs rolling 7‑day mean.

### **5. Percent‑change**
```python
pct_change = (today - yesterday) / yesterday
```

Alerts include:
- severity  
- deviation magnitude  
- campaign_id  
- metric_date  

---

# 🧩 **8. Last‑Touch Attribution (Technical)**

For each order:
1. Find most recent event for same customer  
2. Within 7‑day lookback  
3. Assign order to that campaign  
4. Compute:
   - spend  
   - attributed revenue  
   - conversions  
   - ROAS  
   - CAC  

This produces daily campaign metrics.

---

# 🖥️ **9. Dashboard Behavior**

The React dashboard:

- fetches `/metrics/summary` on load  
- fetches `/predict_next_day_roas`  
- fetches `/anomalies/roas`  
- fetches `/metrics/trend/*`  
- renders:
  - summary cards  
  - anomaly alerts  
  - trend charts  
  - raw drill‑down tables  

---

# 📄 **10. How to Publish This Documentation**

You can expose this doc directly in your site:

### Option A — Add a `/docs` page in React
Create:
```
frontend/src/pages/Docs.jsx
```

Render this Markdown using:
- `react-markdown`  
- `remark-gfm`  

### Option B — Serve Markdown from FastAPI
Add:
```
GET /docs/master
```

Return the Markdown as text.

### Option C — Link to GitHub `/docs/master.md`

---

# 🎉 **11. You Now Have a Complete Master Document**

This is your authoritative reference for:

- architecture  
- attribution  
- analytics  
- anomaly detection  
- ML prediction  
- dashboard behavior  

If you want, I can generate:

- **a PDF‑ready version**  
- **a React page that renders this doc**  
- **a FastAPI endpoint that serves this doc**  
- **a GitHub‑friendly version with TOC + anchors**

Just tell me what format you want next.