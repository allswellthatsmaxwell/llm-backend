import os

from flask import request, Blueprint, Flask, make_response, jsonify
import requests

from app.filesystem import FileSystem
from app.transcription import TranscriptionPipeline

app = Flask(__name__)
app_routes = Blueprint("app_routes", __name__)

HOMEDIR = os.path.expanduser("~")
APPDATA_PATH = f"{HOMEDIR}/llmll/dev_app_data"
LOGFILES_DIR = f"{APPDATA_PATH}/logfiles"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

filesystem = FileSystem(root=APPDATA_PATH)


@app_routes.route("/transcribe", methods=["POST"])
async def transcribe():
    print("Entering routes.transcribe...")
    pipeline = TranscriptionPipeline(request, filesystem)
    response_data = await pipeline.run()
    return make_response(jsonify(response_data))


@app_routes.route("/chat", methods=["POST"])
async def chat():
    print("Entering routes.chat...")
    incoming_request_data = request.get_json()
    print(f"INCOMING_REQUEST_DATA: {incoming_request_data}")
    openai_url = 'https://api.openai.com/v1/chat/completions'

    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json'
    }

    response = requests.post(openai_url, headers=headers, json=incoming_request_data)
    print(f"RESPONSE: {response}")
    print(f"RESPONSE.TEXT: {response.text}")
    print(f"RESPONSE.JSON(): {response.json()}")

    return response.json(), response.status_code
    # response_data = "hi"
    # return make_response(jsonify(response_data))
    # response_data = await pipeline.run()
    # return make_response(jsonify(response_data))
