import { CartesianGrid, Line, LineChart as RechartsLineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export default function LineChart({ data, color = "#1d6f5c", title = "Value", dataKey = "value" }) {
  return (
    <div className="chart-card">
      <div className="chart-header">
        <strong>{title}</strong>
      </div>
      <div style={{ width: "100%", height: 260 }}>
        <ResponsiveContainer>
          <RechartsLineChart data={data} margin={{ top: 16, right: 16, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#dfe5de" />
            <XAxis dataKey="date" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip />
            <Line type="monotone" dataKey={dataKey} stroke={color} strokeWidth={2.5} dot={{ r: 3 }} activeDot={{ r: 6 }} />
          </RechartsLineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
