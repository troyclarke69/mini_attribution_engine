import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import CampaignTable from "./components/CampaignTable";
import CampaignSelector from "./components/CampaignSelector";
import DateRangePicker from "./components/DateRangePicker";
import SummaryCards from "./components/SummaryCards";
import LineChart from "./components/charts/LineChart";
import DualAxisChart from "./components/charts/DualAxisChart";
import RawTable from "./components/tables/RawTable";
import HelpModal from "./components/HelpModal";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;
const emptySummary = { spend: 0, attributed_revenue: 0, roas: 0, cac: 0, conversions: 0, campaigns: [] };
const rawTabs = [
  { key: "ad-spend", label: "Ad Spend" },
  { key: "orders", label: "Orders" },
  { key: "events", label: "Events" },
  { key: "attribution", label: "Attribution" },
];

function App() {
  const [predictedRoas, setPredictedRoas] = useState(null);
  const [summary, setSummary] = useState(emptySummary);
  const [error, setError] = useState("");
  const [isSummaryLoading, setIsSummaryLoading] = useState(true);
  const [isPredictionLoading, setIsPredictionLoading] = useState(true);
  const [predictionError, setPredictionError] = useState(false);
  const [page, setPage] = useState("overview");
  const [rawTab, setRawTab] = useState("ad-spend");
  const [filters, setFilters] = useState({ campaign_id: "", customer_id: "", date_from: "", date_to: "" });
  const [rawData, setRawData] = useState({ rows: [], count: 0 });
  const [pageIndex, setPageIndex] = useState(0);
  const [trendState, setTrendState] = useState({ campaign_id: "", date_from: "", date_to: "" });
  const [roasData, setRoasData] = useState([]);
  const [cacData, setCacData] = useState([]);
  const [conversionData, setConversionData] = useState([]);
  const [spendRevenueData, setSpendRevenueData] = useState([]);
  const [anomalyAlerts, setAnomalyAlerts] = useState([]);
  const [isChartsLoading, setIsChartsLoading] = useState(false);

  const pageTitle = useMemo(() => ({ overview: "Overview", "raw-data": "Raw Data", charts: "Charts & Trends" }[page]), [page]);

  useEffect(() => {
    axios
      .get(`${apiBaseUrl}/metrics/summary`)
      .then((response) => setSummary(response.data))
      .catch(() => setError("Connect the API to view current attribution metrics."))
      .finally(() => setIsSummaryLoading(false));
  }, []);

  const fetchPrediction = () => {
    setIsPredictionLoading(true);
    setPredictionError(false);
    axios
      .get(`${apiBaseUrl}/predict_next_day_roas`)
      .then((response) => setPredictedRoas(response.data.predicted_next_day_roas))
      .catch(() => setPredictionError(true))
      .finally(() => setIsPredictionLoading(false));
  };

  // Fetched from the "Charts & Trends" tab rather than on initial dashboard
  // load: the model + BigQuery client warm up in the background as soon as
  // the app boots (see api/main.py's lifespan handler), so by the time a
  // visitor actually clicks into this tab there's a much better chance
  // it's already warm - and either way, it no longer blocks or delays the
  // rest of the dashboard.
  useEffect(() => {
    if (page !== "charts") return;
    fetchPrediction();
  }, [page]);

  useEffect(() => {
    if (page !== "raw-data") return;
    const params = new URLSearchParams({ limit: "25", offset: String(pageIndex * 25) });
    if (filters.campaign_id) params.set("campaign_id", filters.campaign_id);
    if (filters.customer_id) params.set("customer_id", filters.customer_id);
    if (filters.date_from) params.set("date_from", filters.date_from);
    if (filters.date_to) params.set("date_to", filters.date_to);

    axios
      .get(`${apiBaseUrl}/raw/${rawTab}?${params.toString()}`)
      .then((response) => setRawData(response.data))
      .catch(() => setRawData({ rows: [], count: 0 }));
  }, [page, rawTab, pageIndex, filters]);

  useEffect(() => {
    if (page !== "charts") return;
    const buildParams = (path) => {
      const params = new URLSearchParams();
      if (trendState.campaign_id) params.set("campaign_id", trendState.campaign_id);
      if (trendState.date_from) params.set("date_from", trendState.date_from);
      if (trendState.date_to) params.set("date_to", trendState.date_to);
      return `${apiBaseUrl}/${path}?${params.toString()}`;
    };

    const anomalyParams = new URLSearchParams();
    if (trendState.campaign_id) anomalyParams.set("campaign_id", trendState.campaign_id);
    if (trendState.date_from) anomalyParams.set("date_from", trendState.date_from);
    if (trendState.date_to) anomalyParams.set("date_to", trendState.date_to);

    setIsChartsLoading(true);
    Promise.all([
      axios.get(buildParams("metrics/trend/roas")),
      axios.get(buildParams("metrics/trend/cac")),
      axios.get(buildParams("metrics/trend/conversions")),
      axios.get(buildParams("metrics/trend/spend-revenue")),
      axios.get(`${apiBaseUrl}/anomalies/roas?${anomalyParams.toString()}`),
    ])
      .then(([roasRes, cacRes, conversionRes, spendRevenueRes, anomaliesRes]) => {
        setRoasData((roasRes.data || []).map((item) => ({ ...item, roas: Number(item.roas) })));
        setCacData((cacRes.data || []).map((item) => ({ ...item, cac: Number(item.cac) })));
        setConversionData((conversionRes.data || []).map((item) => ({ ...item, conversions: Number(item.conversions) })));
        setSpendRevenueData((spendRevenueRes.data || []).map((item) => ({
          ...item,
          spend: Number(item.spend),
          attributed_revenue: Number(item.attributed_revenue),
        })));
        setAnomalyAlerts((anomaliesRes.data || []).slice(-5));
      })
      .catch(() => {
        setRoasData([]);
        setCacData([]);
        setConversionData([]);
        setSpendRevenueData([]);
        setAnomalyAlerts([]);
      })
      .finally(() => {
        setIsChartsLoading(false);
      });
  }, [page, trendState]);

  if (isSummaryLoading) {
    return (
      <main className="shell">
        <div className="startup-loading">
          <div className="spinner" aria-hidden="true" />
          <div>
            <h2>Loading the attribution dashboard…</h2>
            <p>Please wait while we fetch campaign metrics.</p>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="shell">
      <header className="masthead">
        <div>
          <p className="eyebrow">MARKETING INTELLIGENCE</p>
          <h1>Attribution, with receipts.</h1>
          <p className="lede">Last-touch performance across every campaign in one clear view.</p>
        </div>
        <div className="masthead-actions">
          <nav className="nav-pills" aria-label="Main sections">
            <button className={page === "overview" ? "active" : ""} onClick={() => setPage("overview")}>Overview</button>
            <button className={page === "raw-data" ? "active" : ""} onClick={() => setPage("raw-data")}>Raw Data</button>
            <button className={page === "charts" ? "active" : ""} onClick={() => setPage("charts")}>Charts & Trends</button>
          </nav>
          <div className="status"><span /> {error ? "Offline" : "Connected"}</div>
        </div>
      </header>

      {error && <p className="notice">{error}</p>}

      {page === "overview" && (
        <>
          <SummaryCards summary={summary} />
          <section className="campaign-section">
            <div className="section-heading">
              <div>
                <p className="eyebrow">CAMPAIGN LEDGER</p>
                <h2>Where revenue came from</h2>
              </div>
              <span>{summary.conversions} conversions</span>
            </div>
            <CampaignTable campaigns={summary.campaigns} />
          </section>
        </>
      )}

      {page === "raw-data" && (
        <section className="panel">
          <div className="panel-header">
            <div>
              <p className="eyebrow">DRILL-DOWN</p>
              <h2>{pageTitle}</h2>
            </div>
          </div>

          <div className="tabs" aria-label="Raw data tabs">
            {rawTabs.map((tab) => (
              <button key={tab.key} className={rawTab === tab.key ? "tab active" : "tab"} onClick={() => { setRawTab(tab.key); setPageIndex(0); }}>
                {tab.label}
              </button>
            ))}
          </div>

          <div className="filter-bar">
            <CampaignSelector
              value={filters.campaign_id}
              campaigns={summary.campaigns}
              onChange={(campaign_id) => setFilters((current) => ({ ...current, campaign_id }))}
            />
            {rawTab !== "ad-spend" && (
              <label className="field">
                <span>Customer ID</span>
                <input value={filters.customer_id} onChange={(event) => setFilters((current) => ({ ...current, customer_id: event.target.value }))} placeholder="customer-123" />
              </label>
            )}
            <DateRangePicker
              from={filters.date_from}
              to={filters.date_to}
              onFromChange={(date_from) => setFilters((current) => ({ ...current, date_from }))}
              onToChange={(date_to) => setFilters((current) => ({ ...current, date_to }))}
            />
          </div>

          <RawTable
            rows={rawData.rows}
            count={rawData.count}
            pageSize={25}
            page={pageIndex}
            onPageChange={(nextPage) => setPageIndex(nextPage)}
            activeTab={rawTab}
          />
        </section>
      )}

      {page === "charts" && (
        <section className="panel">
          <div className="panel-header">
            <div>
              <p className="eyebrow">TREND ANALYSIS</p>
              <h2>{pageTitle}</h2>
            </div>
          </div>

          <div className="filter-bar charts-bar">
            <CampaignSelector
              value={trendState.campaign_id}
              campaigns={summary.campaigns}
              onChange={(campaign_id) => setTrendState((current) => ({ ...current, campaign_id }))}
            />
            <DateRangePicker
              from={trendState.date_from}
              to={trendState.date_to}
              onFromChange={(date_from) => setTrendState((current) => ({ ...current, date_from }))}
              onToChange={(date_to) => setTrendState((current) => ({ ...current, date_to }))}
            />
          </div>

          <section className="panel">
            <div className="panel-header">
              <div>
                <p className="eyebrow">MODEL OUTPUT</p>
                <h2 className="heading-with-help">
                  Predicted Next-Day ROAS
                  <HelpModal title="How this prediction works">
                    <p>
                      This comes from a RandomForest regression model trained on this
                      project&rsquo;s historical campaign metrics. It takes the most recent
                      day&rsquo;s spend, attributed revenue, conversions, CAC, ROAS, and
                      7-day rolling averages/volatility, and predicts what tomorrow&rsquo;s
                      aggregate ROAS is likely to be.
                    </p>
                    <p>
                      The model is trained offline against past days where the actual
                      next-day outcome is already known - it does not update itself
                      automatically, so its accuracy depends on how recently it was
                      retrained relative to the current data.
                    </p>
                  </HelpModal>
                </h2>
              </div>
            </div>

            <div className="metric-card">
              {isPredictionLoading ? (
                <p className="metric-value">Loading...</p>
              ) : predictionError ? (
                <div className="prediction-error">
                  <p className="notice">Unable to load prediction - retry.</p>
                  <button className="inline-button" onClick={fetchPrediction}>Retry</button>
                </div>
              ) : (
                <p className="metric-value">{predictedRoas !== null ? predictedRoas.toFixed(3) : "—"}</p>
              )}
            </div>
          </section>

          {isChartsLoading ? (
            <div className="panel charts-loading">
              <div className="spinner" aria-hidden="true" />
              <p>Loading charts and anomaly signals...</p>
            </div>
          ) : (
            <>
              <div className="chart-grid">
                <LineChart
                  data={roasData}
                  title="ROAS"
                  dataKey="roas"
                  color="#1d6f5c"
                  unitLabel="(x)"
                  decimals={3}
                  help={
                    <HelpModal title="What ROAS measures">
                      <p>
                        ROAS (Return on Ad Spend) is total attributed revenue divided
                        by total spend, summed across every campaign, for each day. A
                        value of 3 means $3 of attributed revenue for every $1 spent
                        that day - it is a ratio (an &ldquo;x&rdquo; multiplier), not
                        a percentage.
                      </p>
                    </HelpModal>
                  }
                />
                <LineChart
                  data={cacData}
                  title="CAC"
                  dataKey="cac"
                  color="#c77d29"
                  unitLabel="($)"
                  decimals={3}
                  help={
                    <HelpModal title="What CAC measures">
                      <p>
                        CAC (Customer Acquisition Cost) is total spend divided by
                        total conversions, summed across every campaign, for each
                        day - the average cost, in dollars, to acquire one
                        conversion that day.
                      </p>
                    </HelpModal>
                  }
                />
                <LineChart data={conversionData} title="Conversions" dataKey="conversions" color="#2f6dbb" />
                <DualAxisChart data={spendRevenueData} decimals={2} />
              </div>

              <section className="panel anomaly-panel">
                <div className="panel-header">
                  <div>
                    <p className="eyebrow">ANOMALY SUMMARY</p>
                    <h2 className="heading-with-help">
                      Recent ROAS alerts
                      <HelpModal title="How anomaly severity is calculated">
                        <p>
                          For each day, ROAS here is total attributed revenue divided by
                          total spend, summed across every campaign. Each day is then
                          compared against the rest of the visible series using four
                          signals: how many standard deviations it sits from the average
                          (z-score), a more outlier-resistant version of the same idea
                          using the median (modified z-score), whether it falls outside
                          the typical interquartile range, and how much it changed from
                          the previous day.
                        </p>
                        <p>
                          A day is marked HIGH if any signal crosses a strict threshold,
                          MEDIUM if a looser threshold is crossed, and otherwise it is not
                          flagged as notable. Because the baseline stats recalculate from
                          the whole series each time, a sustained trend shift can show up
                          as several flagged days in a row rather than a single spike.
                        </p>
                      </HelpModal>
                    </h2>
                  </div>
                </div>
                <div className="anomaly-list">
                  {anomalyAlerts.length === 0 ? (
                    <p className="empty-state">No recent ROAS anomalies detected.</p>
                  ) : (
                    anomalyAlerts.map((alert) => (
                      <div key={`${alert.date}-${alert.metric}`} className={`anomaly-row severity-${alert.severity}`}>
                        <div>
                          <strong>{alert.date}</strong> • {alert.metric.toUpperCase()} = {alert.value.toFixed(3)}
                        </div>
                        <span className="badge">{alert.severity}</span>
                      </div>
                    ))
                  )}
                </div>
              </section>
            </>
          )}
        </section>
      )}
    </main>
  );
}

export default App;
