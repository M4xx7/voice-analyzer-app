from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.concurrency import run_in_threadpool
import shutil
import os
import uuid
import filetype
from threading import Lock

from services.voice_analyzer import VoiceAnalyzer
from schemas.audio_analysis import PurityResult
from schemas.transcription import TranscriberData
from core.audio_utils import convert_audio_to_wav

router = APIRouter()

analyzer = VoiceAnalyzer(model_size="small")
analyzer_lock = Lock()


@router.post("/analyze")
async def analyze_audio(file: UploadFile = File(...)):
    unique_id = uuid.uuid4().hex
    original_path = f"temp_{unique_id}_{file.filename}"

    try:
        with open(original_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        kind = filetype.guess(original_path)
        if kind is None:
            raise HTTPException(status_code=400, detail="Cannot determine file type")

        file_to_analyze = original_path

        if kind.extension != "wav":
            file_to_analyze = convert_audio_to_wav(original_path)

        with analyzer_lock:
            sound_purity = await run_in_threadpool(analyzer.get_sound_purity, file_to_analyze)
            transcript_data = await run_in_threadpool(analyzer.get_transcriber_data, file_to_analyze)
            speech_intensity = analyzer.get_speech_intensity(file_to_analyze)

        return {
            "transcription": TranscriberData(**transcript_data),
            "metrics": {
                "speech_intensity": speech_intensity,
                "purity": PurityResult(**sound_purity),
            }
        }

    finally:
        if os.path.exists(original_path):
            os.remove(original_path)