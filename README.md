# 🩺 NER in Medical Records

Finds and highlights **symptoms**, **drugs** and **diseases** in clinical notes, prescriptions and discharge summaries.

**Live demo:** https://huggingface.co/spaces/yoshitha19/medical-ner

![Screenshot](screenshot.png)

## Features

- Highlights entities in colour: 🟨 symptoms · 🟦 drugs · 🟥 diseases
- Type or paste text, or upload a file: `.txt`, `.pdf`, `.docx`, `.png`, `.jpg`
- Reads scanned PDFs and photos of documents with OCR
- Counts each entity type

## How it works

```
text / file ──► OCR (if scanned) ──► spaCy EntityRuler ──► Hugging Face model ──► highlighted result
                   Tesseract          medical dictionary     fills in the rest
```

1. **spaCy EntityRuler** matches known medical terms from a dictionary. This is fast and precise.
2. **Hugging Face transformer** [`d4data/biomedical-ner-all`](https://huggingface.co/d4data/biomedical-ner-all), a DistilBERT model trained on clinical case reports, finds entities the dictionary doesn't know, such as *burning micturition* or *Montair LC*. Its labels are mapped to SYMPTOM, DRUG and DISEASE, and predictions below 0.5 confidence are dropped.
3. Overlapping matches are merged, keeping the longest span.

## Tech stack

Python · spaCy · Hugging Face Transformers · PyTorch · Tesseract OCR · PyMuPDF · Flask · React (Vite) · Gradio · Hugging Face Spaces (ZeroGPU)

## Project structure

```
├── space/              Gradio app deployed on Hugging Face Spaces (live demo)
└── WApp/
    ├── backend/        Flask API: /ner (text) and /upload (files)
    └── frontend/       React web app
```

## Run locally

**Backend**

```bash
python -m venv venv
source venv/bin/activate
cd WApp/backend
pip install -r requirements.txt
brew install tesseract          # for OCR (Mac); Ubuntu: sudo apt install tesseract-ocr
python app.py                   # http://localhost:5001
```

**Frontend** (in a second terminal)

```bash
cd WApp/frontend
npm install
npm run dev                     # http://localhost:5173
```

**Or the Gradio version**

```bash
cd space
pip install -r requirements.txt gradio
python app.py                   # http://localhost:7860
```

The Hugging Face model (~260 MB) downloads on the first run.

## Limitations and next steps

- **Negation:** "patient denies fever" still highlights *fever*. Next step: negation detection (e.g. `negspacy`).
- **Small dictionary:** the spaCy rules cover common terms only, and the transformer handles the rest.
- **OCR** works well on printed text but not on handwriting.
- Not a medical device. This is for demonstration only.