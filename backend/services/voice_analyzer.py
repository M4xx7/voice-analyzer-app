import librosa
import numpy as np
import parselmouth

from core import labels
from services.voice_transcriber import VoiceTranscriber
from core.config import settings
from schemas.audio_analysis import PurityResult
from schemas.transcription import TranscriberData


class VoiceAnalyzer:

    def __init__(self, model_size):
        self.transcriber = VoiceTranscriber(model_size=model_size)

    def get_sound_purity(self, audio_file):
        sound = parselmouth.Sound(audio_file)
        harmonicity = sound.to_harmonicity_cc(time_step=0.01, minimum_pitch=75, silence_threshold=0.1,
                                              periods_per_window=1.0)
        hnr_values = harmonicity.values
        clean_hnr = hnr_values[hnr_values > -199]
        hnr_db = 0

        if len(clean_hnr) > 0:
            hnr_db = clean_hnr.mean()

        if hnr_db >= settings.HNR_PERFECT:
            purity_label = labels.AudioQuality.PERFECT
            purity_score = 100
        elif hnr_db >= settings.HNR_CLEAR:
            purity_label = labels.AudioQuality.CLEAR
            purity_score = 70
        elif hnr_db >= settings.HNR_HAZY:
            purity_label = labels.AudioQuality.HAZY
            purity_score = 50
        else:
            purity_label = labels.AudioQuality.POOR
            purity_score = 0

        return PurityResult(
            label=purity_label,
            score=purity_score
        )


    def get_transcriber_data(self, audio_file):
        transcriber_data = self.transcriber.transcribe(audio_file)
        content = transcriber_data.content

        return TranscriberData(
            language=transcriber_data.language,
            content=content,
            word_count=len(content.split()),
            words_per_minute=len(content.split()) / float(transcriber_data.duration) * 60
        )


    def get_speech_intensity(self, audio_file):
        sound = parselmouth.Sound(audio_file)
        intensity = sound.to_intensity()
        avg_intensity = intensity.get_average()

        if avg_intensity < settings.INTENSITY_SILENT:
            speech_intensity = labels.SpeechIntensity.SILENT
        elif avg_intensity < settings.INTENSITY_NORMAL:
            speech_intensity = labels.SpeechIntensity.NORMAL
        else:
            speech_intensity = labels.SpeechIntensity.LOUD

        return speech_intensity


    def get_jitter_shimmer(self, audio_file):
        sound = parselmouth.Sound(audio_file)
        point_process = parselmouth.praat.call(sound, "To PointProcess (periodic, cc)", 75, 500)

        jitter = parselmouth.praat.call(point_process, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3) * 100
        shimmer = parselmouth.praat.call([sound, point_process], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3,
                                         1.6) * 100
        if np.isnan(jitter) or np.isnan(shimmer):
            jitter = shimmer = 0
        return float(jitter), float(shimmer)


    def get_harmonicity(self, audio_file):
        sound = parselmouth.Sound(audio_file)
        harmonicity = sound.to_harmonicity_cc(time_step=0.01, minimum_pitch=75, silence_threshold=0.1,
                                              periods_per_window=1.0)
        hnr_values = harmonicity.values
        clean_hnr = hnr_values[hnr_values > -199]
        hnr_db = 0
        if len(clean_hnr) > 0:
            hnr_db = clean_hnr.mean()
        if np.isnan(hnr_db):
            hnr_db = 0
        return float(hnr_db)


    def get_snr(self, audio_file):
        y, sr = librosa.load(audio_file)

        S = np.abs(librosa.stft(y)) ** 2

        noise_spectrum = np.percentile(S, 10, axis=1)
        noise_power = np.mean(noise_spectrum)

        signal_power = np.mean(S)

        snr = 10 * np.log10(signal_power / noise_power)
        if np.isnan(snr):
            snr = 0
        return float(snr)


    def evaluate_audio_quality(self, jitter, shimmer, hnr, snr):
        if snr >= settings.SNR_MAX:
            snr_score = 1
        elif snr <= settings.SNR_MIN:
            snr_score = 0
        else:
            snr_score = (snr - 20) / 20

        if hnr >= settings.HNR_CLEAR:
            hnr_score = 1
        elif hnr <= settings.HNR_HAZY:
            hnr_score = 0
        else:
            hnr_score = (hnr - 5) / 10

        if jitter <= settings.JITTER_MIN:
            jitter_score = 1
        elif jitter >= settings.JITTER_MAX:
            jitter_score = 0
        else:
            jitter_score = 1 - (jitter - 2) / 2

        if shimmer <= settings.SHIMMER_MIN:
            shimmer_score = 1
        elif shimmer >= settings.SHIMMER_MAX:
            shimmer_score = 0
        else:
            shimmer_score = 1 - (shimmer - 9) / 9

        quality = (
                          settings.WEIGHT_SNR * snr_score +
                          settings.WEIGHT_HNR * hnr_score +
                          settings.WEIGHT_JITTER * jitter_score +
                          settings.WEIGHT_SHIMMER * shimmer_score
                  ) * 100

        if quality >= settings.QUALITY_CLEAR:
            label = labels.AudioQuality.CLEAR
        elif quality >= settings.QUALITY_NORMAL:
            label = labels.AudioQuality.NORMAL
        else:
            label = labels.AudioQuality.POOR

        return quality, label
