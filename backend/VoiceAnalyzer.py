import librosa
import parselmouth
import numpy as np
from sympy.codegen.cfunctions import isnan

from VoiceTranscriber import VoiceTranscriber


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

        if hnr_db >= 16:
            purity_label = "perfect"
            purity_score = 100
        elif hnr_db >= 12:
            purity_label = "clear"
            purity_score = 70
        elif hnr_db >= 7:
            purity_label = "hazy"
            purity_score = 50
        else:
            purity_label = "poor"
            purity_score = 0

        return {
            "purity_label": purity_label,
            "purity_score": purity_score
        }

    def get_transcriber_data(self, audio_file):
        transcriber_data = self.transcriber.transcribe(audio_file)
        content = transcriber_data['content']
        return {
            "language": transcriber_data['language'],
            "content": content,
            "word_count": len(content.split()),
            "words_per_minute": len(content.split()) / float(transcriber_data['duration']) * 60
        }

    def get_speech_intensity(self, audio_file):
        sound = parselmouth.Sound(audio_file)
        intensity = sound.to_intensity()
        avg_intensity = intensity.get_average()

        if avg_intensity < 60:
            speech_intensity = "silence/whisper"
        elif avg_intensity < 75:
            speech_intensity = "talk/normal"
        else:
            speech_intensity = "loud/shouting"

        return speech_intensity

    def get_jitter_shimmer(self, audio_file):

        sound = parselmouth.Sound(audio_file)
        point_process = parselmouth.praat.call(sound, "To PointProcess (periodic, cc)", 75, 500)

        jitter = parselmouth.praat.call(point_process, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3) * 100
        shimmer = parselmouth.praat.call([sound, point_process], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3,
                                         1.6) * 100
        if isnan(jitter) or isnan(shimmer):
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
        if isnan(hnr_db):
            hnr_db = 0
        return float(hnr_db)

    def get_snr(self, audio_file):
        y, sr = librosa.load(audio_file)

        S = np.abs(librosa.stft(y)) ** 2  # Power spectrogram

        noise_spectrum = np.percentile(S, 10, axis=1)  # Minimum energy per frequency band
        noise_power = np.mean(noise_spectrum)

        signal_power = np.mean(S)

        snr = 10 * np.log10(signal_power / noise_power)
        if isnan(snr):
            snr = 0
        return float(snr)

    def evaluate_audio_quality(self, jitter, shimmer, hnr, snr):

        if snr >= 40:
            snr_score = 1
        elif snr <= 20:
            snr_score = 0
        else:
            snr_score = (snr - 20) / 20

        if hnr >= 15:
            hnr_score = 1
        elif hnr <= 5:
            hnr_score = 0
        else:
            hnr_score = (hnr - 5) / 10

        if jitter <= 2:
            jitter_score = 1
        elif jitter >= 4:
            jitter_score = 0
        else:
            jitter_score = 1 - (jitter - 2) / 2

        if shimmer <= 9:
            shimmer_score = 1
        elif shimmer >= 18:
            shimmer_score = 0
        else:
            shimmer_score = 1 - (shimmer - 9) / 9

        quality = (
                          0.4 * snr_score +
                          0.4 * hnr_score +
                          0.1 * jitter_score +
                          0.1 * shimmer_score
                  ) * 100

        if quality >= 75:
            label = "clean"
        elif quality >= 30:
            label = "normal"
        else:
            label = "poor"

        return quality, label
