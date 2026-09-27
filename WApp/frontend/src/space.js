// Talks to the live Hugging Face Space (Gradio API) instead of the local Flask backend.
import { Client, handle_file } from "@gradio/client";

const SPACE = import.meta.env.VITE_SPACE || "yoshitha19/medical-ner";
let client = null;

export async function analyzeWithSpace(text, file) {
  client ??= await Client.connect(SPACE);
  const { data } = await client.predict("/analyze", {
    text: text || "",
    file: file ? handle_file(file) : null,
  });

  // The Space returns the text in pieces: [{token: "fever", class_or_confidence: "SYMPTOM"}, ...]
  // Turn that back into the {text, ents} shape the rest of the app uses.
  const [fullText, pieces] = data;
  const ents = [];
  let pos = 0;
  for (const { token, class_or_confidence: label } of pieces) {
    if (label) ents.push({ text: token, label, start: pos, end: pos + token.length, negated: false });
    pos += token.length;
  }
  return { text: fullText, ents };
}