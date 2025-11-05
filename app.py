from __future__ import annotations
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from .adapters import MobileTTS, VisionSimulator

KV = """
ScreenManager:
    MenuScreen:
    RoutesScreen:
    GuidanceScreen:

<MenuScreen>:
    name: "menu"
    BoxLayout:
        orientation: "vertical"
        padding: 16
        spacing: 12
        Label:
            text: "Blind Navigation Assistant"
            font_size: 24
        TextInput:
            id: dest
            hint_text: "Enter destination"
            multiline: False
            size_hint_y: None
            height: "48dp"
        BoxLayout:
            size_hint_y: None
            height: "48dp"
            spacing: 12
            Button:
                text: "Find Routes"
                on_release:
                    app.on_find_routes(dest.text)
            Button:
                text: "Enable Vision"
                on_release: app.toggle_vision()

<RoutesScreen>:
    name: "routes"
    BoxLayout:
        orientation: "vertical"
        padding: 16
        spacing: 12
        Label:
            text: root.routes_text
        BoxLayout:
            size_hint_y: None
            height: "48dp"
            spacing: 12
            Button:
                text: "Walk"
                on_release: app.start_guidance("walking")
            Button:
                text: "Drive"
                on_release: app.start_guidance("driving")
            Button:
                text: "Transit"
                on_release: app.start_guidance("transit")

<GuidanceScreen>:
    name: "guide"
    BoxLayout:
        orientation: "vertical"
        padding: 16
        spacing: 12
        Label:
            text: root.status
        Button:
            text: "Stop"
            size_hint_y: None
            height: "48dp"
            on_release: app.stop_guidance()
"""

class MenuScreen(Screen):
    pass

class RoutesScreen(Screen):
    routes_text = StringProperty("Routes will appear here")

class GuidanceScreen(Screen):
    status = StringProperty("Waiting to start…")

class BlindNavKivyApp(App):
    def build(self):
        self.tts = MobileTTS()
        self.vision_enabled = False
        self.vision = VisionSimulator(on_obstacle=self._on_obstacle, interval_sec=15)
        self.sm = Builder.load_string(KV)
        return self.sm

    def toggle_vision(self):
        self.vision_enabled = not self.vision_enabled
        self.tts.say("Vision enabled" if self.vision_enabled else "Vision disabled")
        if self.vision_enabled:
            self.vision.start()
        else:
            self.vision.stop()

    def on_find_routes(self, destination: str):
        dest = destination.strip() or "nearest coffee shop"
        # Demo route list; in Phase 2 wire to routing.Router
        text = f"Options to {dest}:\n1) Walking - ~15 min\n2) Driving - ~8 min\n3) Transit - ~18 min"
        self.tts.say(f"Found routes to {dest}. Walking, Driving, and Transit.")
        routes_screen: RoutesScreen = self.sm.get_screen("routes")
        routes_screen.routes_text = text
        self.sm.current = "routes"

    def start_guidance(self, mode: str):
        g: GuidanceScreen = self.sm.get_screen("guide")
        g.status = f"{mode.title()} guidance started. Say start when ready."
        self.tts.say(f"Starting {mode} guidance. Say start when you are ready to begin.")
        self.sm.current = "guide"

    def _on_obstacle(self, msg: str):
        if not self.vision_enabled:
            return
        g: GuidanceScreen = self.sm.get_screen("guide")
        g.status = "Obstacle ahead. Waiting for 2 minutes…"
        self.tts.say("Obstacle ahead. Please wait two minutes.")
        # In this demo we don't actually block the UI thread. A real implementation would manage timers.

    def stop_guidance(self):
        self.tts.say("Guidance stopped.")
        self.sm.current = "menu"

if __name__ == "__main__":
    BlindNavKivyApp().run()
