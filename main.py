from __future__ import annotations
import argparse
from typing import Optional
import threading

from config import DEMO_MODE, VOICE_STT_ENGINE, VOSK_MODEL_PATH, ENABLE_VISION, GOOGLE_MAPS_API_KEY, ORS_API_KEY
from voice_io import VoiceIO
from routing import Router, describe_route, RouteOption
from vision import VisionLoop
from utils import minutes_to_eta_str, now_plus_minutes, sleep_seconds, get_approx_location


def choose_route(voice: VoiceIO, options: list[RouteOption]) -> Optional[RouteOption]:
    # Announce options with ETAs
    voice.say("I found these options. Say one, two, or three to choose.")
    for idx, opt in enumerate(options, start=1):
        voice.say(f"Option {idx}: {describe_route(opt)}")

    resp = voice.ask("Which option do you want? One, two, or three?")
    resp_num = None
    tokens = resp.lower().split()
    for token in tokens:
        if token in ("one", "1"):
            resp_num = 1
            break
        if token in ("two", "2"):
            resp_num = 2
            break
        if token in ("three", "3"):
            resp_num = 3
            break
    # Allow choosing by mode name
    if resp_num is None:
        chosen_mode = None
        for t in tokens:
            if t in ("walk", "walking"):
                chosen_mode = "walking"
                break
            if t in ("drive", "driving", "car"):
                chosen_mode = "driving"
                break
            if t in ("bus", "transit", "public"):
                chosen_mode = "transit"
                break
        if chosen_mode:
            for opt in options:
                if opt.mode == chosen_mode:
                    return opt
    if resp_num and 1 <= resp_num <= len(options):
        return options[resp_num - 1]
    voice.say("I didn't catch that. I'll pick the shortest route.")
    return sorted(options, key=lambda x: x.duration_min)[0]


def guidance_loop(voice: VoiceIO, selection: RouteOption, obstacle_event: Optional[threading.Event] = None, demo_mode: bool = True, auto_start: bool = False):
    voice.say(f"Starting {selection.mode} guidance. Estimated time {minutes_to_eta_str(selection.duration_min)}. Arrival around {now_plus_minutes(selection.duration_min)}.")
    remaining = selection.duration_min
    # Speak the first few steps more often, then minute-by-minute updates
    for step in selection.steps:
        voice.say(step)
        sleep_seconds(1.0)

    # Wait for explicit start unless auto-start is enabled
    if not auto_start:
        while True:
            resp = voice.ask("Say start when you are ready to begin, or say go.")
            r = resp.strip().lower()
            if any(k in r for k in ("start", "go", "begin", "proceed")):
                voice.say("Starting now. Stay safe and follow the instructions.")
                break
            else:
                voice.say("Okay, I will wait. Let me know when to start.")

    while remaining > 0:
        # Pause if obstacle signaled
        if obstacle_event is not None and obstacle_event.is_set():
            wait_seconds = 120
            voice.say("Obstacle ahead. Please wait. I will let you know when it's safe to continue.")
            sleep_seconds(wait_seconds)
            if obstacle_event is not None:
                obstacle_event.clear()
            voice.say("It should be clear now. You can proceed.")
        if remaining == 1:
            voice.say("One minute remaining.")
        else:
            voice.say(f"{remaining} minutes remaining.")
        remaining -= 1
        sleep_seconds(3.0 if DEMO_MODE else 60.0)
    voice.say("You have arrived at your destination.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="Force demo mode")
    parser.add_argument("--destination", type=str, default="", help="Destination to navigate to (skips prompt)")
    parser.add_argument("--no-vision", action="store_true", help="Disable vision safety loop")
    parser.add_argument("--auto-select", action="store_true", help="Automatically select the shortest route (non-interactive)")
    parser.add_argument("--vision", action="store_true", help="Force-enable vision safety loop (camera)")
    parser.add_argument("--auto-start", action="store_true", help="Start guidance immediately without waiting for confirmation")
    args = parser.parse_args()

    demo_mode = DEMO_MODE or args.demo

    voice = VoiceIO(stt_engine=VOICE_STT_ENGINE, vosk_model_path=VOSK_MODEL_PATH)
    router = Router(demo_mode=demo_mode, google_key=GOOGLE_MAPS_API_KEY, ors_key=ORS_API_KEY)

    voice.say("Hello. I am your navigation assistant. Please tell me your destination.")
    # Determine approximate origin via IP
    origin_display = "current location"
    loc = get_approx_location()
    if loc:
        origin_display = loc.get("display") or origin_display
        voice.say(f"I detected you are near {origin_display}.")
    if args.destination:
        destination = args.destination
    else:
        destination = voice.ask("Where do you want to go?")
    if not destination:
        destination = "nearest coffee shop"
        voice.say("I didn't hear a destination. Using a nearby place as an example.")

    # In a real app, origin would come from GPS or IP geolocation; here we use a placeholder
    origin = origin_display
    options = router.get_routes(origin, destination)
    if not options:
        voice.say("I'm sorry, I couldn't find routes. Falling back to a safe demo.")
        options = router._demo_routes(destination)

    if args.auto_select:
        selected = sorted(options, key=lambda x: x.duration_min)[0] if options else None
    else:
        selected = choose_route(voice, options)

    # Start vision loop if enabled
    vision_enabled = (not args.no_vision) and (args.vision or ENABLE_VISION)
    obstacle_event = threading.Event() if vision_enabled else None
    vision = VisionLoop(enabled=vision_enabled, voice_say=voice.say, demo_mode=demo_mode, obstacle_event=obstacle_event)
    vision.start()

    try:
        if selected:
            guidance_loop(voice, selected, obstacle_event=obstacle_event, demo_mode=demo_mode, auto_start=args.auto_start)
        else:
            voice.say("No route selected.")
    finally:
        vision.stop()


if __name__ == "__main__":
    main()
