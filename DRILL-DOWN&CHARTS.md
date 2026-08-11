# ⭐ **Phase One: Drill‑Down + Charts Expansion**

> **Goal:** Extend the existing marketing analytics app by adding raw‑data drill‑down capabilities and chart‑based visualizations. Maintain the current architecture (Airflow → BigQuery → FastAPI → React UI). Add new FastAPI endpoints, new BigQuery queries, and new React components/pages to support drill‑down browsing and time‑series charts for campaign performance.

---

## 1. **General Requirements**
- Keep the existing attribution pipeline intact.
- Add new FastAPI routes without breaking existing ones.
- Add new React pages/tabs for drill‑down and charts.
- Use BigQuery SQL files where appropriate.
- Keep everything free‑tier friendly (partitioning optional).
- Maintain clean modular structure:
  - `api/routes/`
  - `api/services/`
  - `ui/src/pages/`
  - `ui/src/components/charts/`
  - `ui/src/components/tables/`

---

## 2. **New FastAPI Endpoints (Drill‑Down)**
Create four new endpoints that expose raw data with pagination, filtering, and sorting:

### **2.1 Raw Ad Spend**
`GET /raw/ad-spend`
- Query BigQuery table `fact_ad_spend`
- Filters:
  - `campaign_id`
  - `date_from`, `date_to`
- Pagination:
  - `limit`, `offset`
- Sorting:
  - `order_by` (date, spend)

### **2.2 Raw Orders**
`GET /raw/orders`
- Query `fact_orders`
- Filters:
  - `customer_id`
  - `date_from`, `date_to`
- Pagination + sorting

### **2.3 Raw Events**
`GET /raw/events`
- Query `fact_events`
- Filters:
  - `campaign_id`
  - `customer_id`
  - `date_from`, `date_to`
- Pagination + sorting

### **2.4 Raw Attribution Rows**
`GET /raw/attribution`
- Query `fact_attribution`
- Filters:
  - `campaign_id`
  - `touch_date_from`, `touch_date_to`
- Pagination + sorting

### **Endpoint Requirements**
- Return JSON arrays of rows.
- Use BigQuery parameterized queries.
- Convert datetime fields to ISO strings.
- Include total count for pagination.

---

## 3. **New FastAPI Endpoints (Charts / Time‑Series Metrics)**

### **3.1 ROAS Trend**
`GET /metrics/trend/roas`
- Query daily ROAS from `campaign_metrics`
- Filters:
  - `campaign_id`
  - `date_from`, `date_to`
- Return:
  - `date`
  - `roas`

### **3.2 CAC Trend**
`GET /metrics/trend/cac`
- Query daily CAC
- Same filters

### **3.3 Conversion Trend**
`GET /metrics/trend/conversions`
- Query daily conversions

### **3.4 Spend vs Revenue Trend**
`GET /metrics/trend/spend-revenue`
- Query:
  - `date`
  - `spend`
  - `attributed_revenue`

### **Endpoint Requirements**
- Return arrays sorted by date.
- Use BigQuery SQL with GROUP BY date.
- Convert timestamps to ISO strings.

---

## 4. **React UI Additions**

### **4.1 New Pages**
Add two new top‑level pages:

#### **Page: “Raw Data”**
Tabs:
- Ad Spend
- Orders
- Events
- Attribution

Each tab:
- Table view
- Pagination controls
- Filters (campaign, date range)
- “View details” modal for row inspection

#### **Page: “Charts & Trends”**
Charts:
- ROAS line chart
- CAC line chart
- Conversions line chart
- Spend vs Revenue dual‑axis chart

Interactions:
- Campaign selector dropdown
- Date range selector
- Hover tooltips
- Click a point → open raw data for that date

### **4.2 Components**
- `Charts/LineChart.tsx`
- `Charts/DualAxisChart.tsx`
- `Tables/RawTable.tsx`
- `Filters/DateRangePicker.tsx`
- `Filters/CampaignSelector.tsx`

Use:
- Recharts or Chart.js (your choice)
- Axios for API calls

---

## 5. **BigQuery SQL Requirements**
Create SQL files for each trend query:

- `sql/trend_roas.sql`
- `sql/trend_cac.sql`
- `sql/trend_conversions.sql`
- `sql/trend_spend_revenue.sql`

Each file:
- SELECT date, metric
- GROUP BY date
- ORDER BY date

---

## 6. **Testing Requirements**
- Add unit tests for FastAPI endpoints.
- Add integration tests for BigQuery queries.
- Add UI smoke tests for charts and tables.

---

## 7. **Non‑Functional Requirements**
- Keep endpoints fast (<200ms typical).
- Use BigQuery’s `LIMIT` + `OFFSET` for pagination.
- Ensure UI handles empty states gracefully.
- Maintain consistent naming conventions.

---

## 8. **Deliverables**
- New FastAPI routes + services
- New SQL files
- New React pages + components
- Updated navigation
- Documentation for all endpoints
- Screenshots of charts and drill‑down tables

---

## 9. **Style & Structure**
- Clean modular code
- Senior‑level naming conventions
- Clear separation of concerns
- Reusable chart + table components
- Avoid duplication in SQL
