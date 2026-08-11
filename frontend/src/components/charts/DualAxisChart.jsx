import { CartesianGrid, Legend, Line, LineChart as RechartsLineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export default function DualAxisChart({ data }) {
  return (
    <div className="chart-card">
      <div className="chart-header">
        <strong>Spend vs Revenue</strong>
      </div>
      <div style={{ width: "100%", height: 260 }}>
        <ResponsiveContainer>
          <RechartsLineChart data={data} margin={{ top: 16, right: 18, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#dfe5de" />
            <XAxis dataKey="date" tick={{ fontSize: 11 }} />
            <YAxis yAxisId="left" tick={{ fontSize: 11 }} />
            <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 11 }} />
            <Tooltip />
            <Legend />
            <Line yAxisId="left" type="monotone" dataKey="spend" stroke="#ff8a3c" strokeWidth={2.5} />
            <Line yAxisId="right" type="monotone" dataKey="attributed_revenue" stroke="#1d6f5c" strokeWidth={2.5} />
          </RechartsLineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
