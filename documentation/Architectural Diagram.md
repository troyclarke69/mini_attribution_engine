# 📐 **System Architecture Diagram**

## **High‑Level Architecture Overview**

```
                         ┌──────────────────────────────┐
                         │          BigQuery             │
                         │  fact_campaign_metrics_*      │
                         │  (raw + enriched features)    │
                         └───────────────┬──────────────┘
                                         │
                                         │ 1. Daily ETL
                                         ▼
                         ┌──────────────────────────────┐
                         │            ETL Layer          │
                         │  - bq_extract_training_data   │
                         │  - data_loader (training +    │
                         │    latest feature row)        │
                         └───────────────┬──────────────┘
                                         │
                                         │ 2. Training DataFrame
                                         ▼
                         ┌──────────────────────────────┐
                         │        ML Training Pipeline   │
                         │  - train_roas_model.py        │
                         │  - RandomForestRegressor      │
                         │  - Feature engineering         │
                         │  - Model evaluation            │
                         └───────────────┬──────────────┘
                                         │
                                         │ 3. Model Artifact (.pkl)
                                         ▼
                         ┌──────────────────────────────┐
                         │        Model Registry         │
                         │     ml/model_roas.pkl         │
                         └───────────────┬──────────────┘
                                         │
                                         │ 4. Load model at startup
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                           FastAPI Backend (API)                              │
│                                                                              │
│  Routes:                                                                     │
│   - /metrics/* (summary, trends, raw data)                                   │
│   - /predict_next_day_roas  ← ML inference endpoint                          │
│                                                                              │
│  Components:                                                                 │
│   - Loads model_roas.pkl                                                     │
│   - Calls get_latest_feature_row()                                           │
│   - Enforces FEATURE_ORDER                                                   │
│   - Returns JSON prediction                                                  │
└───────────────────────────────┬──────────────────────────────────────────────┘
                                │
                                │ 5. JSON API Response
                                ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                           React Dashboard (UI)                               │
│                                                                              │
│  Panels:                                                                     │
│   - Overview (SummaryCards + Predicted ROAS card)                            │
│   - Raw Data (tables)                                                        │
│   - Charts & Trends (ROAS, CAC, conversions, spend/revenue)                  │
│                                                                              │
│  Behavior:                                                                   │
│   - Fetches /metrics/summary on load                                         │
│   - Fetches /predict_next_day_roas for ML output                             │
│   - Renders prediction in “Model Output” card                                │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

# 🧩 **Component Breakdown**

## **1. BigQuery**
- Stores raw marketing data  
- Stores enriched daily metrics  
- Stores rolling 7‑day aggregates  
- Provides training + inference features  

**Tables used:**
- `fact_campaign_metrics_features`  
- `ad_spend`  
- `orders`  
- `events`  

---

## **2. ETL Layer**
- Extracts daily metrics  
- Cleans NaNs  
- Renames `next_day_roas → target_next_day_roas`  
- Produces training DataFrame  
- Produces latest feature row for inference  

---

## **3. ML Training Pipeline**
- RandomForestRegressor  
- 9 engineered features  
- Feature importance inspection  
- Model saved as `model_roas.pkl`  

---

## **4. FastAPI Backend**
- Loads model at startup  
- Exposes `/predict_next_day_roas`  
- Enforces feature order  
- Returns prediction as JSON  

---

## **5. React Dashboard**
- Displays attribution metrics  
- Displays ROAS/CAC trends  
- Displays predicted next‑day ROAS  

---

# 📄 **PDF‑Ready Version**

You can export this Markdown directly to PDF using:

- VS Code → “Markdown PDF: Export”
- GitHub → “Download PDF”
- Any Markdown → PDF converter
