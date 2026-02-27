import React from "react";
import GroupDashboard from "./components/GroupDashboard";

function App() {
  return (
    <div style={{
      minHeight: "100vh",
      backgroundColor: "#f4f6f8",
      padding: "40px",
      fontFamily: "Arial, sans-serif"
    }}>
      <div style={{
        maxWidth: "700px",
        margin: "0 auto",
        background: "white",
        padding: "30px",
        borderRadius: "12px",
        boxShadow: "0 4px 20px rgba(0,0,0,0.08)"
      }}>
        <GroupDashboard />
      </div>
    </div>
  );
}

export default App;