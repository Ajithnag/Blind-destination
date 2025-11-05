from __future__ import annotations
import threading
import time
from typing import Optional

try:
    from ultralytics import YOLO  # optional
except Exception:
    YOLO = None  # type: ignore

import cv2


class VisionLoop:
    def __init__(self, enabled: bool, voice_say, demo_mode: bool = True, obstacle_event: Optional[threading.Event] = None, on_obstacle: Optional[callable] = None):
        self.enabled = enabled
        self.voice_say = voice_say
        self.demo_mode = demo_mode
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self._model = None
        self._obstacle_event = obstacle_event
        self._on_obstacle = on_obstacle

    def start(self):
        if not self.enabled:
            return
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)

    def _load_model(self):
        if YOLO and not self.demo_mode:
            try:
                self._model = YOLO("yolov8n.pt")  # small CPU-friendly model
            except Exception:
                self._model = None

    def _run(self):
        # announce start
        self.voice_say("Starting vision safety. Camera on.")
        self._load_model()
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.voice_say("Warning. Could not access camera.")
            return
        last_alert = 0.0
        try:
            while not self._stop.is_set():
                ret, frame = cap.read()
                if not ret:
                    time.sleep(0.1)
                    continue
                alert_msg = None
                if self._model is not None:
                    # Real detection
                    results = self._model(frame, verbose=False)
                    names = self._model.names if hasattr(self._model, "names") else {}
                    for r in results:
                        if getattr(r, "boxes", None) is not None:
                            for b in r.boxes:
                                cls = int(b.cls[0]) if hasattr(b, "cls") else None
                                name = names.get(cls, "object") if isinstance(names, dict) else "object"
                                if name in ("person", "bicycle", "car", "motorbike", "bus", "truck"):
                                    alert_msg = f"{name} ahead"
                                    break
                        if alert_msg:
                            break
                else:
                    # Demo heuristic: simple motion alert every few seconds
                    now = time.time()
                    if now - last_alert > 6:
                        alert_msg = "Stay alert. Checking surroundings."
                        last_alert = now
                if alert_msg:
                    self.voice_say(alert_msg)
                    # Signal obstacle to main loop
                    if self._obstacle_event:
                        self._obstacle_event.set()
                    if self._on_obstacle:
                        try:
                            self._on_obstacle(alert_msg)
                        except Exception:
                            pass
                # Keep frame rate modest
                time.sleep(0.2)
        finally:
            cap.release()
            self.voice_say("Vision safety stopped.")
