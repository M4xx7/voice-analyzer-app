from pydantic_settings import BaseSettings


class AudioThresholds(BaseSettings):
    HNR_PERFECT: int = 16
    HNR_CLEAR: int = 12
    HNR_HAZY: int = 7

    SNR_MIN: float = 20
    SNR_MAX: float = 40

    JITTER_MIN: float = 2
    JITTER_MAX: float = 4

    SHIMMER_MIN: float = 9
    SHIMMER_MAX: float = 18

    INTENSITY_SILENT: int = 60
    INTENSITY_NORMAL: int = 75

    QUALITY_CLEAR: float = 75
    QUALITY_NORMAL: float = 30

    WEIGHT_SNR: float = 0.4
    WEIGHT_HNR: float = 0.4
    WEIGHT_JITTER: float = 0.1
    WEIGHT_SHIMMER: float = 0.1


settings = AudioThresholds()
