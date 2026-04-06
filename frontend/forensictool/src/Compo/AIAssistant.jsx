import React, { useState } from "react";
import Lottie from "lottie-react";
import robot from "./robot.json";
import { useNavigate } from "react-router-dom";

function AIAssistant() {
  const [open, setOpen] = useState(false);
  const [alerts, setAlerts] = useState([]);
  const [aiMessage, setAiMessage] = useState("Click to analyze activity");
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  // =========================
  // 🔥 API CALL (WITH CASE ID)
  // =========================
  const callAPI = async () => {
    const caseId = localStorage.getItem("case_id");

    if (!caseId) {
      throw new Error("NO_CASE");
    }

    const res = await fetch(
      `http://127.0.0.1:8000/summary/?case_id=${caseId}`
    );

    if (!res.ok) throw new Error("API_ERROR");

    return res.json();
  };

  // =========================
  // 🔥 SCAN LOGIC
  // =========================
  const handleScan = async () => {
    try {
      setLoading(true);

      const data = await callAPI();

      const fetchedAlerts = data.alerts || [];
      setAlerts(fetchedAlerts);

      if (fetchedAlerts.length > 0) {
        setAiMessage(
          `⚠️ ${fetchedAlerts.length} suspicious activity detected. Click to investigate`
        );
      } else {
        setAiMessage("🟢 No suspicious activity found");
      }

      navigate("/summary", {
        state: {
          overview: data.overview,
          alerts: fetchedAlerts,
          timeline: data.timeline
        }
      });

    } catch (err) {

      if (err.message === "NO_CASE") {
        setAiMessage("⚠ Please start investigation first");
      } else {
        setAiMessage("❌ Scan failed");
      }

    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* 🤖 FLOATING ROBOT */}
      <div
        onClick={() => setOpen(!open)}
        style={{
          position: "fixed",
          bottom: "25px",
          right: "25px",
          width: "120px",
          height: "120px",
          cursor: "pointer",
          zIndex: 1001,
          filter:
            alerts.length > 0
              ? "drop-shadow(0 0 25px #ef4444)"
              : "drop-shadow(0 0 10px rgba(59,130,246,0.5))",
          transition: "0.3s"
        }}
      >
        <Lottie animationData={robot} loop />
      </div>

      {/* 📌 PANEL */}
      {open && (
        <div
          style={panelStyle}
          onClick={(e) => e.stopPropagation()}
        >
          {/* HEADER */}
          <div style={header}>
            <div style={miniRobot}>
              <Lottie animationData={robot} loop />
            </div>

            <div>
              <h4 style={{ margin: 0 }}>AI Assistant</h4>
              <small style={subText}>Forensic Analysis</small>
            </div>

            <button onClick={() => setOpen(false)} style={closeBtn}>
              ✕
            </button>
          </div>

          <hr style={divider} />

          {/* CONTENT */}
          <div style={contentArea}>

            {/* STATUS */}
            <div>
              <b>Status</b>
              <p style={{ fontSize: "13px" }}>{aiMessage}</p>
            </div>

            <hr style={divider} />

            {/* ALERTS */}
            <div>
              <b>Alerts</b>

              {alerts.length === 0 ? (
                <p style={{ color: "#94a3b8" }}>No alerts</p>
              ) : (
                alerts.map((a, i) => (
                  <div
                    key={i}
                    style={alertBox}
                    onClick={() =>
                      navigate("/summary", {
                        state: {
                          alertDetails: a,
                          alerts: alerts
                        }
                      })
                    }
                  >
                    {/* 🔥 FIXED: SHOW TYPE + RISK */}
                    <p style={{ margin: 0 }}>
                      <b>{a.type}</b> ({a.risk})
                    </p>

                    {/* 🔥 FIXED: EXPLANATION */}
                    <p style={{ fontSize: "12px" }}>
                      {(a.explanation || a.message || "").slice(0, 60)}...
                    </p>
                  </div>
                ))
              )}
            </div>

          </div>

          <hr style={divider} />

          {/* BUTTON */}
          <button style={btn} onClick={handleScan}>
            {loading ? "Analyzing..." : "Run Scan"}
          </button>

        </div>
      )}
    </>
  );
}

/* ========================= STYLES (UNCHANGED) ========================= */

const panelStyle = {
  position: "fixed",
  bottom: "150px",
  right: "25px",
  width: "300px",
  height: "420px",
  background: "#020617",
  color: "white",
  padding: "12px",
  borderRadius: "12px",
  border: "1px solid rgba(255,255,255,0.1)",
  zIndex: 1000,
  boxShadow: "0 10px 30px rgba(0,0,0,0.6)",
  display: "flex",
  flexDirection: "column"
};

const contentArea = {
  flex: 1,
  overflowY: "auto"
};

const header = {
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between"
};

const miniRobot = {
  width: "40px",
  height: "40px"
};

const subText = {
  fontSize: "11px",
  color: "#94a3b8"
};

const closeBtn = {
  background: "none",
  border: "none",
  color: "white",
  cursor: "pointer",
  fontSize: "14px"
};

const divider = {
  border: "none",
  borderTop: "1px solid rgba(255,255,255,0.1)",
  margin: "8px 0"
};

const alertBox = {
  padding: "8px",
  borderRadius: "6px",
  background: "rgba(255,255,255,0.03)",
  marginBottom: "6px",
  cursor: "pointer"
};

const btn = {
  width: "100%",
  padding: "8px",
  borderRadius: "6px",
  border: "none",
  background: "#1e293b",
  color: "white",
  cursor: "pointer"
};

export default AIAssistant;