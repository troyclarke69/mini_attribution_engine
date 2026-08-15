import { CartesianGrid, Line, LineChart as RechartsLineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export default function LineChart({ data, color = "#1d6f5c", title = "Value", dataKey = "value", unitLabel, decimals = 0, help }) {
  const formatValue = (value) => (typeof value === "number" ? value.toFixed(decimals) : value);

  return (
    <div className="chart-card">
      <div className="chart-header">
        <strong className="heading-with-help">
          {title}
          {unitLabel ? ` ${unitLabel}` : ""}
          {help}
        </strong>
      </div>
      <div style={{ width: "100%", height: 260 }}>
        <ResponsiveContainer>
          <RechartsLineChart data={data} margin={{ top: 16, right: 16, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#dfe5de" />
            <XAxis dataKey="date" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} tickFormatter={formatValue} />
            <Tooltip formatter={formatValue} />
            <Line type="monotone" dataKey={dataKey} stroke={color} strokeWidth={2.5} dot={{ r: 3 }} activeDot={{ r: 6 }} />
          </RechartsLineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
