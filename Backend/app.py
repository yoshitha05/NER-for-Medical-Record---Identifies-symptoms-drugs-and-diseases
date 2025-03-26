from flask import Flask, send_from_directory, request, jsonify
import os
from flask_cors import CORS  # Import CORS
from NER import perform_ner  # Importing the function from NER.py

app = Flask(__name__, static_folder="templates/build", static_url_path="")
CORS(app)  # Enable CORS for all routes

@app.route("/")
def serve_react():
    return send_from_directory("templates/build", "index.html")

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
