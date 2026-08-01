export default function SummaryCards({ summary }) {
  const cards = [
    ["Spend", `$${summary.spend.toLocaleString(undefined, { maximumFractionDigits: 0 })}`],
    ["Attributed revenue", `$${summary.attributed_revenue.toLocaleString(undefined, { maximumFractionDigits: 0 })}`],
    ["ROAS", `${summary.roas.toFixed(2)}x`],
    ["CAC", `$${summary.cac.toFixed(2)}`],
  ];

  return (
    <section className="summary-grid" aria-label="Performance summary">
      {cards.map(([label, value]) => (
        <article className="summary-card" key={label}>
          <span>{label}</span>
          <strong>{value}</strong>
        </article>
      ))}
    </section>
  );
}
