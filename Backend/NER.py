from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline
MODEL_NAME = "d4data/biomedical-ner-all"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForTokenClassification.from_pretrained(MODEL_NAME)
nlp_pipeline = pipeline("ner", model=model, tokenizer=tokenizer, device=-1)
ALLOWED_ENTITIES = {"Medication", "Sign_symptom", "Disease_disorder"}

def predict_ner(text):
    """Performs NER and filters only drugs, symptoms, and diseases."""
    ner_results = nlp_pipeline(text)
    filtered_results = [ent for ent in ner_results if ent['entity'].split("-")[-1] in ALLOWED_ENTITIES]
    return merge_entities(filtered_results)

def merge_entities(ner_results):
    """Merges subword tokens into full entities."""
    merged = []
    current_entity = None

    for ent in ner_results:
        word = ent['word'].replace("##", "")  # Remove subword markers
        entity_type = ent['entity'].split("-")[-1]  # Extract entity type
        score = float(ent['score'])  # Convert to Python float

        if entity_type in ALLOWED_ENTITIES:
            if ent['entity'].startswith("B-") or (current_entity and current_entity["entity"] != entity_type):
                # If a new entity starts or the entity type changes, store previous and start new
                if current_entity:
                    merged.append(current_entity)
                current_entity = {"word": word, "entity": entity_type, "score": score}
            else:
                # Continue merging the current entity
                current_entity["word"] += " " + word
                current_entity["score"] = max(current_entity["score"], score)  # Keep highest confidence

    if current_entity:
        merged.append(current_entity)

    return merged
