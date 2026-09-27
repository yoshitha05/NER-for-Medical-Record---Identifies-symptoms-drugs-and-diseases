import { useState } from "react";
import "./App.css";
import { analyzeWithSpace } from "./space";

// Online (Vercel): VITE_USE_SPACE=true sends requests to the Hugging Face Space.
// On your laptop: uses the local Flask backend.
const USE_SPACE = import.meta.env.PROD || import.meta.env.VITE_USE_SPACE === "true";
const API = import.meta.env.VITE_API_URL || "http://localhost:5001";
const LABELS = ["SYMPTOM", "DRUG", "DISEASE"];

// Split the text into plain parts and highlighted entity parts
function Highlighted({ text, ents }) {
  const parts = [];
  let last = 0;
  ents.forEach((e, i) => {
    if (e.start > last) parts.push(text.slice(last, e.start));
    parts.push(
      <mark key={i} className={e.label} title={e.label}>
        {text.slice(e.start, e.end)}
      </mark>
    );
    last = e.end;
  });
  parts.push(text.slice(last));
  return <div className="result">{parts}</div>;
}

export default function App() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function send(url, options, spaceInput) {
    setLoading(true);
    setError("");
    try {
      let data;
      if (USE_SPACE) {
        data = await analyzeWithSpace(spaceInput.text, spaceInput.file);
      } else {
        const res = await fetch(url, options);
        data = await res.json();
        if (!res.ok) throw new Error(data.error);
      }
      setResult(data);
      setText(data.text);
    } catch (err) {
      setError(err.message || "Something went wrong");
    }
    setLoading(false);
  }

  const analyzeText = () =>
    send(`${API}/ner`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    }, { text });

  const uploadFile = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const form = new FormData();
    form.append("file", file);
    send(`${API}/upload`, { method: "POST", body: form }, { file });
    e.target.value = ""; // allow uploading the same file again
  };

  const clearAll = () => {
    setText("");
    setResult(null);
    setError("");
  };

  return (
    <main>
      <h1>🩺 NER in Medical Records</h1>

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Type or paste a clinical note..."
      />

      <div className="actions">
        <button onClick={analyzeText} disabled={loading || !text.trim()}>
          {loading ? "Analyzing..." : "Analyze"}
        </button>
        <label className="upload">
          Upload file (.txt, .pdf, .docx, image)
          <input type="file" accept=".txt,.pdf,.docx,.png,.jpg,.jpeg" onChange={uploadFile} hidden />
        </label>
        <button className="clear" onClick={clearAll} disabled={loading}>
          Clear
        </button>
      </div>

      {error && <p className="error">{error}</p>}

      {result && (
        <>
          <div className="legend">
            {LABELS.map((l) => (
              <span key={l} className={l}>
                {l} ({result.ents.filter((e) => e.label === l && !e.negated).length})
              </span>
            ))}
          </div>
          {/* negated entities ("denies fever") are left as plain text */}
          <Highlighted text={result.text} ents={result.ents.filter((e) => !e.negated)} />
        </>
      )}
    </main>
  );
}