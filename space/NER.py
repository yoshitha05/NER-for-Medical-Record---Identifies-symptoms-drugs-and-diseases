import spacy
from spacy.util import filter_spans
from transformers import pipeline

# 1. spaCy pipeline with a small medical dictionary
nlp = spacy.blank("en")
ruler = nlp.add_pipe("entity_ruler", config={"phrase_matcher_attr": "LOWER"})
ruler.add_patterns(
    [{"label": "DISEASE", "pattern": t} for t in ["diabetes", "hypertension", "asthma", "dengue", "malaria", "typhoid", "migraine"]]
    + [{"label": "DRUG", "pattern": t} for t in ["paracetamol", "dolo 650", "metformin", "azithromycin", "ibuprofen", "insulin"]]
    + [{"label": "SYMPTOM", "pattern": t} for t in ["fever", "cough", "headache", "vomiting", "fatigue", "chest pain", "body pain"]]
)

# 2. Hugging Face model fills in what the dictionary misses.
# On a Hugging Face ZeroGPU Space it runs on a GPU; on your laptop it runs on the CPU.
try:
    import spaces  # only installed on Hugging Face Spaces
    gpu = spaces.GPU
    DEVICE = "cuda"
except ImportError:
    gpu = lambda fn: fn  # no-op locally
    DEVICE = -1  # CPU

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

    return {
        "text": text,
        "ents": [
            {"text": e.text, "label": e.label_, "start": e.start_char, "end": e.end_char}
            for e in doc.ents
        ],
    }


if __name__ == "__main__":
    print(perform_ner("Patient has fever and burning micturition, known diabetes, given Dolo 650 and Montair LC."))