Absolutely, Troy — here’s a clean, professional **Markdown document** you can drop directly into `/docs/model_roas.md`.  
I’ll also explain **exactly what “conversion” means** in your analytics context.

For the **downloadable PDF**, I’ll prepare the full content in a format ready for export — you can paste it into any PDF generator (VS Code → “Markdown PDF”, GitHub → “Download PDF”, or your build pipeline).

---

# 📘 **ROAS Prediction & Attribution Analytics — Technical Documentation**

## 🏷️ Overview
This document explains how the **Predicted Next‑Day ROAS** model works, how ROAS and CAC are calculated, and how daily marketing performance metrics flow through the attribution engine.

It is intended for:
- Data engineers  
- ML engineers  
- Marketing analysts  
- Stakeholders reviewing model behavior  

---

# 📦 **1. Data Pipeline Overview**

## 1.1 Source Data (BigQuery)
All training and prediction features come from:

```
fact_campaign_metrics_features
```

This table contains daily marketing performance metrics including:
- Spend  
- Conversions  
- Revenue  
- Rolling 7‑day aggregates  
- Next‑day ROAS (the prediction target)

---

# 🧮 **2. Key Metrics**

## 2.1 ROAS (Return on Ad Spend)
**Formula:**

\[
\text{ROAS} = \frac{\text{Attributed Revenue}}{\text{Spend}}
\]

**Interpretation:**
- ROAS = 4.0 → every $1 spent produced $4 in revenue  
- Higher is better  
- ROAS is volatile day‑to‑day, so rolling averages are used

---

## 2.2 CAC (Customer Acquisition Cost)
**Formula:**

\[
\text{CAC} = \frac{\text{Spend}}{\text{Conversions}}
\]

**Interpretation:**
- CAC = $25 → it costs $25 to acquire one conversion  
- Lower is better  
- CAC spikes when spend increases or conversions drop

---

## 2.3 What is a “Conversion”?
A **conversion** is any event that represents a successful outcome of your marketing funnel.

In your attribution engine, a conversion is:

> **A completed purchase event attributed to a campaign.**

This comes from your `orders` and `events` tables and is joined into the daily metrics.

Examples:
- A customer completes checkout  
- A subscription is purchased  
- A lead becomes a paying customer  

Conversions are the backbone of CAC and ROAS analytics.

---

# 🔢 **3. Prediction Target**

The model predicts:

\[
\text{target\_next\_day\_roas}
\]

This is the ROAS observed **the day after** the feature row.

---

# 🧠 **4. Model Inputs (Features)**

The model uses **nine numeric features**, in the exact order learned during training:

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

### Feature Definitions

| Feature | Description |
|--------|-------------|
| **spend** | Total ad spend for the day |
| **attributed_revenue** | Revenue attributed to campaigns |
| **conversions** | Number of successful conversion events |
| **cac** | Cost per acquisition |
| **roas** | Daily return on ad spend |
| **rolling_7d_roas** | 7‑day average ROAS |
| **rolling_7d_spend** | 7‑day total spend |
| **rolling_7d_conversions** | 7‑day total conversions |
| **rolling_7d_volatility** | Standard deviation of daily ROAS over 7 days |

---

# 🏗️ **5. Model Architecture**

The model is a **RandomForestRegressor**:

```python
RandomForestRegressor(
    n_estimators=200,
    max_depth=12,
    random_state=42
)
```

Why Random Forest?
- Handles nonlinear relationships  
- Robust to noisy marketing data  
- Works well with small‑to‑medium datasets  
- Provides feature importance for transparency  

---

# 📈 **6. Feature Importance**

| Feature | Importance |
|--------|------------|
| rolling_7d_volatility | 0.4676 |
| spend | 0.2507 |
| cac | 0.0981 |
| attributed_revenue | 0.0636 |
| rolling_7d_conversions | 0.0379 |
| conversions | 0.0307 |
| roas | 0.0232 |
| rolling_7d_roas | 0.0201 |
| rolling_7d_spend | 0.0082 |

**Interpretation:**
- Volatility is the strongest predictor  
- Spend is the second strongest  
- CAC and attributed revenue also matter  
- Rolling aggregates stabilize predictions  

---

# 🔮 **7. Prediction Flow (FastAPI)**

### Step‑by‑step:

1. FastAPI loads model:
   ```python
   model = joblib.load("ml/model_roas.pkl")
   ```

2. Fetch latest feature row:
   ```python
   df = get_latest_feature_row()
   ```

3. Drop non‑features:
   ```python
   X = df.drop(columns=["metric_date", "target_next_day_roas"])
   ```

4. Enforce feature order:
   ```python
   X = X[FEATURE_ORDER]
   ```

5. Predict:
   ```python
   pred = model.predict(X)[0]
   ```

6. Return JSON:
   ```json
   {"predicted_next_day_roas": 4.433}
   ```

---

# 🖥️ **8. Dashboard Integration**

React fetches prediction:

```javascript
fetch(`${apiBaseUrl}/predict_next_day_roas`)
  .then(res => res.json())
  .then(data => setPredictedRoas(data.predicted_next_day_roas));
```

Displayed in the Overview panel.

---

# 📄 **9. PDF Version (Ready for Export)**

Copy/paste this entire Markdown into:

- VS Code → Command Palette → “Markdown PDF: Export”
- GitHub → “Download PDF”
- Any Markdown → PDF converter

This produces a clean, professional PDF with:
- Technical details  
- User‑facing explanations  
- Formulas  
- Tables  
- Architecture overview  

