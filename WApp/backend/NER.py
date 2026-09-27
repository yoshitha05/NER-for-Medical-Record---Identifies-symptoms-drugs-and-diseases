import os

import spacy
from spacy.util import filter_spans
from negspacy.negation import Negex  # noqa: F401  (registers the "negex" component)
from negspacy.termsets import termset
from transformers import pipeline

from medical_terms import DISEASES, DRUGS, SYMPTOMS

# 1. spaCy pipeline with a medical dictionary (medical_terms.py)
nlp = spacy.blank("en")
nlp.add_pipe("sentencizer")  # negation only looks within the same sentence
ruler = nlp.add_pipe("entity_ruler", config={"phrase_matcher_attr": "LOWER"})
ruler.add_patterns(
    [{"label": "DISEASE", "pattern": t} for t in DISEASES]
    + [{"label": "DRUG", "pattern": t} for t in DRUGS]
    + [{"label": "SYMPTOM", "pattern": t} for t in SYMPTOMS]
)

# 2. Negation: marks entities the patient does NOT have ("denies fever", "no history of diabetes")
negation_terms = termset("en_clinical")
negation_terms.add_patterns({"following_negations": ["ruled out", "absent", "not present", "negative"]})
negex = nlp.add_pipe("negex", config={"neg_termset": negation_terms.get_patterns()})

# 3. Hugging Face model fills in what the dictionary misses
# Set USE_HF=0 to run with the dictionary only (evaluate.py uses this to compare)
USE_HF = os.getenv("USE_HF", "1") != "0"
hf_ner = pipeline("ner", model="d4data/biomedical-ner-all", aggregation_strategy="simple") if USE_HF else None
LABEL_MAP = {"Sign_symptom": "SYMPTOM", "Disease_disorder": "DISEASE", "Medication": "DRUG"}


def perform_ner(text):
    doc = nlp(text)
    spans = list(doc.ents)

    for ent in (hf_ner(text) if hf_ner else []):
        label = LABEL_MAP.get(ent["entity_group"])
        if label and ent["score"] > 0.5:  # skip low-confidence guesses
            span = doc.char_span(ent["start"], ent["end"], label=label, alignment_mode="expand")
            if span is not None:
                spans.append(span)

    # Remove overlaps: keeps the longest span (e.g. "chest pain" over "pain")
    doc.ents = filter_spans(spans)
    negex(doc)  # run negation again so it also covers entities found by the Hugging Face model

    return {
        "text": text,
        "ents": [
            {"text": e.text, "label": e.label_, "start": e.start_char, "end": e.end_char, "negated": e._.negex}
            for e in doc.ents
        ],
    }


if __name__ == "__main__":
    print(perform_ner("Patient denies fever and burning micturition. No history of diabetes. Has headache. Given Dolo 650."))