from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline

# Load NER model
MODEL_NAME = "d4data/biomedical-ner-all"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForTokenClassification.from_pretrained(MODEL_NAME)
nlp_pipeline = pipeline("ner", model=model, tokenizer=tokenizer)

def predict_ner(text):
    ner_results = nlp_pipeline(text)
    merged_results = merge_entities(ner_results)  # Apply merging
    return merged_results

def merge_entities(ner_results):
    merged = []
    current_entity = None
    
    for ent in ner_results:
        word = ent['word'].replace("##", "")  # Remove subword marker
        
        if ent['entity'].startswith("B-"):
            if current_entity:
                merged.append(current_entity)  # Save previous entity
            current_entity = {
                "word": word,
                "entity": ent['entity'][2:],  # Remove B- or I- prefix
                "score": round(ent['score'], 2)  # Round confidence score
            }
        
        elif ent['entity'].startswith("I-") and current_entity:
            current_entity["word"] += word  # Merge subword
        
        else:
            if current_entity:
                merged.append(current_entity)  # Save previous entity
            current_entity = {
                "word": word,
                "entity": ent['entity'][2:],  # Remove B- or I- prefix
                "score": round(ent['score'], 2)
            }
    
    if current_entity:
        merged.append(current_entity)  # Save the last entity
    
    return merged
