import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

function Timelinechat({ data }) {
  // 🔥 Step 1: Group events by hour
  const grouped = {};

  (data || []).forEach((e) => {
    if (!e || !e.timestamp) return;

    const time = String(e.timestamp).slice(11, 13) + ":00";

    if (!grouped[time]) {
      grouped[time] = {
        time,
        FILE: 0,
        BROWSER: 0,
        OTHER: 0,
      };
    }

    if (e.event_type?.startsWith("FILE")) {
      grouped[time].FILE += 1;
    } else if (e.event_type === "BROWSER_VISIT") {
      grouped[time].BROWSER += 1;
    } else {
      grouped[time].OTHER += 1;
    }
  });

  // 🔥 Step 2: Convert & sort
  const chartData = Object.values(grouped).sort((a, b) =>
    a.time.localeCompare(b.time)
  );

  return (
    <div
      id="timeline-graph" // ✅ IMPORTANT (for PDF export)
      style={{
        width: "100%",
        height: "32vh",
        background: "linear-gradient(145deg, #0f172a, #020617)",
        padding: "12px",
        borderRadius: "12px",
        boxShadow: "0 6px 18px rgba(0,0,0,0.4)",
      }}
    >
      {/* TITLE */}
      <div
        style={{
          color: "#cbd5f5",
          fontSize: "13px",
          marginBottom: "6px",
          fontWeight: "500",
        }}
      >
        Event Activity Timeline
      </div>

      <ResponsiveContainer width="100%" height="90%">
        <BarChart data={chartData}>
          {/* X AXIS */}
          <XAxis
            dataKey="time"
            stroke="#94a3b8"
            tick={{ fontSize: 11 }}
          />

          {/* Y AXIS */}
          <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} />

          {/* TOOLTIP */}
          <Tooltip
            contentStyle={{
              backgroundColor: "#020617",
              border: "1px solid #1e293b",
              borderRadius: "8px",
              color: "#fff",
            }}
            labelStyle={{ color: "#38bdf8" }}
          />

          {/* LEGEND */}
          <Legend
            wrapperStyle={{
              fontSize: "12px",
              color: "#cbd5f5",
            }}
          />

          {/* BARS */}
          <Bar
            dataKey="FILE"
            stackId="a"
            fill="#38bdf8"
            radius={[4, 4, 0, 0]}
          />

          <Bar
            dataKey="BROWSER"
            stackId="a"
            fill="#60a5fa"
            radius={[4, 4, 0, 0]}
          />

          <Bar
            dataKey="OTHER"
            stackId="a"
            fill="#64748b"
            radius={[4, 4, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default Timelinechat;