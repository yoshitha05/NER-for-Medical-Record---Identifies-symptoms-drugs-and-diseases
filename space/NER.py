# `spaces` must be imported before torch/transformers on a ZeroGPU Space.
# The model runs on the CPU: DistilBERT is small and fast enough, and CPU time has no daily
# quota (free ZeroGPU time runs out quickly for visitors who are not logged in).
try:
    import spaces  # only installed on Hugging Face Spaces

    @spaces.GPU
    def _gpu_placeholder():  # a ZeroGPU Space needs at least one GPU function to start; never called
        pass
except ImportError:
    pass

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
# Words AFTER an entity ("absent", "ruled out") are handled by negated_by_next_words() below,
# because negspacy would apply them to the whole sentence before them.
negation_terms.remove_patterns({"following_negations": negation_terms.get_patterns()["following_negations"]})
negex = nlp.add_pipe("negex", config={"neg_termset": negation_terms.get_patterns()})

FOLLOWING_NEGATIONS = ("ruled out", "absent", "not present", "negative", "unlikely", "excluded", "declined", "free")
FILLER_WORDS = {"is", "was", "are", "were", "been", "has", "have", "test", "tests", "also", "now"}


def negated_by_next_words(ent):
    """'Malaria ruled out', 'constipation is absent': only the entity right before the cue is negated."""
    next_words = [t.lower_ for t in ent.doc[ent.end: ent.end + 5] if t.lower_ not in FILLER_WORDS]
    return " ".join(next_words).startswith(FOLLOWING_NEGATIONS)

# 3. Hugging Face model fills in what the dictionary misses
hf_ner = pipeline("ner", model="d4data/biomedical-ner-all", aggregation_strategy="simple", device=-1)  # CPU
LABEL_MAP = {"Sign_symptom": "SYMPTOM", "Disease_disorder": "DISEASE", "Medication": "DRUG"}


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
    for ent in doc.ents:
        if not ent._.negex and negated_by_next_words(ent):
            ent._.negex = True

    return {
        "text": text,
        "ents": [
            {"text": e.text, "label": e.label_, "start": e.start_char, "end": e.end_char, "negated": e._.negex}
            for e in doc.ents
        ],
    }


if __name__ == "__main__":
    print(perform_ner("Patient denies fever and burning micturition. No history of diabetes. Has headache. Given Dolo 650."))