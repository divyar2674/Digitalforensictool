import React, { useEffect, useState } from "react";
import { Routes, Route, Navigate } from "react-router-dom";

import Navbar from "./Compo/Navbar";
import Home from "./Compo/Home";
import Dashboard from "./Compo/Dashboard";
import Timeline from "./Compo/Timeline";
import AIAssistant from "./Compo/AIAssistant";
import Summarypanel from "./Compo/Summarypanel";
import Storypanel from "./Compo/Storypanel";
import InvestigationForm from "./Compo/InvestigationForm";
function App() {
  const [caseId, setCaseId] = useState(null);

  // 🔥 FORCE ASK EVERY TIME
  useEffect(() => {
    localStorage.removeItem("case_id");
    setCaseId(null);
  }, []);

  return (
    <>
      <Navbar />

      <Routes>
        <Route path="/" element={<Home setCaseId={setCaseId} />} />

        <Route
          path="/Dashboard"
          element={
            caseId ? <Dashboard /> : <Navigate to="/" />
          }
        />

        <Route
          path="/Timeline"
          element={
            caseId ? <Timeline /> : <Navigate to="/" />
          }
        />
        <Route path="/investigation" element={<InvestigationForm />} />
        <Route
          path="/summary"
          element={
            caseId ? <Summarypanel /> : <Navigate to="/" />
          }
        />

        <Route
          path="/story"
          element={
            caseId ? <Storypanel /> : <Navigate to="/" />
          }
        />
      </Routes>

      <AIAssistant />
    </>
  );
}

export default App;