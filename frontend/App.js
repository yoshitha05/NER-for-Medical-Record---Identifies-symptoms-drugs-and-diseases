import React, { useState } from "react";

const entityColors = {
  "B-Sign_symptom": "#FFD700",  // Gold for symptoms
  "I-Sign_symptom": "#FFD700",  // Gold for continuation of symptoms
  "B-Medication": "#FF6347",    // Tomato red for medications
  "I-Medication": "#FF6347",    // Tomato red for continuation of medications
  "B-Disease": "#32CD32",       // Lime green for diseases
  "I-Disease": "#32CD32"       // Lime green for diseases
};

const App = () => {
  const [text, setText] = useState("");
  const [entities, setEntities] = useState([]);
  const [error, setError] = useState(null);

  const handleAnalyze = async () => {
    try {
      const response = await fetch("http://localhost:5001/ner", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      setEntities(data.entities);
      setError(null);
    } catch (error) {
      console.error("Fetch error:", error);
      setError("Failed to fetch data. Ensure Flask is running on port 5001.");
    }
  };

  const handleClear = () => {
    setText("");
    setEntities([]);
    setError(null);
  };

  return (
    <div style={{
      minHeight: "100vh",
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      flexDirection: "column",
      fontFamily: "'Arial', sans-serif",
      background: "linear-gradient(to right, #ff9a9e, #fad0c4)", // Pink gradient background
      color: "#333",
      padding: "20px"
    }}>
      <h1 style={{ fontSize: "28px", fontWeight: "bold", marginBottom: "20px" }}>
       🩺 Medical NER Analyzer
      </h1>

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Enter medical text..."
        rows="4"
        style={{
          width: "80%",
          maxWidth: "600px",
          padding: "12px",
          fontSize: "16px",
          borderRadius: "10px",
          border: "1px solid #ccc",
          boxShadow: "2px 2px 10px rgba(0, 0, 0, 0.1)"
        }}
      />

      <div style={{ marginTop: "15px" }}>
        <button 
          onClick={handleAnalyze} 
          style={{
            padding: "12px 20px",
            fontSize: "16px",
            cursor: "pointer",
            backgroundColor: "#ff477e", // Pinkish-red button
            color: "#fff",
            border: "none",
            borderRadius: "8px",
            fontWeight: "bold",
            boxShadow: "2px 2px 10px rgba(0, 0, 0, 0.2)",
            marginRight: "10px"
          }}
        >
          Analyze
        </button>
        <button 
          onClick={handleClear} 
          style={{
            padding: "12px 20px",
            fontSize: "16px",
            cursor: "pointer",
            backgroundColor: "#f44336", // Red button
            color: "#fff",
            border: "none",
            borderRadius: "8px",
            fontWeight: "bold",
            boxShadow: "2px 2px 10px rgba(0, 0, 0, 0.2)"
          }}
        >
          Clear
        </button>
      </div>

      {error && (
        <p style={{ color: "red", marginTop: "10px", fontSize: "16px" }}>
          ⚠️ {error}
        </p>
      )}

      <div style={{
        fontSize: "18px",
        lineHeight: "1.6",
        marginTop: "20px",
        background: "#fff",
        padding: "15px",
        borderRadius: "10px",
        boxShadow: "3px 3px 15px rgba(0, 0, 0, 0.2)",
        maxWidth: "600px",
        width: "80%",
        textAlign: "center"
      }}>
        {entities.length > 0 ? (
          entities.map((entity, index) => (
            <span 
              key={index}
              style={{
                backgroundColor: entityColors[entity.entity] || "#ADD8E6", // Default blue if unknown entity
                padding: "5px 10px",
                borderRadius: "8px",
                margin: "4px",
                fontWeight: "bold",
                display: "inline-block"
              }}
            >
              {entity.word} ({entity.entity}) {`[${entity.score.toFixed(2)}]`}
            </span>
          ))
        ) : (
          <p style={{ color: "#777", fontSize: "16px" }}>No entities found. Enter text above! 📝</p>
        )}
      </div>
    </div>
  );
};

export default App;
