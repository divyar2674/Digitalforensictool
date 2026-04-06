import React, { useState } from 'react'
import { Link } from "react-router-dom";

function Navbar() {

  const [hovered, setHovered] = useState(null);

  const styles = {
    nav: {
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      background: "#ffffff",
      padding: "12px 40px",
      borderBottom: "1px solid #e2e8f0",
      boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
    },

    logo: {
      fontSize: "20px",
      fontWeight: "600",
      color: "#1e293b",
    },

    links: {
      display: "flex",
      gap: "15px",
    },

    link: {
      padding: "6px 12px",
      borderRadius: "6px",
      textDecoration: "none",
      fontWeight: "500",
      color: "#334155",
      transition: "0.2s",
    }
  };

  const getStyle = (name) => ({
    ...styles.link,
    backgroundColor: hovered === name ? "#e2e8f0" : "transparent",
    color: hovered === name ? "#1e293b" : "#334155",
  });

  return (
    <nav style={styles.nav}>
      
      {/* Logo */}
      <div style={styles.logo}>Forensic Tool</div>

      {/* Links */}
      <div style={styles.links}>
        <Link
          to="/"
          style={getStyle("home")}
          onMouseEnter={() => setHovered("home")}
          onMouseLeave={() => setHovered(null)}
        >
          Home
        </Link>


        <Link
          to="/Timeline"
          style={getStyle("timeline")}
          onMouseEnter={() => setHovered("timeline")}
          onMouseLeave={() => setHovered(null)}
        >
          Timeline
        </Link>
      </div>

    </nav>
  )
}

export default Navbar