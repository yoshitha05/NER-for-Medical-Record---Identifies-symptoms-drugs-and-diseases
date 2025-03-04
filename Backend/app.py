from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Load NER model
MODEL_NAME = "d4data/biomedical-ner-all"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForTokenClassification.from_pretrained(MODEL_NAME)
nlp_pipeline = pipeline("ner", model=model, tokenizer=tokenizer)

def predict_ner(text):
    ner_results = nlp_pipeline(text)
    return [{"word": ent['word'], "entity": ent['entity'], "score": float(ent['score'])} for ent in ner_results]

@app.route('/ner', methods=['POST'])
def ner():
    try:
        data = request.get_json()
        text = data.get("text", "")

        if not text:
            return jsonify({"error": "No text provided"}), 400  # Return error if text is empty

        entities = predict_ner(text)
        return jsonify({'entities': entities})

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Catch server errors

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Ensure Flask runs on port 5001
