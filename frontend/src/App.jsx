import { useEffect, useState } from "react";
import CampaignTable from "./components/CampaignTable";
import SummaryCards from "./components/SummaryCards";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const emptySummary = { spend: 0, attributed_revenue: 0, roas: 0, cac: 0, conversions: 0, campaigns: [] };

export default function App() {
  const [summary, setSummary] = useState(emptySummary);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${apiBaseUrl}/metrics/summary`)
      .then((response) => {
        if (!response.ok) throw new Error("Metrics unavailable");
        return response.json();
      })
      .then(setSummary)
      .catch(() => setError("Connect the API to view current attribution metrics."));
  }, []);

  return (
    <main className="shell">
      <header className="masthead">
        <div>
          <p className="eyebrow">MARKETING INTELLIGENCE / LIVE MODEL</p>
          <h1>Attribution, with receipts.</h1>
          <p className="lede">Last-touch performance across every campaign in one clear view.</p>
        </div>
        <div className="status"><span /> {error ? "Offline" : "Connected"}</div>
      </header>
      {error && <p className="notice">{error}</p>}
      <SummaryCards summary={summary} />
      <section className="campaign-section">
        <div className="section-heading"><div><p className="eyebrow">CAMPAIGN LEDGER</p><h2>Where revenue came from</h2></div><span>{summary.conversions} conversions</span></div>
        <CampaignTable campaigns={summary.campaigns} />
      </section>
    </main>
  );
}
