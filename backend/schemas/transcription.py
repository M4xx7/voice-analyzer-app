from pydantic import BaseModel


class TranscriptionResult(BaseModel):
    content: str
    language: str
    duration: float

class TranscriberData(BaseModel):
    language: str
    content: str
    word_count: int
    words_per_minute: float

