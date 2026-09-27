# `spaces` must be imported before torch/transformers on a ZeroGPU Space.
# On the Space the model runs on a GPU; on your laptop it runs on the CPU.
try:
    import spaces  # only installed on Hugging Face Spaces
    gpu = spaces.GPU
    DEVICE = "cuda"
except ImportError:
    gpu = lambda fn: fn  # no-op locally
    DEVICE = -1  # CPU

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
hf_ner = pipeline("ner", model="d4data/biomedical-ner-all", aggregation_strategy="simple", device=DEVICE)
LABEL_MAP = {"Sign_symptom": "SYMPTOM", "Disease_disorder": "DISEASE", "Medication": "DRUG"}


@gpu
def run_hf(text):
    return hf_ner(text)


def perform_ner(text):
    doc = nlp(text)
    spans = list(doc.ents)

    for ent in run_hf(text):
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