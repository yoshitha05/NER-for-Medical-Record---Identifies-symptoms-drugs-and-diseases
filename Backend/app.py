from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
from NER import perform_ner  # Importing the function from NER.py

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/ner', methods=['POST'])
def analyze_text():
    data = request.get_json()
    text = data.get("text", "")

    if not text.strip():
        return jsonify({"error": "No text provided"}), 400

    try:
        result = perform_ner(text)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"NER processing failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(port=5001, debug=True)
