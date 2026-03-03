from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import tempfile
import filetype
from moviepy import AudioFileClip
from threading import Lock

from VoiceAnalyzer import VoiceAnalyzer

app = FastAPI(title='Voice Analysis API')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

analyzer = VoiceAnalyzer(model_size="small")
analyzer_lock = Lock()


def convert_audio_to_wav(input_path: str) -> str:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        output_path = tmp.name

    with AudioFileClip(input_path) as audio:
        audio.write_audiofile(output_path, logger=None)

    return output_path


@app.post("/analyze")
async def analyze_audio(file: UploadFile = File(...)):
    original_path = f"temp_{file.filename}"

    try:
        with open(original_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

            kind = filetype.guess(original_path)
            if kind is None:
                raise HTTPException(status_code=400, detail="Cannot determine file type")

            file_to_analyze = original_path

            if kind.extension != 'wav':
                file_to_analyze = convert_audio_to_wav(original_path)

        with analyzer_lock:
            sound_purity = analyzer.get_sound_purity(file_to_analyze)
            transript_data = analyzer.get_transcriber_data(file_to_analyze)
            speech_intensity = analyzer.get_speech_intensity(file_to_analyze)

            return {
                "transcription": {
                    "language": transript_data["language"],
                    "content": transript_data["content"],
                    "word_count": transript_data["word_count"],
                    "words_per_minute": transript_data["words_per_minute"]
                },
                "metrics": {
                    "speech_intensity": speech_intensity,
                    "purity_label": sound_purity["purity_label"],
                    "purity_score": sound_purity["purity_score"],
                }
            }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        if original_path and os.path.exists(original_path):
            os.remove(original_path)


@app.post("/evaluate")
async def evaluate_audio(file: UploadFile = File(...)):
    original_path = f"temp_{file.filename}"

    try:
        with open(original_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

            kind = filetype.guess(original_path)
            if kind is None:
                raise HTTPException(status_code=400, detail="Cannot determine file type")

            file_to_analyze = original_path

            if kind.extension != 'wav':
                file_to_analyze = convert_audio_to_wav(original_path)

        with analyzer_lock:
            jitter, shimmer = analyzer.get_jitter_shimmer(file_to_analyze)
            hnr = analyzer.get_harmonicity(file_to_analyze)
            snr = analyzer.get_snr(file_to_analyze)
            quality, label = analyzer.evaluate_audio_quality(jitter, shimmer, hnr, snr)

            return {
                "audio_metrics": {
                    "jitter": jitter,
                    "shimmer": shimmer,
                    "hnr": hnr,
                    "snr": snr
                },
                "score": {
                    "score": quality,
                    "label": label
                }
            }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        if original_path and os.path.exists(original_path):
            os.remove(original_path)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
