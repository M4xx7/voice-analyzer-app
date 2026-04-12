from enum import Enum


class AudioQuality(str, Enum):
    PERFECT = "perfect"
    CLEAR = "clear"
    NORMAL = "normal"
    HAZY = "hazy"
    POOR = "poor"


class SpeechIntensity(str, Enum):
    SILENT = "silence/whisper"
    NORMAL = "talk/normal"
    LOUD = "loud/shouting"
