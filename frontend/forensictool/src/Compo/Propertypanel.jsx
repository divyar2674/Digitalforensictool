import React from "react";

function Propertypanel({ event }) {
  if (!event) {
    return <div>Select an event</div>;
  }

  const meta = event.metadata || {};

  const textStyle = {
    wordBreak: "break-word",
    overflowWrap: "break-word",
    whiteSpace: "normal",
  };

  const safe = (value) =>
    value !== undefined && value !== null && value !== "" ? value : "N/A";

  // 🔥 FIX: EXTRACT PATH PROPERLY
  const filePath =
    event.details || meta.full_path || meta.path || "N/A";

  // 🔥 Extract previous state (for deleted files)
  const prev = meta.previous_state || {};

  return (
    <div style={{ padding: "10px" }}>
      <h3>Properties</h3>

      <p><b>Timestamp:</b> {safe(event.timestamp)}</p>
      <p><b>Event:</b> {safe(event.event_type)}</p>
      <p><b>File/User:</b> {safe(event.file_name)}</p>
      <p><b>Source:</b> {safe(event.source)}</p>

      <hr />

      {/* 🔥 FILE DETAILS */}
      {event.event_type?.startsWith("FILE") && (
        <>
          <h4>File Details</h4>

          {/* ✅ FIXED PATH */}
          <p style={textStyle}>
            <b>Path:</b> {safe(filePath)}
          </p>

          <p>
            <b>Size:</b> {safe(meta.size)}
          </p>

          <p>
            <b>Type:</b> {safe(meta.extension)}
          </p>

          {/* 🔥 HANDLE NORMAL + DELETED FILES */}
          <p>
            <b>Created:</b> {safe(prev.created_time || meta.created_time || meta.created)}
          </p>

          <p>
            <b>Modified:</b> {safe(prev.modified_time || meta.modified_time || meta.modified)}
          </p>

          <p>
            <b>Accessed:</b> {safe(prev.accessed_time || meta.accessed_time || meta.accessed)}
          </p>

          {/* 🔥 SHOW DELETE TIME */}
          {meta.deleted_time && (
            <p>
              <b>Deleted:</b> {safe(meta.deleted_time)}
            </p>
          )}
        </>
      )}

      {/* 🔥 BROWSER DETAILS */}
      {event.event_type === "BROWSER_VISIT" && (
        <>
          <h4>Browser Details</h4>

          <p style={textStyle}>
            <b>URL:</b> {safe(meta.url)}
          </p>

          <p style={textStyle}>
            <b>Title:</b> {safe(meta.title)}
          </p>

          <p>
            <b>Visit Count:</b> {safe(meta.visit_count)}
          </p>

          <p>
            <b>Typed Count:</b> {safe(meta.typed_count)}
          </p>
        </>
      )}

      {/* 🔥 WINDOWS LOGIN EVENTS */}
      {(event.event_type === "LOGIN_FAILURE" ||
        event.event_type === "LOGIN_SUCCESS") && (
        <>
          <h4>Login Details</h4>

          <p>
            <b>Username:</b> {safe(meta.username)}
          </p>

          <p>
            <b>IP Address:</b> {safe(meta.ip_address)}
          </p>

          <p>
            <b>Status:</b> {safe(meta.status)}
          </p>

          <p>
            <b>Event ID:</b> {safe(meta.event_id)}
          </p>
        </>
      )}

      {/* 🔥 PROCESS EVENTS */}
      {event.event_type === "PROCESS_CREATED" && (
        <>
          <h4>Process Details</h4>

          <p style={textStyle}>
            <b>Process:</b> {safe(meta.process)}
          </p>

          <p>
            <b>Event ID:</b> {safe(meta.event_id)}
          </p>
        </>
      )}

      {/* 🔹 DEFAULT */}
      {!event.event_type?.startsWith("FILE") &&
        event.event_type !== "BROWSER_VISIT" &&
        event.event_type !== "LOGIN_FAILURE" &&
        event.event_type !== "LOGIN_SUCCESS" &&
        event.event_type !== "PROCESS_CREATED" && (
          <>
            <h4>Details</h4>
            <p style={textStyle}>{safe(event.details)}</p>
          </>
        )}
    </div>
  );
}

export default Propertypanel;