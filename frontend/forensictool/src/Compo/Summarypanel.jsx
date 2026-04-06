import { useState } from "react";
import { useLocation } from "react-router-dom";

function Summarypanel() {
  const location = useLocation();
  const data = location.state || {};

  const alerts = data.alerts || [];
  const overview = data.overview || {};

  const [selectedAlert, setSelectedAlert] = useState(null);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [loading, setLoading] = useState(false);

  const downloadSummaryPDF = async () => {
    try {
      setLoading(true);

      const response = await fetch("http://127.0.0.1:8000/export_summary_pdf/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          case_id: data.case_id,
          alerts,
          overview,
        }),
      });

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "forensic_report.pdf";
      a.click();
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (risk) => {
    if (risk === "HIGH") return "#ef4444";
    if (risk === "MEDIUM") return "#f59e0b";
    return "#22c55e";
  };

  return (
    <div style={container}>
      {/* HEADER */}
      <div style={header}>
        <div>
          <h1 style={{ margin: 0 }}>🔍 AI Forensic Dashboard</h1>
          <p style={{ color: "#94a3b8" }}>
            Analyze alerts and investigate suspicious activity
          </p>
        </div>

        <button style={downloadBtn} onClick={downloadSummaryPDF}>
          {loading ? "Generating..." : "Download Report"}
        </button>
      </div>

      {/* STATS */}
      <div style={stats}>
        <Stat title="Events" value={overview.total_events} />
        <Stat title="Suspicious" value={overview.suspicious_events} />
        <Stat title="Alerts" value={overview.total_alerts} />
        <Stat title="High Risk" value={overview.high_risk_alerts} />
      </div>

      {/* MAIN */}
      <div style={layout}>

        {/* ALERT LIST */}
        <div style={left}>
          <h3>Alerts</h3>

          {alerts.map((a, i) => (
            <div
              key={i}
              style={{
                ...alertCard,
                borderLeft: `4px solid ${getRiskColor(a.risk)}`,
                ...(selectedAlert === a && selected),
              }}
              onClick={() => {
                setSelectedAlert(a);
                setSelectedEvent(null);
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <b>{a.type}</b>
                <span style={badge(a.risk)}>{a.risk}</span>
              </div>

              <p style={{ fontSize: 13 }}>{a.explanation}</p>
            </div>
          ))}
        </div>

        {/* DETAILS */}
        <div style={right}>
          {!selectedAlert ? (
            <div style={empty}>Select an alert</div>
          ) : (
            <>
              {/* SUMMARY */}
              <div style={card}>
                <h3>Alert Summary</h3>
                <Info label="Risk" value={selectedAlert.risk} />
                <Info label="Explanation" value={selectedAlert.explanation} />
              </div>

              {/* TIMELINE */}
              <div style={card}>
                <h3>Timeline</h3>

                {selectedAlert.sequence.map((e) => (
                  <div
                    key={e.event_id}
                    style={{
                      ...timeline,
                      borderLeft: `3px solid ${
                        e.suspicious ? "#ef4444" : "#22c55e"
                      }`,
                    }}
                    onClick={() => setSelectedEvent(e)}
                  >
                    <b>{e.event_type}</b>
                    <small>
                      {new Date(e.timestamp).toLocaleString()}
                    </small>
                  </div>
                ))}
              </div>

              {/* EVENT DETAILS */}
              {selectedEvent && (
                <div style={card}>
                  <h3>Event Details</h3>
                  <Info label="File" value={selectedEvent.file_name} />
                  <Info label="Source" value={selectedEvent.source} />
                  <Info label="Path" value={selectedEvent.details} />
                  <Info label="Severity" value={selectedEvent.severity} />
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

/* COMPONENTS */
const Stat = ({ title, value }) => (
  <div style={stat}>
    <p>{title}</p>
    <h2>{value || 0}</h2>
  </div>
);

const Info = ({ label, value }) => (
  <div style={info}>
    <span>{label}</span>
    <span>{value}</span>
  </div>
);

/* STYLES */
const container = {
  padding: 20,
  background: "linear-gradient(135deg, #0f172a, #020617)",
  color: "white",
  minHeight: "100vh",
};

const header = {
  display: "flex",
  justifyContent: "space-between",
  marginBottom: 20,
};

const stats = {
  display: "grid",
  gridTemplateColumns: "repeat(4,1fr)",
  gap: 15,
  marginBottom: 20,
};

const stat = {
  background: "#111827",
  padding: 15,
  borderRadius: 12,
  textAlign: "center",
  boxShadow: "0 0 10px rgba(0,0,0,0.5)",
};

const layout = { display: "flex", gap: 20 };

const left = { width: "30%" };
const right = { width: "70%", display: "flex", flexDirection: "column", gap: 15 };

const alertCard = {
  background: "#111827",
  padding: 12,
  borderRadius: 10,
  marginBottom: 10,
  cursor: "pointer",
  transition: "0.2s",
};

const selected = {
  background: "#1e293b",
  transform: "scale(1.02)",
};

const badge = (risk) => ({
  background:
    risk === "HIGH" ? "#ef4444" : risk === "MEDIUM" ? "#f59e0b" : "#22c55e",
  padding: "2px 6px",
  borderRadius: 6,
  fontSize: 10,
});

const card = {
  background: "#111827",
  padding: 15,
  borderRadius: 12,
  boxShadow: "0 0 10px rgba(0,0,0,0.4)",
};

const timeline = {
  padding: 10,
  marginBottom: 10,
  background: "#020617",
  borderRadius: 8,
  cursor: "pointer",
};

const info = {
  display: "flex",
  justifyContent: "space-between",
  padding: "5px 0",
};

const empty = {
  textAlign: "center",
  marginTop: 50,
  color: "#94a3b8",
};

const downloadBtn = {
  background: "#3b82f6",
  padding: "10px 15px",
  borderRadius: 8,
  border: "none",
  color: "white",
  cursor: "pointer",
};

export default Summarypanel;