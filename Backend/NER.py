import spacy
from spacy.tokens import Span
from transformers import pipeline

# Load a medical NER model from Hugging Face
nlp_ner = pipeline("ner", model="d4data/biomedical-ner-all", aggregation_strategy="simple")

def perform_ner(text):
    """Performs NER on the provided text and returns entities in JSON format."""

    # Perform NER using the loaded model
    entities = nlp_ner(text)

    # Convert Hugging Face entities to spaCy Span objects
    nlp = spacy.blank("en")
    doc = nlp(text)
    spans = []
    for ent in entities:
        # Use char_span to create spans directly from character indices
        span = doc.char_span(ent['start'], ent['end'], label=ent['entity_group'])
        if not span:
            # Fallback: manually create a span if char_span fails
            span = Span(doc, doc.text[:ent['start']].count(" "), doc.text[:ent['end']].count(" "), label=ent['entity_group'])
        spans.append(span)
    doc.set_ents(spans, default="unmodified")

    # Return structured JSON output
    return {
        "text": text,
        "ents": [
            {
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            }
            for ent in doc.ents
        ]
    }
