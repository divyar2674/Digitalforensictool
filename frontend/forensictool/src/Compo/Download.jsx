import React, { useState } from "react";

const Download = ({ timeline }) => {
  const [loading, setLoading] = useState(false);

  // 🔥 SAFE fallback
  const safeTimeline = Array.isArray(timeline) ? timeline : [];

  const handleDownload = async (type) => {
    try {
      setLoading(true);

      // =========================
      // 📄 CSV DOWNLOAD
      // =========================
      if (type === "csv") {
        const caseId = localStorage.getItem("case_id");

        const response = await fetch(
          `http://127.0.0.1:8000/export_csv/?case_id=${caseId}`
        );

        if (!response.ok) throw new Error("CSV download failed");

        const blob = await response.blob();
        downloadFile(blob, "forensic_records.csv");
      }

      // =========================
      // 📊 PDF DOWNLOAD (WITH GRAPH)
      // =========================
      else if (type === "pdf") {
        const element = document.getElementById("timeline-graph");

        if (!element) {
          alert("Graph not found");
          setLoading(false);
          return;
        }

        // 🔥 SAFE dynamic import (prevents crash)
        const html2canvas = (await import("html2canvas")).default;

        // wait for graph render
        await new Promise((res) => setTimeout(res, 500));

        const canvas = await html2canvas(element, { scale: 2 });
        const graphImage = canvas.toDataURL("image/png");

        const response = await fetch("http://127.0.0.1:8000/export_pdf/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            case_id: localStorage.getItem("case_id"),
            graph: graphImage,
            timeline: safeTimeline,
          }),
        });

        if (!response.ok) throw new Error("PDF download failed");

        const blob = await response.blob();
        downloadFile(blob, "forensic_report.pdf");
      }
    } catch (error) {
      console.error("Download error:", error);
      alert("Download failed. Check console.");
    } finally {
      setLoading(false);
    }
  };

  // 🔥 DOWNLOAD HELPER
  const downloadFile = (blob, filename) => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
  };

  return (
    <div style={styles.container}>
      <h3 style={styles.heading}>Export Scan Results</h3>

      <div style={styles.buttonGroup}>
        {/* CSV BUTTON */}
        <button
          style={{
            ...styles.button,
            backgroundColor: "#16a34a",
            opacity: loading ? 0.7 : 1,
          }}
          disabled={loading}
          onClick={() => handleDownload("csv")}
        >
          {loading ? "Processing..." : "Download CSV"}
        </button>

        {/* PDF BUTTON */}
        <button
          style={{
            ...styles.button,
            backgroundColor: "#2563eb",
            opacity: loading ? 0.7 : 1,
          }}
          disabled={loading}
          onClick={() => handleDownload("pdf")}
        >
          {loading ? "Generating..." : "Download PDF"}
        </button>
      </div>
    </div>
  );
};

export default Download;


//
// ================= STYLES =================
//

const styles = {
  container: {
    padding: "10px",
    borderRadius: "10px",
    background: "#111827",
    color: "#fff",
  },
  heading: {
    marginBottom: "8px",
    fontSize: "14px",
    color: "#cbd5f5",
  },
  buttonGroup: {
    display: "flex",
    gap: "10px",
  },
  button: {
    padding: "8px 12px",
    border: "none",
    borderRadius: "6px",
    color: "#fff",
    cursor: "pointer",
    fontWeight: "600",
  },
};