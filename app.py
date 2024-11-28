from flask import Flask, request, jsonify
from azure.storage.blob import BlobServiceClient
import requests

app = Flask(__name__)

# Azure Blob and Translator settings
BLOB_CONNECTION_STRING = "your_blob_connection_string"
TRANSLATOR_KEY = "your_translator_key"
TRANSLATOR_ENDPOINT = "https://api.cognitive.microsofttranslator.com"

# Upload endpoint
@app.route('/translate', methods=['POST'])
def translate_file():
    file = request.files['file']
    target_language = request.form['language']
    
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400
    
    # Read file content
    file_content = file.read().decode('utf-8')
    
    # Translate content
    headers = {
        'Ocp-Apim-Subscription-Key': TRANSLATOR_KEY,
        'Content-Type': 'application/json',
    }
    translate_url = f"{TRANSLATOR_ENDPOINT}/translate?api-version=3.0&to={target_language}"
    body = [{'text': file_content}]
    response = requests.post(translate_url, headers=headers, json=body)
    translated_text = response.json()[0]['translations'][0]['text']
    
    # Upload translated file to Blob Storage
    blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
    container_name = "translated-files"
    blob_name = file.filename.split('.')[0] + f"_{target_language}.txt"
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    blob_client.upload_blob(translated_text, overwrite=True)
    
    # Generate download link
    download_url = f"https://youraccount.blob.core.windows.net/{container_name}/{blob_name}"
    return jsonify({'downloadUrl': download_url})

if __name__ == "__main__":
    app.run(debug=True)