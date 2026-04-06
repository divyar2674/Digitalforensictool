import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

function InvestigationForm({ onStart }) {

  const navigate = useNavigate();

  const [form, setForm] = useState({
    name: "",
    badge_id: "",
    role: "",
    case_id: "",
    title: "",
    description: "",
    device_name: "",
    path: "D:\\"
  });

  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async () => {

    // 🔥 AUTO GENERATE CASE ID IF EMPTY
    let finalCaseId = form.case_id || "CASE_" + Date.now();

    if (!form.name || !form.device_name) {
      alert("⚠ Investigator name & device required");
      return;
    }

    try {
      setLoading(true);

      const res = await fetch("http://127.0.0.1:8000/start-investigation/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...form,
          case_id: finalCaseId
        })
      });

      const data = await res.json();

      console.log("API RESPONSE:", data); // 🔍 debug

      if (data.case_id) {
        // ✅ SAVE CASE
        localStorage.setItem("case_id", data.case_id);

        // ✅ OPTIONAL CALLBACK (if used somewhere)
        if (onStart) {
          onStart(data.case_id);
        }

        // 🔥 REDIRECT TO TIMELINE (MAIN FIX)
        navigate("/Timeline");

      } else {
        alert(data.error || "Failed to create case");
      }

    } catch (err) {
      console.error(err);
      alert("❌ Failed to start investigation");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.wrapper}>

      <div style={styles.card}>

        <h2 style={styles.title}>Digital Forensic Investigation</h2>
        <p style={styles.subtitle}>Enter investigator & case details to begin</p>

        {/* 👤 INVESTIGATOR */}
        <div style={styles.section}>
          <h4 style={styles.sectionTitle}>Investigator Details</h4>

          <input name="name" placeholder="Investigator Name" onChange={handleChange} style={styles.input} />
          <input name="badge_id" placeholder="Badge ID" onChange={handleChange} style={styles.input} />
          <input name="role" placeholder="Role" onChange={handleChange} style={styles.input} />
        </div>

        {/* 📁 CASE */}
        <div style={styles.section}>
          <h4 style={styles.sectionTitle}>Case Details</h4>

          <input name="case_id" placeholder="Case ID (auto if empty)" onChange={handleChange} style={styles.input} />
          <input name="title" placeholder="Case Title" onChange={handleChange} style={styles.input} />
          <textarea name="description" placeholder="Case Description" onChange={handleChange} style={styles.textarea} />
        </div>

        {/* 💻 DEVICE */}
        <div style={styles.section}>
          <h4 style={styles.sectionTitle}>Evidence Device</h4>

          <input name="device_name" placeholder="Device Name" onChange={handleChange} style={styles.input} />
          <input name="path" placeholder="Path (D:\\)" onChange={handleChange} style={styles.input} />
        </div>

        <button
          style={{
            ...styles.button,
            opacity: loading ? 0.7 : 1,
            cursor: loading ? "not-allowed" : "pointer"
          }}
          onClick={handleSubmit}
          disabled={loading}
        >
          {loading ? "Initializing..." : "Start Investigation"}
        </button>

      </div>
    </div>
  );
}

/* ================= STYLES ================= */

const styles = {

  wrapper: {
    minHeight: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    background: "linear-gradient(135deg, #0f172a, #1e293b)",
  },

  card: {
    width: "480px",
    padding: "25px",
    background: "#ffffff",
    borderRadius: "12px",
    boxShadow: "0 15px 40px rgba(0,0,0,0.3)",
  },

  title: {
    margin: 0,
    textAlign: "center",
    color: "#0f172a",
  },

  subtitle: {
    textAlign: "center",
    fontSize: "13px",
    color: "#64748b",
    marginBottom: "15px",
  },

  section: {
    marginBottom: "15px",
  },

  sectionTitle: {
    marginBottom: "8px",
    color: "#1e293b",
    fontSize: "14px",
  },

  input: {
    width: "100%",
    padding: "10px",
    marginBottom: "8px",
    borderRadius: "6px",
    border: "1px solid #cbd5f5",
    fontSize: "13px",
    outline: "none",
  },

  textarea: {
    width: "100%",
    padding: "10px",
    borderRadius: "6px",
    border: "1px solid #cbd5f5",
    fontSize: "13px",
    minHeight: "60px",
    resize: "none",
  },

  button: {
    width: "100%",
    padding: "12px",
    background: "linear-gradient(to right, #2563eb, #1d4ed8)",
    color: "white",
    border: "none",
    borderRadius: "8px",
    fontWeight: "600",
    marginTop: "10px",
    transition: "0.2s",
  },
};

export default InvestigationForm;