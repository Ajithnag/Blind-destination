from __future__ import annotations
import sys
import threading
from typing import Optional

import pyttsx3

try:
    import speech_recognition as sr  # optional
except Exception:
    sr = None  # type: ignore

try:
    from vosk import Model, KaldiRecognizer  # optional
    import json
except Exception:
    Model = None  # type: ignore
    KaldiRecognizer = None  # type: ignore
    json = None  # type: ignore


class VoiceIO:
    def __init__(self, stt_engine: str = "", vosk_model_path: str = ""):
        self.tts = pyttsx3.init()
        # Tune for clarity and speed
        self.tts.setProperty("rate", 185)
        self.tts.setProperty("volume", 1.0)

        self._stt_engine = stt_engine
        self._vosk_model_path = vosk_model_path
        self._vosk_model = None
        if self._stt_engine == "vosk" and Model and vosk_model_path:
            try:
                self._vosk_model = Model(vosk_model_path)
            except Exception:
                self._vosk_model = None

        self._tts_lock = threading.Lock()

    def say(self, text: str, wait: bool = True):
        with self._tts_lock:
            self.tts.say(text)
            self.tts.runAndWait()
        if not wait:
            pass

    def ask(self, prompt: str, timeout: Optional[int] = None) -> str:
        # Speak prompt, then attempt STT, else fallback to keyboard input
        self.say(prompt)
        if self._stt_engine == "vosk" and self._vosk_model and KaldiRecognizer:
            return self._listen_vosk(timeout=timeout)
        elif self._stt_engine == "sr" and sr:
            return self._listen_sr(timeout=timeout)
        else:
            # Keyboard fallback for demo
            sys.stdout.write("\nType your response and press Enter: ")
            sys.stdout.flush()
            return input().strip()

    def _listen_sr(self, timeout: Optional[int] = None) -> str:
        if not sr:
            return ""
        r = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                audio = r.listen(source, timeout=timeout or 5, phrase_time_limit=10)
                text = r.recognize_google(audio)
                return text
            except Exception:
                return ""

    def _listen_vosk(self, timeout: Optional[int] = None) -> str:
        if not (Model and KaldiRecognizer and self._vosk_model):
            return ""
        import pyaudio  # provided by SpeechRecognition dependency stack
        pa = pyaudio.PyAudio()
        stream = pa.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
        stream.start_stream()
        rec = KaldiRecognizer(self._vosk_model, 16000)
        try:
            # Listen for a few seconds
            for _ in range(0, 16000 // 800):
                data = stream.read(4000, exception_on_overflow=False)
                if rec.AcceptWaveform(data):
                    res = rec.Result()
                    try:
                        obj = json.loads(res)
                        return obj.get("text", "").strip()
                    except Exception:
                        return ""
            # final partial
            final = rec.FinalResult()
            try:
                obj = json.loads(final)
                return obj.get("text", "").strip()
            except Exception:
                return ""
        finally:
            stream.stop_stream()
            stream.close()
            pa.terminate()
