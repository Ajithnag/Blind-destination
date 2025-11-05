from __future__ import annotations
import os
import random
from dataclasses import dataclass
from typing import List, Optional, Dict

import requests

from utils import minutes_to_eta_str, now_plus_minutes


@dataclass
class RouteOption:
    mode: str  # walking, driving, transit
    duration_min: int
    distance_km: float
    summary: str
    provider: str
    steps: List[str]


class Router:
    def __init__(self, demo_mode: bool, google_key: str = "", ors_key: str = ""):
        self.demo_mode = demo_mode
        self.google_key = google_key
        self.ors_key = ors_key

    def get_routes(self, origin: str, destination: str) -> List[RouteOption]:
        if self.demo_mode or not (self.google_key or self.ors_key):
            return self._demo_routes(destination)
        # Prefer Google if key provided; else ORS
        try:
            if self.google_key:
                return self._google_routes(origin, destination)
            elif self.ors_key:
                return self._ors_routes(origin, destination)
        except Exception:
            pass
        # fallback to demo
        return self._demo_routes(destination)

    def _demo_routes(self, destination: str) -> List[RouteOption]:
        random.seed(destination)
        walk = RouteOption(
            mode="walking",
            duration_min=random.randint(10, 45),
            distance_km=round(random.uniform(0.8, 3.5), 2),
            summary=f"Walk to {destination} via Main Street",
            provider="demo",
            steps=[
                "Head north",
                "Turn right at the second intersection",
                "Continue for 500 meters",
                "Destination on your left",
            ],
        )
        drive = RouteOption(
            mode="driving",
            duration_min=random.randint(5, 20),
            distance_km=round(random.uniform(1.0, 5.0), 2),
            summary=f"Drive to {destination} via Central Ave",
            provider="demo",
            steps=[
                "Start driving east",
                "Merge onto Central Ave",
                "Take exit 3 toward Downtown",
                "Arrive at destination",
            ],
        )
        transit = RouteOption(
            mode="transit",
            duration_min=random.randint(12, 40),
            distance_km=round(random.uniform(1.2, 6.0), 2),
            summary=f"Bus 24 to {destination} then 3-minute walk",
            provider="demo",
            steps=[
                "Walk to Bus Stop A",
                "Take Bus 24 for 3 stops",
                "Walk 200 meters south",
                "Destination on your right",
            ],
        )
        return [walk, drive, transit]

    def _google_routes(self, origin: str, destination: str) -> List[RouteOption]:
        # Minimal example using Google Directions API v1 (requires billing)
        # This function fetches walking and driving; transit requires extra params depending on region
        base = "https://maps.googleapis.com/maps/api/directions/json"
        modes = ["walking", "driving"]
        options: List[RouteOption] = []
        for mode in modes:
            params = {"origin": origin, "destination": destination, "mode": mode, "key": self.google_key}
            r = requests.get(base, params=params, timeout=10)
            r.raise_for_status()
            data = r.json()
            if data.get("routes"):
                route = data["routes"][0]
                leg = route["legs"][0]
                dur_min = int(leg["duration"]["value"]) // 60
                dist_km = round(leg["distance"]["value"] / 1000.0, 2)
                steps = [s["html_instructions"] for s in leg.get("steps", [])]
                options.append(
                    RouteOption(
                        mode=mode,
                        duration_min=dur_min,
                        distance_km=dist_km,
                        summary=route.get("summary", f"{mode.title()} route"),
                        provider="google",
                        steps=[_strip_html(x) for x in steps],
                    )
                )
        return options

    def _ors_routes(self, origin: str, destination: str) -> List[RouteOption]:
        # Minimal example using OpenRouteService Directions API
        # Note: requires geocoding origin/destination to coordinates (not implemented fully here)
        return []


def describe_route(option: RouteOption) -> str:
    return (
        f"{option.mode} takes {minutes_to_eta_str(option.duration_min)}, "
        f"about {option.distance_km} kilometers, via {option.summary}."
    )


def _strip_html(s: str) -> str:
    import re
    return re.sub("<.*?>", " ", s).replace("  ", " ").strip()
