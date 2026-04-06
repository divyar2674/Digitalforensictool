import React, { useState, useEffect } from "react";
import Eventtable from "./Eventtable";
import Previewpanel from "./Previewpanel";
import Propertypanel from "./Propertypanel";
import Timelinechat from "./Timelinechat";

import Download from "./Download";
import InvestigationForm from "./InvestigationForm";

function Timeline() {
  const [caseId, setCaseId] = useState(localStorage.getItem("case_id"));
  const [timeline, setTimeline] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);

  useEffect(() => {
    if (!caseId) return;

    fetch(`http://127.0.0.1:8000/timeline/?case_id=${caseId}`)
      .then((res) => res.json())
      .then((data) => {
        setTimeline(data.timeline || []);
        console.log("Fetched timeline:", data.timeline);
      });
  }, [caseId]);

  // 🔒 BLOCK UI UNTIL CASE CREATED
  if (!caseId) {
    return <InvestigationForm onStart={setCaseId} />;
  }

  return (
    <div style={container}>
      {/* HEADER */}
      <div style={header}>
        <div>
          <h2>Forensic Timeline</h2>
          <p style={subText}>Case ID: {caseId}</p>
        </div>

        <div>
          <Download timeline={timeline} />
        </div>
      </div>

      {/* TIMELINE CHAT */}
      <div style={card}>
        <Timelinechat data={timeline} />
      </div>

      {/* MAIN CONTENT */}
      <div style={mainGrid}>
        {/* LEFT: TABLE */}
        <div style={tableSection}>
          <div style={sectionHeader}>Events</div>
          <Eventtable data={timeline} onSelect={setSelectedEvent} />
        </div>

        {/* RIGHT: PROPERTIES */}
        <div style={propertySection}>
          <div style={sectionHeader}>Event Details</div>
          <Propertypanel event={selectedEvent} />
        </div>
      </div>

      {/* BOTTOM SECTION */}
      <div style={bottomGrid}>
        {/* PREVIEW */}
        <div style={card}>
          <div style={sectionHeader}>Preview</div>
          <Previewpanel event={selectedEvent} />
        </div>

        {/* AI ASSISTANT */}
        
      </div>
    </div>
  );
}

export default Timeline;

/* ================= STYLES ================= */

const container = {
  padding: "20px",
  background: "#0b1220",
  minHeight: "100vh",
  color: "white",
  fontFamily: "sans-serif",
};

const header = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  marginBottom: "20px",
};

const subText = {
  color: "#94a3b8",
  fontSize: "14px",
};

const mainGrid = {
  display: "grid",
  gridTemplateColumns: "2fr 1fr",
  gap: "15px",
  marginTop: "15px",
};

const bottomGrid = {
  display: "grid",
  gridTemplateColumns: "1fr",
  gap: "15px",
  marginTop: "15px",
};

const tableSection = {
  background: "#111827",
  borderRadius: "12px",
  padding: "10px",
  maxHeight: "500px",
  overflow: "none",
};

const propertySection = {
  background: "#111827",
  borderRadius: "12px",
  padding: "10px",
  position: "sticky",
  top: "20px",
  height: "fit-content",
};

const card = {
  background: "#111827",
  borderRadius: "12px",
  padding: "15px",
};

const sectionHeader = {
  fontSize: "14px",
  color: "#94a3b8",
  marginBottom: "10px",
  borderBottom: "1px solid #1f2937",
  paddingBottom: "5px",
};