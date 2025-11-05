# Blind Navigation Assistant (Voice-Only)

A Windows-friendly Python project that provides a voice-driven navigation assistant with optional computer vision safety alerts.

Core capabilities:
- Voice-only interaction: speaks and listens to the user (destination, mode choice, confirmations)
- Routing: shortest routes for walking, driving, and public transit, with ETAs and step-by-step guidance
- Continuous guidance: minute-by-minute ETA updates during navigation
- Vision safety loop (optional): camera-based alerts about surroundings (people, vehicles, obstacles) when enabled

This repository includes a fully runnable "demo mode" that works without any API keys or ML models installed. In demo mode, routing and vision are simulated to let you experience the voice flow immediately.

## Project Structure

```
blind_nav_assistant/
  README.md
  requirements.txt
  .env.example
  src/
    main.py
    config.py
    voice_io.py
    routing.py
    vision.py
    utils.py
```

- `src/main.py`: Orchestrates the end-to-end experience.
- `src/config.py`: Loads environment variables and feature flags (demo mode, API keys, etc.).
- `src/voice_io.py`: Text-to-speech (pyttsx3) and optional speech-to-text (Vosk / SpeechRecognition).
- `src/routing.py`: Integrates with Google Directions API and OpenRouteService as fallback; demo mode stubs.
- `src/vision.py`: Optional YOLO-based detection via `ultralytics` (if installed) with a safe demo fallback.
- `src/utils.py`: Shared helpers.

## Requirements

Windows 10/11, Python 3.10+

## Quick Start (Demo Mode: No API keys needed)

1) Create and activate a virtual environment (PowerShell):

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Install dependencies:

```
pip install -r requirements.txt
```

3) Run in demo mode (no camera or ML required):

```
python -m src.main --demo
```

- The assistant will use Windows TTS to speak prompts.
- You can reply by voice (if you later install STT) or press Enter to use keyboard input.
- It will simulate routes for walking, driving, and transit, and a guidance loop with minute-by-minute ETA updates.

## Optional: Real Routing and Vision

To enable real routing and/or vision:

1) Copy `.env.example` to `.env` and fill in keys/flags:

- `GOOGLE_MAPS_API_KEY` or `ORS_API_KEY` for routing
- `DEMO_MODE=false` to disable demo routing and vision
- `VOICE_STT_ENGINE=vosk` (recommended offline) or `VOICE_STT_ENGINE=sr` (SpeechRecognition)
- `VOSK_MODEL_PATH` to a downloaded Vosk model directory (e.g., `models\vosk-model-small-en-us-0.15`)
- `ENABLE_VISION=true`

2) Install optional packages for STT and YOLO:

```
pip install vosk ultralytics
```

3) Download a Vosk English model:

- Models: https://alphacephei.com/vosk/models
- Unzip to `models/` and set `VOSK_MODEL_PATH` in `.env`.

4) Run with real APIs and vision:

```
python -m src.main
```

## Notes on APIs and Privacy

- You must bring your own API keys. Do not commit them; keep them in `.env`.
- Vision processing runs locally. If enabled, it accesses your default webcam.
- Always ensure the user consents to camera/microphone use.

## Troubleshooting

- If TTS is silent, check Windows audio output and that `pyttsx3` is installed.
- If `vosk` is not installed or no model is provided, the app falls back to keyboard input.
- If APIs are not configured, the app runs in demo routing mode.

## Roadmap

- Haptics integration (vibration cues)
- Map matching to improve step-by-step precision
- On-device small-vision model for low-power devices
- Edge-case handling (bad GPS, indoor environments)

## License

For personal and educational use. Replace or add a license as needed.
