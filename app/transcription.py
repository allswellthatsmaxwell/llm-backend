import os
import json

from flask import request, Blueprint, Flask, make_response, jsonify
from openai import OpenAI

client = OpenAI()

from app.audio_processing import remove_silence_and_save
from app.filesystem import FileSystem, delete_file

app = Flask(__name__)

EXT = "m4a"


async def _transcribe(fpath) -> str:
    print(f"_transcribe.fpath={fpath}")
    with open(fpath, 'rb') as audio_file:
        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
    # print(json.dumps(transcript, indent=4))
    return transcript.text


class TranscriptionPipeline:
    def __init__(self, request, filesystem: FileSystem):
        user_id = request.args.get('userId', None)
        if user_id:
            dest_dir = os.path.join(filesystem.root, user_id, "recordings")
        else:
            dest_dir = os.path.join(filesystem.root, "recordings")
        os.makedirs(dest_dir, exist_ok=True)

        self.audio_data = request.get_data()
        self.destpath = f"{dest_dir}/rec1.{EXT}"
        self.trimmed_path = self.destpath.replace(f".{EXT}", f"_trimmed.{EXT}")
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
            print("Successfully wrote audio data.")
            has_audio = True # self.remove_silence()
            transcript = await self._get_transcript(has_audio)
            print("Successfully got transcript.")
            response_data = {'transcription': transcript}
            return response_data
        except Exception as e:
            app.logger.error(e)
            return {'error': str(e)}

    async def _get_transcript(self, has_audio: bool):
        if has_audio:
            app.logger.info("Transcribing...")
            transcript = await _transcribe(self.destpath)
            app.logger.info("Done transcribing.")
            app.logger.info(transcript)
        else:
            app.logger.info("No non-silent audio detected.")
            transcript = "SYSTEM: No audio detected. Output an empty list."
        return transcript

    def _cleanup(self):
        delete_file(self.destpath)
        delete_file(self.trimmed_path)
