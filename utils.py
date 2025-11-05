import time
from datetime import datetime, timedelta
from typing import Tuple, Dict, Any

import requests


def minutes_to_eta_str(minutes: int) -> str:
    if minutes <= 0:
        return "arriving now"
    if minutes == 1:
        return "1 minute"
    return f"{minutes} minutes"


def now_plus_minutes(minutes: int) -> str:
    eta = datetime.now() + timedelta(minutes=minutes)
    return eta.strftime("%I:%M %p").lstrip("0")


def sleep_seconds(s: float):
    try:
        time.sleep(s)
    except KeyboardInterrupt:
        pass


def get_approx_location() -> Dict[str, Any]:
    """Return approximate location via IP geolocation.

    Returns keys: city, region, country, lat, lon, display.
    On failure, returns empty dict.
    """
    try:
        # ipapi.co is a public, no-auth endpoint for coarse IP geolocation
        r = requests.get("https://ipapi.co/json/", timeout=5)
        r.raise_for_status()
        data = r.json()
        city = data.get("city", "")
        region = data.get("region", "")
        country = data.get("country_name", "")
        lat = data.get("latitude") or data.get("lat")
        lon = data.get("longitude") or data.get("lon")
        display = ", ".join([x for x in [city, region, country] if x])
        return {"city": city, "region": region, "country": country, "lat": lat, "lon": lon, "display": display}
    except Exception:
        return {}
