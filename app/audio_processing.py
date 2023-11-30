from pydub import AudioSegment
from pydub.silence import detect_nonsilent


def remove_silence_and_save(input_file, output_file) -> bool:
    trimmed_audio = remove_silence(input_file)
    if trimmed_audio:
        trimmed_audio.export(output_file, format="wav")
        return True
    else:
        return False


def remove_silence(audio_file, silence_threshold=-20, min_silence_duration=100, padding=50):
    audio = AudioSegment.from_wav(audio_file)
    nonsilent_ranges = detect_nonsilent(audio, min_silence_len=min_silence_duration, silence_thresh=silence_threshold)

    if not nonsilent_ranges:
        return None

    trimmed_audio = AudioSegment.empty()
    for start, end in nonsilent_ranges:
        start = max(0, start - padding)
        end += padding
        trimmed_audio += audio[start:end]

    return trimmed_audio
