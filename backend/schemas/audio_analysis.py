from pydantic import BaseModel
from schemas.transcription import TranscriberData


class PurityResult(BaseModel):
    label: str
    score: int


class AudioAnalysisResult(BaseModel):
    purity: PurityResult
    transcriber: TranscriberData
    speech_intensity: str
    jitter: float
    shimmer: float
    harmonicity: float
    snr: float
    quality_score: float
    quality_label: str
