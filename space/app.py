try:
    import spaces  # noqa: F401  (must come first on a ZeroGPU Space)
except ImportError:
    pass

import gradio as gr
import pymupdf
import pytesseract
from docx import Document
from PIL import Image

from NER import perform_ner

COLORS = {"SYMPTOM": "#fde68a", "DRUG": "#93c5fd", "DISEASE": "#fca5a5"}


def ocr(image):
    return pytesseract.image_to_string(image.convert("L"))


def read_file(path):
    name = path.lower()
    if name.endswith(".txt"):
        return open(path, encoding="utf-8", errors="ignore").read()
    if name.endswith(".pdf"):
        pages = []
        for page in pymupdf.open(path):
            text = page.get_text()
            if not text.strip():  # scanned page -> OCR
                text = ocr(Image.frombytes("RGB", *_page_image(page)))
            pages.append(text)
        return "\n".join(pages)
    if name.endswith(".docx"):
        return "\n".join(p.text for p in Document(path).paragraphs)
    if name.endswith((".png", ".jpg", ".jpeg")):
        return ocr(Image.open(path))
    raise gr.Error("Supported files: .txt, .pdf, .docx, .png, .jpg")


def _page_image(page):
    pix = page.get_pixmap(dpi=300)
    return (pix.width, pix.height), pix.samples


def analyze(text, file):
    if file:
        text = read_file(file)
    if not text or not text.strip():
        raise gr.Error("Type some text or upload a file first.")

    result = perform_ner(text)
    highlighted = {
        "text": result["text"],
        # negated entities ("denies fever") are left as plain text
        "entities": [
            {"entity": e["label"], "start": e["start"], "end": e["end"]}
            for e in result["ents"] if not e["negated"]
        ],
    }
    counts = " · ".join(
        f"**{label}**: {sum(e['entity'] == label for e in highlighted['entities'])}" for label in COLORS
    )
    return text, highlighted, counts


EXAMPLES = [
    "Patient is a 34-year-old female presenting with high fever, body pain and headache for 4 days. "
    "Also reports vomiting and loss of appetite. Suspected dengue. Advised Dolo 650 three times a day and ORS.",
    "65-year-old male, known case of type 2 diabetes and hypertension. Currently on Metformin 500 mg and "
    "Amlodipine 5 mg. Complains of fatigue, frequent urination and blurred vision.",
    "Child brought with dry cough, wheezing and shortness of breath since last night. History of asthma. "
    "Started on Montelukast and Budesonide inhaler.",
    "Patient denies fever, cough or chest pain. No history of diabetes. Malaria ruled out. "
    "Complains only of mild headache. Given Paracetamol.",
]

with gr.Blocks(title="NER in Medical Records") as demo:
    gr.Markdown(
        "# 🩺 NER in Medical Records\n"
        "Highlights **symptoms**, **drugs** and **diseases** in clinical text using spaCy and the "
        "Hugging Face model `d4data/biomedical-ner-all`. Things the patient does **not** have "
        "(\"denies fever\", \"no history of diabetes\") are not highlighted."
    )

    text = gr.Textbox(label="Clinical note", lines=6, placeholder="Type or paste a clinical note...")
    file = gr.File(label="Or upload a file (.txt, .pdf, .docx, image)",
                   file_types=[".txt", ".pdf", ".docx", ".png", ".jpg", ".jpeg"], type="filepath")

    with gr.Row():
        analyze_btn = gr.Button("Analyze", variant="primary")
        clear_btn = gr.ClearButton(value="Clear")

    counts = gr.Markdown()
    output = gr.HighlightedText(label="Result", color_map=COLORS, show_legend=True, combine_adjacent=False)

    clear_btn.add([text, file, output, counts])
    analyze_btn.click(analyze, inputs=[text, file], outputs=[text, output, counts])
    gr.Examples(EXAMPLES, inputs=text)

if __name__ == "__main__":
    demo.launch()