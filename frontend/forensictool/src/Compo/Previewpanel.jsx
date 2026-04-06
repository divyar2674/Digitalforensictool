import React from "react";

function Previewpanel({ event }) {
  if (!event) {
    return (
      <div
        style={{
          textAlign: "center",
          padding: "20px",
          color: "#888",
          fontFamily: "Segoe UI, sans-serif",
        }}
      >
        Select an event to preview
      </div>
    );
  }

  const meta = event.metadata || {};

  // 🔥 FIXED PATH / URL LOGIC
  const path =
    meta.path ||
    (event.source === "FileSystem" || event.source === "RecycleBin"
      ? event.details
      : "");

  const url =
    meta.url ||
    (event.event_type === "BROWSER_VISIT" ? event.details : "");

  const isImage =
    path &&
    (path.toLowerCase().endsWith(".jpg") ||
      path.toLowerCase().endsWith(".png") ||
      path.toLowerCase().endsWith(".jpeg"));

  return (
    <div
      style={{
        background: "#ffffff",
        borderRadius: "12px",
        padding: "16px",
        boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
        fontFamily: "Segoe UI, sans-serif",
      }}
    >
      {/* HEADER */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "12px",
        }}
      >
        <h3 style={{ margin: 0, fontSize: "18px", fontWeight: "600" }}>
          Preview
        </h3>

        <span
          style={{
            background: "#e3f2fd",
            color: "#1976d2",
            padding: "4px 10px",
            borderRadius: "8px",
            fontSize: "12px",
            fontWeight: "500",
          }}
        >
          {event.event_type}
        </span>
      </div>

      {/* 🖼 IMAGE PREVIEW */}
      {isImage && (
        <div style={{ textAlign: "center", marginBottom: "15px" }}>
          <img
            src={`http://localhost:8000/serve-file?path=${encodeURIComponent(
              path
            )}`}
            alt="preview"
            onClick={() =>
              window.open(
                `http://localhost:8000/serve-file?path=${encodeURIComponent(
                  path
                )}`
              )
            }
            style={{
              width: "140px",
              height: "140px",
              objectFit: "cover",
              borderRadius: "10px",
              border: "1px solid #ddd",
              cursor: "pointer",
              transition: "0.2s",
            }}
          />

          <p
            style={{
              fontSize: "11px",
              marginTop: "8px",
              color: "#666",
              wordBreak: "break-all",
            }}
          >
            {path}
          </p>
        </div>
      )}

      {/* 🌐 BROWSER PREVIEW */}
      {event.event_type === "BROWSER_VISIT" && url && (
        <div style={{ marginBottom: "15px" }}>
          <iframe
            src={url}
            title="browser-preview"
            style={{
              width: "100%",
              height: "250px",
              borderRadius: "8px",
              border: "1px solid #ddd",
            }}
          />

          <a
            href={url}
            target="_blank"
            rel="noreferrer"
            style={{
              display: "block",
              marginTop: "8px",
              fontSize: "13px",
              color: "#1976d2",
              textDecoration: "none",
            }}
          >
            🔗 Open in new tab
          </a>
        </div>
      )}

      {/* 📄 DEFAULT INFO */}
      {!isImage && event.event_type !== "BROWSER_VISIT" && (
        <div
          style={{
            background: "#f9fafc",
            padding: "10px",
            borderRadius: "8px",
            marginBottom: "12px",
          }}
        >
          <p
            style={{
              fontSize: "12px",
              fontWeight: "600",
              color: "#555",
              marginBottom: "4px",
            }}
          >
            File / Path
          </p>

          <p
            style={{
              fontSize: "13px",
              color: "#222",
              wordBreak: "break-all",
            }}
          >
            {path || "Not available"}
          </p>
        </div>
      )}

      {/* 📊 METADATA */}
      <div>
        <p
          style={{
            fontSize: "12px",
            fontWeight: "600",
            color: "#555",
            marginBottom: "6px",
          }}
        >
          Metadata
        </p>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "6px",
          }}
        >
          {Object.entries(meta).map(([key, value]) => (
            <div
              key={key}
              style={{
                background: "#f4f6f8",
                padding: "6px",
                borderRadius: "6px",
              }}
            >
              <span
                style={{
                  fontSize: "11px",
                  color: "#777",
                  display: "block",
                }}
              >
                {key}
              </span>

              <span
                style={{
                  fontSize: "12px",
                  fontWeight: "500",
                  color: "#333",
                }}
              >
                {String(value || "N/A")}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Previewpanel;