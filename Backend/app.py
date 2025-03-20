from flask import Flask, request, jsonify
from flask_cors import CORS
from NER import predict_ner  # Import modified NER function
import traceback

app = Flask(__name__)
CORS(app)  # Enable CORS

@app.route('/ner', methods=['POST'])
def ner():
    try:
        data = request.get_json()
        text = data.get("text", "").strip()

        if not text:
            return jsonify({"error": "No text provided"}), 400  # Handle empty input

        entities = predict_ner(text)

        # Ensure all numbers are converted to float
        for entity in entities:
            entity["score"] = float(entity["score"])

        return jsonify({'entities': entities})

    except Exception as e:
        print("Error:", str(e))
        traceback.print_exc()  # Show full error in the console
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Run Flask on port 5001
