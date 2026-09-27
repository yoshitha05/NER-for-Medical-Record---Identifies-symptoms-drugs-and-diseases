import io
import os

import pymupdf as fitz
import pytesseract
from docx import Document
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image

from NER import perform_ner

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB upload limit
CORS(app)

IMAGE_TYPES = (".png", ".jpg", ".jpeg")


def ocr(image):
    return pytesseract.image_to_string(image.convert("L"))  # grayscale helps OCR


def read_pdf(data):
    pages = []
    for page in fitz.open(stream=data, filetype="pdf"):
        text = page.get_text()
        if not text.strip():  # scanned page (just an image) -> OCR it
            pix = page.get_pixmap(dpi=300)
            text = ocr(Image.open(io.BytesIO(pix.tobytes("png"))))
        pages.append(text)
    return "\n".join(pages)


def read_file(file):
    name = file.filename.lower()
    if name.endswith(".txt"):
        return file.read().decode("utf-8", errors="ignore")
    if name.endswith(".pdf"):
        return read_pdf(file.read())
    if name.endswith(".docx"):
        return "\n".join(p.text for p in Document(file).paragraphs)
    if name.endswith(IMAGE_TYPES):
        return ocr(Image.open(file))
    raise ValueError("Supported files: .txt, .pdf, .docx, .png, .jpg")


@app.errorhandler(413)
def too_large(_):
    return jsonify({"error": "File is too large (max 10 MB)"}), 413


@app.route("/")
def health():
    return jsonify({"status": "ok"})


@app.route("/ner", methods=["POST"])
def analyze_text():
    text = (request.get_json(silent=True) or {}).get("text", "")
    if not text.strip():
        return jsonify({"error": "No text provided"}), 400
    return jsonify(perform_ner(text))


@app.route("/upload", methods=["POST"])
def analyze_file():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400
    try:
        text = read_file(file)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except pytesseract.TesseractNotFoundError:
        return jsonify({"error": "Tesseract is not installed (Mac: brew install tesseract)"}), 500
    except Exception:
        return jsonify({"error": "Could not read this file. Is it damaged?"}), 400
    if not text.strip():
        return jsonify({"error": "No readable text found in the file"}), 400
    return jsonify(perform_ner(text))


if __name__ == "__main__":
    app.run(port=int(os.getenv("PORT", 5001)), debug=True)