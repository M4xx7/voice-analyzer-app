from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os
import uuid
import filetype
from threading import Lock

from services.voice_analyzer import VoiceAnalyzer
from schemas.audio_analysis import AudioAnalysisResult, PurityResult
from core.audio_utils import convert_audio_to_wav

router = APIRouter()

analyzer = VoiceAnalyzer(model_size="small")
analyzer_lock = Lock()


@router.post("/evaluate")
async def evaluate_audio(file: UploadFile = File(...)):
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

            purity_data = analyzer.get_sound_purity(file_to_analyze)
            transcriber_data = analyzer.get_transcriber_data(file_to_analyze)
            speech_intensity = analyzer.get_speech_intensity(file_to_analyze)

            jitter, shimmer = analyzer.get_jitter_shimmer(file_to_analyze)
            hnr = analyzer.get_harmonicity(file_to_analyze)
            snr = analyzer.get_snr(file_to_analyze)
            quality, label = analyzer.evaluate_audio_quality(jitter, shimmer, hnr, snr)

        return AudioAnalysisResult(
            purity=purity_data,
            transcriber=transcriber_data,
            speech_intensity=speech_intensity,

            jitter=jitter,
            shimmer=shimmer,
            harmonicity=hnr,
            snr=snr,

            quality_score=quality,
            quality_label=label
        )

    finally:
        if os.path.exists(original_path):
            os.remove(original_path)