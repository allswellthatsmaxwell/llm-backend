import os
import json

from flask import request, Blueprint, Flask, make_response, jsonify
import openai

from app.audio_processing import remove_silence_and_save
from app.filesystem import FileSystem, delete_file

app = Flask(__name__)


async def transcribe(file):
    with open(file, 'rb') as audio:
        transcript = openai.Audio.transcribe("whisper-1", audio)
    print(json.dumps(transcript, indent=4))
    return transcript


class TranscriptionPipeline:
    def __init__(self, request, filesystem: FileSystem):
        user_id = request.args.get('userId', None)
        dest_dir = os.path.join(filesystem.root, user_id, "recordings")
        os.makedirs(dest_dir, exist_ok=True)

        self.audio_data = request.get_data()
        self.destpath = f"{dest_dir}/rec1.wav"
        self.trimmed_path = self.destpath.replace(".wav", "_trimmed.wav")
        app.logger.info(f"userId: {user_id}")
        app.logger.info("TranscriptionPipeline, len(audio_data):", len(self.audio_data))

    def write_audio_data(self):
        app.logger.info(f"Writing to '{self.destpath}'.")
        with open(self.destpath, "wb") as f:
            f.write(self.audio_data)
        app.logger.info("Done writing.")

    def remove_silence(self):
        app.logger.info("Removing silence...")
        has_audio = remove_silence_and_save(self.destpath, self.trimmed_path)
        app.logger.info("Done removing silence.")
        return has_audio

    async def run(self):
        try:
            self.write_audio_data()
            has_audio = self.remove_silence()
            transcript = self._get_transcript(has_audio)
            response_data = {'transcription': transcript}
            return response_data
        except Exception as e:
            app.logger.error(e)
            return {'error': str(e)}

    async def _get_transcript(self, has_audio: bool):
        if has_audio:
            app.logger.info("Transcribing...")
            transcript = await transcribe(self.destpath)
            app.logger.info("Done transcribing.")
            app.logger.info(transcript)
        else:
            app.logger.info("No non-silent audio detected.")
            transcript = "SYSTEM: No audio detected. Output an empty list."
        return transcript

    def _cleanup(self):
        delete_file(self.destpath)
        delete_file(self.trimmed_path)
