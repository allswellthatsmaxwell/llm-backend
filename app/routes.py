import os

from flask import request, Blueprint, Flask, make_response, jsonify

from app.filesystem import FileSystem
from app.transcription import TranscriptionPipeline

app = Flask(__name__)
app_routes = Blueprint("app_routes", __name__)
app.register_blueprint(app_routes)

HOMEDIR = os.path.expanduser("~")
APPDATA_PATH = f"{HOMEDIR}/llmll/dev_app_data"
LOGFILES_DIR = f"{APPDATA_PATH}/logfiles"

filesystem = FileSystem(root=APPDATA_PATH)


@app_routes.route("/transcribe", methods=["POST"])
async def transcribe():
    print("Entering routes.transcribe...")
    pipeline = TranscriptionPipeline(request, filesystem)
    response_data = await pipeline.run()
    return make_response(jsonify(response_data))