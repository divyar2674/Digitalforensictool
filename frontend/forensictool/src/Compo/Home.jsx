import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

function Home({ setCaseId }) {
  const [input, setInput] = useState("");
  const navigate = useNavigate();

  const loadCase = () => {
    if (!input) return;

    localStorage.setItem("case_id", input);
    setCaseId(input);
    navigate("/Timeline");
  };

  const startNew = () => {
    localStorage.removeItem("case_id");
    navigate("/investigation");
  };

  return (
    <div style={styles.wrapper}>

      {/* HERO SECTION */}
      <div style={styles.hero}>
        <h1 style={styles.title}>Digital Forensic Timeline Reconstructor</h1>
        <p style={styles.subtitle}>
          Analyze system activity, reconstruct timelines, and detect suspicious behavior with AI-powered insights.
        </p>
      </div>

      {/* ACTION PANEL */}
      <div style={styles.card}>

        <h2 style={styles.sectionTitle}>Start Investigation</h2>

        <input
          placeholder="Enter Existing Case ID"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          style={styles.input}
        />

        <div style={styles.buttonRow}>
          <button style={styles.loadBtn} onClick={loadCase}>
            Load Case
          </button>

          <button style={styles.newBtn} onClick={startNew}>
            Start New Case
          </button>
        </div>

      </div>

      {/* FEATURES */}
      <div style={styles.features}>

        <div style={styles.featureCard}>
          <h3>Timeline Analysis</h3>
          <p>
            Automatically reconstruct chronological events from file system,
            browser history, and system logs.
          </p>
        </div>

        <div style={styles.featureCard}>
          <h3>AI Insights</h3>
          <p>
            Detect anomalies, suspicious patterns, and generate intelligent
            alerts using AI-based analysis.
          </p>
        </div>

        <div style={styles.featureCard}>
          <h3>Evidence Tracking</h3>
          <p>
            Maintain chain of custody and track digital evidence securely
            throughout the investigation lifecycle.
          </p>
        </div>

      </div>

      {/* HOW TO USE */}
      <div style={styles.howTo}>
        <h2 style={styles.sectionTitle}>How to Use</h2>

        <ol style={styles.steps}>
          <li>Start a new case or load an existing one</li>
          <li>Provide investigator and device details</li>
          <li>Run scan to collect system events</li>
          <li>Analyze timeline and review alerts</li>
          <li>Export reports and insights</li>
        </ol>
      </div>

    </div>
  );
}

/* ================= STYLES ================= */

const styles = {

  wrapper: {
    minHeight: "100vh",
    padding: "30px",
    background: "linear-gradient(135deg, #0f172a, #1e293b)",
    color: "white",
    fontFamily: "sans-serif",
  },

  hero: {
    textAlign: "center",
    marginBottom: "30px",
  },

  title: {
    fontSize: "32px",
    marginBottom: "10px",
  },

  subtitle: {
    color: "#94a3b8",
    fontSize: "15px",
  },

  card: {
    background: "#111827",
    padding: "20px",
    borderRadius: "12px",
    maxWidth: "500px",
    margin: "0 auto",
    textAlign: "center",
    boxShadow: "0 10px 30px rgba(0,0,0,0.4)",
  },

  sectionTitle: {
    marginBottom: "15px",
  },

  input: {
    width: "100%",
    padding: "12px",
    borderRadius: "8px",
    border: "none",
    marginBottom: "15px",
    outline: "none",
  },

  buttonRow: {
    display: "flex",
    gap: "10px",
    justifyContent: "center",
  },

  loadBtn: {
    padding: "10px 15px",
    background: "#2563eb",
    color: "white",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
  },

  newBtn: {
    padding: "10px 15px",
    background: "#22c55e",
    color: "white",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
  },

  features: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
    gap: "15px",
    marginTop: "30px",
  },

  featureCard: {
    background: "#111827",
    padding: "15px",
    borderRadius: "10px",
    border: "1px solid #1f2937",
  },

  howTo: {
    marginTop: "30px",
    background: "#111827",
    padding: "20px",
    borderRadius: "12px",
  },

  steps: {
    marginTop: "10px",
    paddingLeft: "20px",
    lineHeight: "1.8",
    color: "#cbd5f5",
  },
};

export default Home;