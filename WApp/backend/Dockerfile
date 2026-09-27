FROM python:3.11-slim

# Tesseract for OCR (scanned PDFs and images)
RUN apt-get update \
    && apt-get install -y --no-install-recommends tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Hugging Face Spaces runs the app as user 1000
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    HF_HOME=/home/user/.cache/huggingface
WORKDIR /home/user/app

# CPU-only torch (much smaller than the default GPU build), then the rest
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download the Hugging Face model during the build so the first request is fast
RUN python -c "from transformers import pipeline; pipeline('ner', model='d4data/biomedical-ner-all')"

COPY --chown=user . .

# Cloud Run / Render give the port in $PORT; defaults to 7860 otherwise
ENV PORT=7860
EXPOSE 7860
CMD gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 180 app:app