export default function DateRangePicker({ from, to, onFromChange, onToChange }) {
  return (
    <div className="date-range">
      <label className="field">
        <span>From</span>
        <input type="date" value={from} onChange={(event) => onFromChange(event.target.value)} />
      </label>
      <label className="field">
        <span>To</span>
        <input type="date" value={to} onChange={(event) => onToChange(event.target.value)} />
      </label>
    </div>
  );
}
