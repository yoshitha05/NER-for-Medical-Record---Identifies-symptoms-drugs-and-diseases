import React, { useState } from "react";

const entityColors = {
  "Sign_symptom": "#FFD700",  // Yellow (Symptoms)
  "Disease_disorder": "#FF4500",  // OrangeRed (Diseases)
  "Medication": "#556B2F"  // DarkOliveGreen (Drugs)
};

const API_URL = "/ner";  // Flask backend

const App = () => {
  const [text, setText] = useState("");
  const [displacyData, setDisplacyData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    if (!text.trim()) {
      setError("Please enter medical text before analyzing.");
      return;
    }
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      if (!data.ents || data.ents.length === 0) {
        setError("No entities found in the provided text.");
        setDisplacyData(null);
      } else {
        setDisplacyData(data);
      }
    } catch (error) {
      setError("Failed to fetch data. Ensure Flask is running on port 5001.");
    }
    setLoading(false);
  };

  const handleClear = () => {
    setText("");
    setDisplacyData(null);
    setError(null);
  };

  const renderDisplacy = () => {
    if (!displacyData || !displacyData.ents || displacyData.ents.length === 0) {
      return "Enter text above to analyze!";
    }

    const { text, ents } = displacyData;

    // Sort entities by their start index
    const sortedEntities = ents.sort((a, b) => a.start - b.start);

    // Build the highlighted text
    let highlightedText = "";
    let lastIndex = 0;

    sortedEntities.forEach((ent) => {
      // Add the text before the entity
      highlightedText += text.slice(lastIndex, ent.start);

      // Add the highlighted entity
      const color = entityColors[ent.label] || "#ADD8E6";
      highlightedText += `<span style="background-color: ${color}; color: white; padding: 2px 4px; border-radius: 4px;">${text.slice(ent.start, ent.end)}</span>`;

      // Update the last index
      lastIndex = ent.end;
    });

    // Add the remaining text after the last entity
    highlightedText += text.slice(lastIndex);

    return highlightedText;
  };

  return (
    <div
      style={{
        textAlign: "center",
        padding: "20px",
        fontFamily: "Arial, sans-serif",
        backgroundImage: "linear-gradient(to bottom, #f0f8ffE6, rgba(0, 0, 128, 0.6)), url('/Med.webp')", 
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
        minHeight: "100vh",
        color: "white",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <h1 style={{ fontSize: "40px", fontWeight: "bold", color: "#004d4d", marginBottom: "20px" }}>
        🩺 <span style={{ color: "#004d4d" }}>Medical NER Analyzer</span>
      </h1>
      <div style={{
          width: "100%",
          maxWidth: "600px",
          background: "rgba(255, 255, 255, 0.8)",
          borderRadius: "16px",
          padding: "50px",
          paddingLeft: "20px",
          boxShadow: "0px 8px 20px rgba(0, 0, 0, 0.2)",
          backdropFilter: "blur(10px)",
        }}>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter medical text..."
          rows="6"
          style={{
            width: "100%",
            padding: "15px",
            fontSize: "16px",
            borderRadius: "8px",
            border: "1px solid #ccc",
            marginBottom: "20px",
          }}
        />
        <div style={{ display: "flex", justifyContent: "center", gap: "15px" }}>
          <button onClick={handleAnalyze} disabled={loading} style={{
              padding: "12px 25px", fontSize: "16px", borderRadius: "8px",
              border: "none", backgroundColor: "#007BFF", color: "white",
              cursor: loading ? "not-allowed" : "pointer",
            }}>
            {loading ? "Loading..." : "Analyze"}
          </button>
          <button onClick={handleClear} style={{
              padding: "12px 25px", fontSize: "16px", borderRadius: "8px",
              border: "none", backgroundColor: "#6c757d", color: "white",
            }}>
            Clear
          </button>
        </div>
        {error && <p style={{ color: "#dc3545", marginTop: "15px" }}>⚠️ {error}</p>}
        <div style={{ marginTop: "20px", fontSize: "14px", color: "#555" }} dangerouslySetInnerHTML={{ __html: renderDisplacy() }} />
      </div>
    </div>
  );
};

export default App;
