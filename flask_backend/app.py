from flask import Flask, request, jsonify
from model import probe_model_5l_profit  # Import your model logic
import json

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    This endpoint handles the file upload and processes the data using model.py.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.json'):
        # 
        file_content = file.read()
        
        # Convert bytes to string (if necessary)
        data_string = file_content.decode('utf-8')  # Decode if it's bytes
        
        # Load the JSON data
        data = json.loads(data_string)
        # print(type(data))
        result = probe_model_5l_profit(data["data"])
        return jsonify(result), 200

    return jsonify({"error": "Invalid file type. Only JSON files are allowed."}), 400

if __name__ == '__main__':
    app.run(debug=True)
