# Voice Analyzer API

Voice Analyzer is a backend API for analyzing audio files that contain human speech.  
It extracts speech-related features, computes acoustic metrics, and evaluates the overall quality of an audio sample.

## Features

- Speech transcription and language detection  
- Speech intensity and audio purity analysis  
- Acoustic feature extraction (jitter, shimmer, HNR, SNR)  
- Audio quality evaluation based on extracted metrics  
- Support for uploaded and recorded audio files  
- Automatic audio format normalization to WAV  

## Notes

This app is designed specifically for **human speech audio**.  
Non-speech or low-quality audio may result in undefined or incomplete metrics.
