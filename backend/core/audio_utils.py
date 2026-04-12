import tempfile
from moviepy import AudioFileClip


def convert_audio_to_wav(input_path: str) -> str:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        output_path = tmp.name

    with AudioFileClip(input_path) as audio:
        audio.write_audiofile(output_path, logger=None)

    return output_path