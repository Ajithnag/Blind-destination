from __future__ import annotations
import threading
import time
from typing import Optional, Callable

try:
    from plyer import tts
except Exception:
    tts = None  # type: ignore


class MobileTTS:
    def say(self, text: str):
        if tts:
            try:
                tts.speak(text)
                return
            except Exception:
                pass
        print(f"[TTS] {text}")


class VisionSimulator:
    def __init__(self, on_obstacle: Optional[Callable[[str], None]] = None, interval_sec: int = 15):
        self._on_obstacle = on_obstacle
        self._interval = interval_sec
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)

    def _run(self):
        last = 0.0
        while not self._stop.is_set():
            now = time.time()
            if now - last >= self._interval:
                last = now
                if self._on_obstacle:
                    try:
                        self._on_obstacle("Obstacle ahead. Please wait.")
                    except Exception:
                        pass
            time.sleep(0.25)
