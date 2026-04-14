from faster_whisper import WhisperModel

from schemas.transcription import TranscriptionResult


class VoiceTranscriber:
    def __init__(self, model_size="small"):
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")

    def transcribe(self, audio_path):
        segments, info = self.model.transcribe(
            audio_path,
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
            word_timestamps=False
        )

        segments = list(segments)

        full_text = " ".join([segment.text for segment in segments]).strip()

        return TranscriptionResult(
            content=full_text,
            language=info.language,
            duration=info.duration
        )
