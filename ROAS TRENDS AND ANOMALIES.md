# 🧠 **MASTER PROMPT #1 — ROAS Trend Modeling & Time‑Series Intelligence**

> **You are an expert ML engineer, data scientist, and attribution architect.  
Your task is to design and implement a complete ROAS trend analysis system for a marketing attribution engine.  
Follow these instructions precisely:**
>
> ### **1. Data Understanding**
> - Assume daily marketing metrics exist in BigQuery:  
>   `metric_date, spend, conversions, attributed_revenue, roas, cac, rolling_7d_* fields`.
> - Explain the statistical meaning of ROAS trends, CAC trends, volatility, seasonality, and lag effects.
>
> ### **2. Time‑Series Feature Engineering**
> Produce code + explanation for:
> - Rolling windows (7d, 14d, 30d)
> - Lag features (t‑1, t‑2, t‑7)
> - Volatility measures (stddev, MAD)
> - Trend decomposition (level, slope)
> - Smoothing (EMA, Holt‑Winters)
>
> ### **3. Trend Analytics**
> Generate:
> - ROAS trend charts  
> - CAC trend charts  
> - Spend vs revenue dual‑axis charts  
> - Trend summaries (increasing, decreasing, stable)
> - Statistical anomaly flags (z‑score, IQR, rolling deviation)
>
> ### **4. ML Forecasting**
> Provide code + reasoning for:
> - Prophet  
> - ARIMA  
> - RandomForestRegressor time‑series variant  
> - Feature importance for trend drivers  
>
> ### **5. Dashboard Integration**
> Produce:
> - API endpoints  
> - JSON response formats  
> - React components  
> - Chart.js / Recharts configs  
>
> ### **6. Deliverables**
> - Full code  
> - Full architecture  
> - Full explanation  
> - Full reasoning  
> - No placeholders  
>
> **Your output must be deeply technical, production‑ready, and structured.**

-----------------------------------------------------------------------------------

# 🚨 **MASTER PROMPT #2 — Anomaly Detection for ROAS, CAC, Spend, Conversions**

> **You are an expert ML engineer specializing in anomaly detection for marketing analytics.  
Your task is to design and implement a complete anomaly detection system for ROAS, CAC, spend, conversions, and revenue.  
Follow these instructions precisely:**
>
> ### **1. Data Understanding**
> - Assume daily metrics exist with rolling windows and volatility fields.
> - Explain what constitutes an anomaly in ROAS, CAC, spend, conversions.
>
> ### **2. Statistical Anomaly Detection**
> Provide code + explanation for:
> - Z‑score anomaly detection  
> - Modified z‑score (MAD)  
> - IQR outlier detection  
> - Rolling deviation thresholds  
> - Percent‑change anomaly detection  
>
> ### **3. ML‑Based Anomaly Detection**
> Provide code + reasoning for:
> - Isolation Forest  
> - One‑Class SVM  
> - Autoencoder anomaly scoring  
> - RandomForest anomaly classification  
>
> ### **4. Alerting Logic**
> Produce:
> - Severity scoring (low/medium/high)  
> - Alert thresholds  
> - Alert aggregation  
> - Daily anomaly summary  
>
> ### **5. API Integration**
> Produce:
> - `/anomalies/roas` endpoint  
> - `/anomalies/cac` endpoint  
> - JSON schema for alerts  
>
> ### **6. Dashboard Integration**
> Produce:
> - React alert components  
> - Color‑coded severity badges  
> - Trend overlays showing anomaly points  
>
> ### **7. Deliverables**
> - Full code  
> - Full architecture  
> - Full explanation  
> - Full reasoning  
> - No placeholders  
>
> **Your output must be deeply technical, production‑ready, and structured.**
