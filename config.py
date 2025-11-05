import os
from dotenv import load_dotenv

load_dotenv()

DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"
VOICE_STT_ENGINE = os.getenv("VOICE_STT_ENGINE", "").strip().lower()  # 'vosk' or 'sr'
VOSK_MODEL_PATH = os.getenv("VOSK_MODEL_PATH", "").strip()
ENABLE_VISION = os.getenv("ENABLE_VISION", "false").lower() == "true"

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "").strip()
ORS_API_KEY = os.getenv("ORS_API_KEY", "").strip()

DEFAULT_CITY = os.getenv("DEFAULT_CITY", "").strip()
DEFAULT_LAT = os.getenv("DEFAULT_LAT", "").strip()
DEFAULT_LON = os.getenv("DEFAULT_LON", "").strip()
