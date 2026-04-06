import React, { useState } from "react";

function Eventtable({ data, onSelect }) {
  const [selectedIndex, setSelectedIndex] = useState(null);

  if (!data || data.length === 0) {
    return <div style={{ padding: 10 }}>No events found</div>;
  }

  const getEventColor = (type) => {
    if (!type) return "#94a3b8";
    if (type === "FILE_DELETED") return "#ef4444";
    if (type === "FILE_CREATED") return "#22c55e";
    if (type === "FILE_MODIFIED") return "#eab308";
    if (type === "FILE_ACCESSED") return "#38bdf8";
    if (type === "BROWSER_VISIT") return "#60a5fa";
    return "#94a3b8";
  };

  const formatTime = (time) => {
    if (!time) return "-";
    try {
      return new Date(time).toLocaleString();
    } catch {
      return "-";
    }
  };

  // 🔥 EXPAND EVENTS INTO MULTIPLE ROWS
  const expandedData = data.flatMap((event) => {
    if (event.event_type === "FILE_DELETED") {
      const prev = event.metadata?.previous_state || {};

      return [
        prev.created_time && {
          ...event,
          event_type: "FILE_CREATED",
          timestamp: prev.created_time,
        },
        prev.modified_time && {
          ...event,
          event_type: "FILE_MODIFIED",
          timestamp: prev.modified_time,
        },
        prev.accessed_time && {
          ...event,
          event_type: "FILE_ACCESSED",
          timestamp: prev.accessed_time,
        },
        event, // original delete event
      ].filter(Boolean);
    }

    return [event];
  });

  // 🔥 SORT BY TIME (important)
  expandedData.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

  return (
    <div style={container}>
      <table style={table}>
        <thead style={thead}>
          <tr>
            <th style={th}>Time</th>
            <th style={th}>Event</th>
            <th style={th}>File</th>
            <th style={th}>Source</th>
          </tr>
        </thead>

        <tbody>
          {expandedData.map((event, index) => {
            const isSelected = index === selectedIndex;

            return (
              <tr
                key={index}
                onClick={() => {
                  setSelectedIndex(index);
                  onSelect(event);
                }}
                style={{
                  ...row,
                  ...(isSelected && selectedRow),
                }}
              >
                {/* TIME */}
                <td style={td}>{formatTime(event.timestamp)}</td>

                {/* EVENT */}
                <td style={td}>
                  <div style={eventCell}>
                    <span
                      style={{
                        ...dot,
                        background: getEventColor(event.event_type),
                      }}
                    />
                    <span
                      style={{
                        color: getEventColor(event.event_type),
                        fontWeight: "500",
                      }}
                    >
                      {event.event_type}
                    </span>
                  </div>
                </td>

                {/* FILE */}
                <td style={td} title={event.file_name}>
                  {truncate(event.file_name, 25)}
                </td>

                {/* SOURCE */}
                <td style={td}>{event.source}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

/* ================= HELPERS ================= */

const truncate = (text, len) => {
  if (!text) return "-";
  return text.length > len ? text.slice(0, len) + "..." : text;
};

/* ================= STYLES ================= */

const container = {
  maxHeight: "500px",
  overflowY: "auto",
  borderRadius: "12px",
  background: "#0b1220",
};

const table = {
  width: "100%",
  borderCollapse: "collapse",
};

const thead = {
  position: "sticky",
  top: 0,
  background: "#1e293b",
  zIndex: 1,
};

const th = {
  padding: "12px",
  textAlign: "left",
  fontSize: "13px",
  color: "#cbd5f5",
  borderBottom: "1px solid #334155",
};

const td = {
  padding: "10px",
  fontSize: "13px",
  borderBottom: "1px solid #1f2937",
};

const row = {
  cursor: "pointer",
  transition: "0.2s",
};

const selectedRow = {
  background: "#1e293b",
};

const eventCell = {
  display: "flex",
  alignItems: "center",
  gap: "8px",
};

const dot = {
  width: "8px",
  height: "8px",
  borderRadius: "50%",
};

export default Eventtable;