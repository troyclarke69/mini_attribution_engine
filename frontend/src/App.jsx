import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import CampaignTable from "./components/CampaignTable";
import CampaignSelector from "./components/CampaignSelector";
import DateRangePicker from "./components/DateRangePicker";
import SummaryCards from "./components/SummaryCards";
import LineChart from "./components/charts/LineChart";
import DualAxisChart from "./components/charts/DualAxisChart";
import RawTable from "./components/tables/RawTable";

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

  useEffect(() => {
    axios
      .get(`${apiBaseUrl}/predict_next_day_roas`)
      .then((response) => setPredictedRoas(response.data.predicted_next_day_roas))
      .catch(() => setPredictedRoas(null))
      .finally(() => setIsPredictionLoading(false));
  }, []);

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

  if (isSummaryLoading || isPredictionLoading) {
    return (
      <main className="shell">
        <div className="startup-loading">
          <div className="spinner" aria-hidden="true" />
          <div>
            <h2>Loading the attribution dashboard…</h2>
            <p>Please wait while we fetch campaign metrics and model output.</p>
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
          <section className="panel">
            <div className="panel-header">
              <div>
                <p className="eyebrow">MODEL OUTPUT</p>
                <h2>Predicted Next-Day ROAS</h2>
              </div>
            </div>

            <div className="metric-card">
              <p className="metric-value">
                {predictedRoas !== null ? predictedRoas.toFixed(3) : "Loading..."}
              </p>
            </div>
          </section>
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

          {isChartsLoading ? (
            <div className="panel charts-loading">
              <div className="spinner" aria-hidden="true" />
              <p>Loading charts and anomaly signals...</p>
            </div>
          ) : (
            <>
              <div className="chart-grid">
                <LineChart data={roasData} title="ROAS" dataKey="roas" color="#1d6f5c" />
                <LineChart data={cacData} title="CAC" dataKey="cac" color="#c77d29" />
                <LineChart data={conversionData} title="Conversions" dataKey="conversions" color="#2f6dbb" />
                <DualAxisChart data={spendRevenueData} />
              </div>

              <section className="panel anomaly-panel">
                <div className="panel-header">
                  <div>
                    <p className="eyebrow">ANOMALY SUMMARY</p>
                    <h2>Recent ROAS alerts</h2>
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
