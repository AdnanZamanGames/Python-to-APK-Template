import re
import math
import time
import json
import os
import shutil
import subprocess
import copy
import functools
import urllib.parse
import random

from kivy.app import App
from kivy.config import Config
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Ellipse, Mesh, Line, PushMatrix, PopMatrix, Rotate
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.slider import Slider
from kivy.uix.switch import Switch
from kivy.uix.spinner import Spinner
from kivy.core.audio import SoundLoader
from kivy.core.text import Label as CoreLabel

Config.set("graphics", "orientation", "landscape")
Window.fullscreen = "auto"
Window.clearcolor = (0.025, 0.035, 0.075, 1)

# Clean visual themes. Names avoid genre/effect labels; the style stays polished.
THEMES = {
    "Midnight": {"bg": (0.025, 0.035, 0.075, 1), "panel": (0.055, 0.075, 0.14, 1), "accent": (0.12, 0.72, 0.92, 1), "secondary": (0.48, 0.38, 0.82, 1), "good": (0.22, 0.82, 0.52, 1), "text": (0.9, 0.95, 1, 1), "grid": (0.20, 0.29, 0.40, 0.72)},
    "Ocean": {"bg": (0.015, 0.075, 0.11, 1), "panel": (0.025, 0.15, 0.20, 1), "accent": (0.12, 0.82, 0.78, 1), "secondary": (0.12, 0.48, 0.68, 1), "good": (0.42, 0.86, 0.52, 1), "text": (0.88, 1, 0.98, 1), "grid": (0.12, 0.38, 0.42, 0.75)},
    "Sunset": {"bg": (0.12, 0.045, 0.075, 1), "panel": (0.20, 0.075, 0.12, 1), "accent": (1, 0.48, 0.22, 1), "secondary": (0.72, 0.24, 0.42, 1), "good": (0.95, 0.72, 0.25, 1), "text": (1, 0.92, 0.86, 1), "grid": (0.48, 0.22, 0.27, 0.78)},
    "Forest": {"bg": (0.025, 0.075, 0.055, 1), "panel": (0.045, 0.13, 0.085, 1), "accent": (0.35, 0.82, 0.42, 1), "secondary": (0.18, 0.52, 0.32, 1), "good": (0.72, 0.9, 0.3, 1), "text": (0.91, 1, 0.88, 1), "grid": (0.20, 0.40, 0.26, 0.78)},
}
NEON_BG = THEMES["Midnight"]["bg"]
NEON_PANEL = THEMES["Midnight"]["panel"]
NEON_CYAN = THEMES["Midnight"]["accent"]
NEON_PINK = THEMES["Midnight"]["secondary"]
NEON_GREEN = THEMES["Midnight"]["good"]
NEON_TEXT = THEMES["Midnight"]["text"]

# Unity Ads configuration for Blocky Platformer (Android).
# Keep test mode enabled during development. Set False only after release checks
# and after switching the Unity Dashboard test-mode override appropriately.
UNITY_GAME_ID = "800427297"
UNITY_REWARDED_PLACEMENT_ID = "BP_Rewarded_Android"
UNITY_INTERSTITIAL_PLACEMENT_ID = "BP_Interstitial_Android"
UNITY_TEST_MODE = True

# direction: UP_RIGHT means /, UP_LEFT means \.
OBJECTS_DATA = [
{"id": 1, "name": "Ground", "shape": "SQUARE", "color": "GREEN", "length": "1 Tile W x 1 Tile L", "desc": "Solid block."},
{"id": 2, "name": "Spike", "shape": "TRIANGLE", "color": "RED", "length": "1 Tile W x 1 Tile L", "desc": "Kills player."},
{"id": 3, "name": "SAW", "shape": "CIRCLE", "color": "RED", "length": "1 Tile W x 1 Tile L", "desc": "Rotating hazard."},
{"id": 4, "name": "Moving Platform", "shape": "RECTANGLE", "color": "PURPLE", "length": "3 Tiles W x 1 Tile L", "desc": "Carries player."},
{"id": 5, "name": "Checkpoint", "shape": "SQUARE", "color": "GREEN", "length": "1 Tile W x 1 Tile L", "desc": "Saves respawn."},
{"id": 6, "name": "Coin", "shape": "CIRCLE", "color": "YELLOW", "length": "1 Tile W x 1 Tile L", "desc": "Collectible."},
{"id": 7, "name": "Gem", "shape": "POLYGON", "color": "BLUE", "length": "1 Tile W x 1 Tile L", "desc": "Diamond gem."},
{"id": 8, "name": "Key", "shape": "KEY SHAPED", "color": "BROWN", "length": "1 Tile W x 1 Tile L", "desc": "Unlocks doors."},
{"id": 9, "name": "Door", "shape": "RECTANGLE", "color": "BROWN", "length": "2 Tiles W x 1 Tile L", "desc": "Opens doors."},
{"id": 10, "name": "Button", "shape": "RECTANGLE", "color": "ORANGE", "length": "1 Tile W x 0.2 Tiles L", "desc": "Trigger."},
{"id": 11, "name": "Small Jump Pad", "shape": "RECTANGLE", "color": "PINK", "length": "1 Tile W x 0.2 Tiles L", "desc": "Small boost."},
{"id": 12, "name": "Medium Jump Pad", "shape": "RECTANGLE", "color": "YELLOW", "length": "1 Tile W x 0.2 Tiles L", "desc": "Med boost."},
{"id": 13, "name": "Large Jump Pad", "shape": "RECTANGLE", "color": "RED", "length": "1 Tile W x 0.2 Tiles L", "desc": "Large boost."},
{"id": 14, "name": "Trampoline", "shape": "RECTANGLE", "color": "SURFACE-RED", "length": "4 Tiles W x 1 Tile L", "desc": "Bouncy base."},
{"id": 15, "name": "Lava", "shape": "WAVY RECTANGLE", "color": "YELLOW", "length": "1 Tile W x 1 Tile L", "desc": "Lava hazard."},
{"id": 16, "name": "Water", "shape": "WAVY RECTANGLE", "color": "BLUE", "length": "1 Tile W x 1 Tile L", "desc": "Swimming water."},
{"id": 17, "name": "Ice", "shape": "SQUARE", "color": "AQUA BLUE", "length": "1 Tile W x 1 Tile L", "desc": "Low friction."},
{"id": 18, "name": "Fan", "shape": "RECTANGLE", "color": "BLUE", "length": "3 Tiles W x 1 Tile L", "desc": "Wind force."},
{"id": 19, "name": "Enemy", "shape": "SQUARE", "color": "RED", "length": "1 Tile W x 1 Tile L", "desc": "Patrol enemy."},
{"id": 20, "name": "Breakable Platform", "shape": "RECTANGLE", "color": "BROWN", "length": "3 Tiles W x 1 Tile L", "desc": "Breaks under feet."},
{"id": 21, "name": "Disappearing Platform", "shape": "RECTANGLE", "color": "WHITE", "length": "3 Tiles W x 1 Tile L", "desc": "Fades out."},
{"id": 22, "name": "Teleporter Start", "shape": "OVAL", "color": "BLACK", "length": "1 Tile W x 2 Tiles L", "desc": "Entry portal."},
{"id": 23, "name": "Teleporter End", "shape": "OVAL", "color": "BLACK", "length": "1 Tile W x 2 Tiles L", "desc": "Exit portal."},
{"id": 24, "name": "Slope /", "shape": "RAMP", "direction": "UP_RIGHT", "color": "BLACK", "length": "1 Tile W x 1 Tile L", "desc": "Ramp rises left to right."},
{"id": 25, "name": "Slope \\", "shape": "RAMP", "direction": "UP_LEFT", "color": "BLUE", "length": "1 Tile W x 1 Tile L", "desc": "Ramp rises right to left."},
{"id": 26, "name": "Half Block", "shape": "SQUARE", "color": "BLACK", "length": "1 Tile W x 0.5 Tiles L", "desc": "Half height."},
{"id": 27, "name": "Fake Block", "shape": "SQUARE", "color": "WHITE", "length": "1 Tile W x 1 Tile L", "desc": "Vanishes."},
{"id": 28, "name": "Invisible Block", "shape": "SQUARE", "color": "TRANSPARENT WHITE", "length": "1 Tile W x 1 Tile L", "desc": "Secret trap."},
{"id": 29, "name": "Tilting Platform", "shape": "RECTANGLE", "color": "BROWN", "length": "5 Tiles W x 1 Tile L", "desc": "Tilts on weight."},
{"id": 30, "name": "Sticky Block", "shape": "SQUARE", "color": "GREEN", "length": "1 Tile W x 1 Tile L", "desc": "Slows movement."},
{"id": 31, "name": "Laser", "shape": "SQUARE", "color": "RED", "length": "1 Tile W x 0.2 Tiles L", "desc": "Deadly beam."},
{"id": 32, "name": "Gravity Up", "shape": "RECTANGLE", "color": "YELLOW", "length": "1 Tile W x 3 Tiles L", "desc": "Reverses gravity."},
{"id": 33, "name": "Gravity Down", "shape": "RECTANGLE", "color": "BLUE", "length": "1 Tile W x 3 Tiles L", "desc": "Normal gravity."},
{"id": 34, "name": "Low Gravity Zone", "shape": "RECTANGLE", "color": "GREEN", "length": "1 Tile W x 3 Tiles L", "desc": "Low gravity."},
{"id": 35, "name": "High Gravity Zone", "shape": "RECTANGLE", "color": "PINK", "length": "1 Tile W x 3 Tiles L", "desc": "High gravity."},
{"id": 36, "name": "Slow Zone", "shape": "RECTANGLE", "color": "ORANGE", "length": "1 Tile W x 3 Tiles L", "desc": "Reduces speed."},
{"id": 37, "name": "Speed Zone", "shape": "RECTANGLE", "color": "RED", "length": "1 Tile W x 3 Tiles L", "desc": "Boosts speed."},
{"id": 38, "name": "Double Jump Zone", "shape": "RECTANGLE", "color": "PURPLE", "length": "1 Tile W x 3 Tiles L", "desc": "Double jump."},
{"id": 39, "name": "Conveyor", "shape": "RECTANGLE", "color": "GRAY", "length": "3 Tiles W x 1 Tile L", "desc": "Auto moves."},
{"id": 40, "name": "Ladder", "shape": "RECTANGLE", "color": "BROWN", "length": "0.2 Tiles W x 5 Tiles L", "desc": "Climbable."},
{"id": 41, "name": "No Jump Zone", "shape": "RECTANGLE", "color": "AQUA", "length": "1 Tile W x 3 Tiles L", "desc": "No jumping."},
{"id": 42, "name": "One-Way Platform", "shape": "RECTANGLE", "color": "WHITE", "length": "3 Tiles W x 1 Tile L", "desc": "Pass through."},
{"id": 43, "name": "Fake Spike", "shape": "TRIANGLE", "color": "RED", "length": "1 Tile W x 1 Tile L", "desc": "Harmless spike."},
{"id": 44, "name": "Slab", "shape": "SQUARE", "color": "WHITE", "length": "1 Tile W x 0.5 Tiles L", "desc": "Flat slab."},
{"id": 45, "name": "Text", "shape": "TEXT", "color": "WHITE", "length": "1 Tile W x 1 Tile L", "desc": "Displays text."},
{"id": 46, "name": "Toggle", "shape": "CIRCLE", "color": "RED", "length": "1 Tile W x 1 Tile L", "desc": "On/Off trigger."},
{"id": 47, "name": "Spike Block", "shape": "SQUARE", "color": "RED", "length": "1 Tile W x 1 Tile L", "desc": "Solid spike."},
{"id": 48, "name": "Moving SAW", "shape": "CIRCLE", "color": "RED", "length": "1 Tile W x 1 Tile L", "desc": "Moving saw."},
{"id": 49, "name": "Fireball", "shape": "CIRCLE", "color": "RED", "length": "1 Tile W x 1 Tile L", "desc": "Flying fireball."},
{"id": 50, "name": "Alpha", "shape": "CIRCLE", "color": "WHITE", "length": "1 Tile W x 1 Tile L", "desc": "Fade trigger."},
{"id": 51, "name": "Normal Gravity Zone", "shape": "RECTANGLE", "color": "WHITE", "length": "1 Tile W x 3 Tiles L", "desc": "Restores normal downward gravity."},
{"id": 52, "name": "Normal Speed Zone", "shape": "RECTANGLE", "color": "GRAY", "length": "1 Tile W x 3 Tiles L", "desc": "Restores normal movement speed."},
{"id": 54, "name": "Timer Trigger", "shape": "CIRCLE", "color": "YELLOW", "length": "1 Tile W x 1 Tile L", "desc": "Runs an action after a timer."},
{"id": 55, "name": "Move Trigger", "shape": "CIRCLE", "color": "PURPLE", "length": "1 Tile W x 1 Tile L", "desc": "Moves a target group by tiles over time."},
{"id": 56, "name": "Sound Trigger", "shape": "CIRCLE", "color": "BLUE", "length": "1 Tile W x 1 Tile L", "desc": "Plays imported audio when activated."},
{"id": 57, "name": "Toggle Trigger", "shape": "CIRCLE", "color": "ORANGE", "length": "1 Tile W x 1 Tile L", "desc": "Toggles a target group on/off when activated."},
{"id": 58, "name": "Circle", "shape": "CIRCLE", "color": "WHITE", "length": "1 Tile W x 1 Tile L", "desc": "A plain circle."},
]

@functools.lru_cache(maxsize=256)
def get_color_rgba(color_str):
    c = str(color_str).strip().upper()
    if re.fullmatch(r"#?[0-9A-F]{6}", c):
        h = c.lstrip("#")
        return (int(h[0:2], 16)/255.0, int(h[2:4], 16)/255.0, int(h[4:6], 16)/255.0, 1.0)
    if "GREEN" in c: return (0.2, 0.8, 0.2, 1)
    if "RED" in c: return (0.9, 0.2, 0.2, 1)
    if "YELLOW" in c: return (0.9, 0.8, 0.1, 1)
    if "PURPLE" in c: return (0.6, 0.2, 0.8, 1)
    if "BROWN" in c: return (0.5, 0.3, 0.1, 1)
    if "ORANGE" in c: return (1, 0.5, 0, 1)
    if "PINK" in c: return (1, 0.4, 0.7, 1)
    if "BLUE" in c or "AQUA" in c: return (0.2, 0.6, 1, 1)
    if "BLACK" in c: return (0.2, 0.2, 0.2, 1)
    if "WHITE" in c or "TRANSPARENT" in c: return (0.9, 0.9, 0.9, 1)
    if "GRAY" in c: return (0.5, 0.5, 0.5, 1)
    return (0.7, 0.7, 0.7, 1)

@functools.lru_cache(maxsize=256)
def parse_tile_dimensions(length_str):
    text = length_str.upper()
    width = height = 1.0
    m = re.search(r"([\d.]+)\s*TILES?\s*W", text)
    if m: width = float(m.group(1))
    m = re.search(r"([\d.]+)\s*TILES?\s*L", text)
    if m: height = float(m.group(1))
    return width, height

class MultiTouchButton(Button):
    def __init__(self, action_callback, **kwargs):
        super().__init__(**kwargs)
        self.action_callback = action_callback
        self.active_touch = None
        self.last_touch_pos = None

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and self.active_touch is None:
            self.active_touch = touch
            self.last_touch_pos = tuple(touch.pos)
            touch.grab(self)
            self.action_callback(True)
            return True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.grab_current == self:
            touch.ungrab(self)
            self.active_touch = None
            self.action_callback(False)
            return True
        return super().on_touch_up(touch)

class ColorWheel(Widget):
    """Simple touch-selectable HSV color wheel."""
    def __init__(self, initial="#FFFFFF", on_color=None, **kwargs):
        super().__init__(**kwargs)
        self.on_color = on_color
        self.hue = 0.0
        self.saturation = 0.0
        self.value = 1.0
        try:
            r, g, b, _ = get_color_rgba(initial)
            import colorsys
            self.hue, self.saturation, self.value = colorsys.rgb_to_hsv(r, g, b)
        except Exception:
            pass
        self.bind(pos=self.redraw, size=self.redraw)
        self.redraw()

    def redraw(self, *args):
        self.canvas.clear()
        import colorsys
        cx, cy = self.center
        radius = max(10, min(self.width, self.height) * 0.46)
        with self.canvas:
            for i in range(72):
                a1 = 2 * math.pi * i / 72
                a2 = 2 * math.pi * (i + 1) / 72
                hue = i / 72
                rgb = colorsys.hsv_to_rgb(hue, 1, 1)
                Color(*rgb, 1)
                Mesh(vertices=[cx, cy, 0, 0, cx+radius*math.cos(a1), cy+radius*math.sin(a1), 0, 0,
                               cx+radius*math.cos(a2), cy+radius*math.sin(a2), 0, 0], indices=[0,1,2], mode="triangles")
            # center marker indicates selected hue/saturation
            a = self.hue * 2 * math.pi
            rr = radius * self.saturation
            Color(1, 1, 1, 1)
            Ellipse(pos=(cx+rr*math.cos(a)-6, cy+rr*math.sin(a)-6), size=(12,12))
            Color(0, 0, 0, 1)
            Ellipse(pos=(cx+rr*math.cos(a)-3, cy+rr*math.sin(a)-3), size=(6,6))

    def color_hex(self):
        import colorsys
        rgb = colorsys.hsv_to_rgb(self.hue, self.saturation, self.value)
        return "#%02X%02X%02X" % tuple(round(v*255) for v in rgb)

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        self._choose(touch.pos)
        touch.grab(self)
        return True

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            self._choose(touch.pos)
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            return True
        return super().on_touch_up(touch)

    def _choose(self, pos):
        import colorsys
        dx, dy = pos[0]-self.center_x, pos[1]-self.center_y
        radius = max(1, min(self.width, self.height)*0.46)
        self.hue = (math.atan2(dy, dx) / (2*math.pi)) % 1.0
        self.saturation = min(1.0, math.hypot(dx,dy)/radius)
        self.redraw()
        if self.on_color:
            self.on_color(self.color_hex())


class CosmeticPreview(Widget):
    """Canvas-based cosmetic thumbnail; avoids unsupported Unicode glyph boxes."""
    def __init__(self, kind="skin", name="Green", rgba=(0.2, 0.9, 0.3, 1), **kwargs):
        super().__init__(**kwargs)
        self.kind = kind
        self.name = name
        self.rgba = rgba
        self.bind(pos=self.redraw, size=self.redraw)
        self.redraw()

    def redraw(self, *_):
        self.canvas.clear()
        x, y, w, h = self.x, self.y, self.width, self.height
        if w <= 0 or h <= 0:
            return
        with self.canvas:
            Color(0.035, 0.055, 0.095, 1)
            Rectangle(pos=(x, y), size=(w, h))
            Color(0.22, 0.30, 0.42, 1)
            Line(rectangle=(x + 2, y + 2, w - 4, h - 4), width=1.2)
            if self.kind == "skin":
                size = min(w * 0.58, h * 0.68)
                px, py = x + (w-size)/2, y + (h-size)/2
                Color(self.rgba[0]*0.42, self.rgba[1]*0.42, self.rgba[2]*0.42, 1)
                Rectangle(pos=(px-3, py-3), size=(size+6, size+6))
                Color(*self.rgba)
                Rectangle(pos=(px, py), size=(size, size))
                Color(1, 1, 1, 0.32)
                Rectangle(pos=(px+size*0.12, py+size*0.78), size=(size*0.76, max(2, size*0.08)))
            elif self.name != "None":
                colors = {
                    "Spark": (1.0, 0.88, 0.16, 1), "Flame": (1.0, 0.26, 0.045, 1),
                    "Ice": (0.18, 0.76, 1.0, 1), "Rainbow": (0.8, 0.25, 1.0, 1),
                }
                c = colors.get(self.name, self.rgba)
                cx, cy = x + w*0.55, y + h*0.5
                for i, scale in enumerate((1.0, 0.78, 0.58, 0.4)):
                    Color(c[0], c[1], c[2], 1.0 - i*0.18)
                    r = min(w, h) * 0.11 * scale
                    Ellipse(pos=(cx - w*0.12 - i*w*0.12 - r/2, cy + ((i%2)*2-1)*h*0.08-r/2), size=(r, r))
                if self.name == "Rainbow":
                    for i, c in enumerate(((1,.2,.2,1),(1,.65,.1,1),(.2,.8,1,1),(.5,1,.3,1))):
                        Color(*c)
                        Ellipse(pos=(x+w*(.18+i*.14), y+h*.23), size=(min(w,h)*.12, min(w,h)*.12))
            else:
                Color(0.72, 0.82, 0.94, 1)
                Ellipse(pos=(x+w*.40, y+h*.40), size=(min(w,h)*.20, min(w,h)*.20))



class RotationWheel(Widget):
    """Circular drag control drawn around the selected editor object."""
    def __init__(self, on_angle, **kwargs):
        super().__init__(**kwargs)
        self.on_angle = on_angle
        self.angle = 0.0
        self._drag_touch = None
        with self.canvas:
            Color(0.05, 0.08, 0.15, 0.22)
            self._outer_fill = Ellipse(pos=self.pos, size=self.size)
            Color(0.02, 0.04, 0.10, 0.98)
            self._ring_shadow = Line(circle=(0, 0, 76), width=7.0)
            Color(0.10, 0.92, 1.0, 1.0)
            self._ring = Line(circle=(0, 0, 76), width=4.0)
            Color(0.10, 0.92, 1.0, 0.70)
            self._inner_ring = Line(circle=(0, 0, 66), width=1.6)
            Color(0.96, 0.45, 0.22, 1)
            self._pointer = Ellipse(pos=(0, 0), size=(14, 14))
            Color(0.92, 0.98, 1, 0.95)
            self._pointer_line = Line(points=[0, 0, 0, 0], width=2)
        self.angle_label = Label(text='0°', bold=True, font_size=14,
                                 color=(0.95, 0.98, 1, 1),
                                 size_hint=(None, None), size=(52, 26))
        self.add_widget(self.angle_label)
        self.bind(pos=self._redraw, size=self._redraw)
        self._redraw()

    def set_angle(self, angle):
        self.angle = float(angle) % 360.0
        self.angle_label.text = f'{int(round(self.angle)) % 360}°'
        self._redraw()

    def _redraw(self, *_):
        cx, cy = self.center
        radius = min(self.width, self.height) * 0.43
        self._outer_fill.pos = self.pos
        self._outer_fill.size = self.size
        self._ring.circle = (cx, cy, radius)
        self._inner_ring.circle = (cx, cy, radius - 10)
        rad = math.radians(self.angle)
        ex = cx + math.cos(rad) * radius
        ey = cy + math.sin(rad) * radius
        self._pointer.pos = (ex - 7, ey - 7)
        self._pointer_line.points = [cx, cy, ex, ey]
        self.angle_label.center = (cx, cy)

    def _angle_from_touch(self, touch):
        dx, dy = touch.x - self.center_x, touch.y - self.center_y
        self.set_angle(math.degrees(math.atan2(dy, dx)) % 360.0)
        self.on_angle(self.angle)

    def on_touch_down(self, touch):
        if self.disabled or not self.collide_point(*touch.pos):
            return False
        dx, dy = touch.x - self.center_x, touch.y - self.center_y
        distance = math.hypot(dx, dy)
        radius = min(self.width, self.height) * 0.43
        if abs(distance - radius) > 24:
            return False
        self._drag_touch = touch
        touch.grab(self)
        self._angle_from_touch(touch)
        return True

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            self._angle_from_touch(touch)
            return True
        return False

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            self._drag_touch = None
            return True
        return False


class FullScreenGridCanvas(Widget):
    SOLID_IDS = {1, 4, 9, 17, 20, 21, 26, 27, 28, 29, 30, 39, 44, 47}

    def __init__(self, app_ref, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app_ref
        self.cols, self.rows = 32, 20
        self.grid_data = {}
        self.player_x = self.player_y = 0.0
        self.player_vx = self.player_vy = 0.0
        self.player_angle = 0.0
        self.is_grounded = False
        self.move_left = self.move_right = self.move_up = self.move_down = False
        self.elapsed_time = 0.0
        self.animation_time = 0.0
        self.visual_redraw_elapsed = 0.0
        self.land_bounce = 0.0
        self.active_spawn = None
        self.has_key = False
        self.score = 0
        self.teleport_cooldown = 0.0
        self.collected_ids = set()
        self.timers = {}
        self.disappearing_states = {}
        self.broken_blocks = set()
        self.enemy_directions = {}
        self.toggle_states = {}
        self.object_contact_latches = set()
        self.alpha = 1.0
        self.trigger_runtime = {}
        self.move_offsets = {}
        self.loaded_sounds = {}
        self.selected_key = None
        self._objects_by_id = {}
        self._all_object_items = ()
        self._render_order_index = {}
        self._render_stage_index = None
        self._indexed_auto_endpoint_col = 0
        self._runtime_index_signature = None
        self._runtime_index_dirty = True
        self._dimensions_by_key = {}
        self._solid_objects_cache = ()
        self._spatial_buckets = {}
        self._text_texture_cache = {}
        # Responsive jump input: a short input buffer and coyote-time grace.
        self.jump_buffer_remaining = 0.0
        self.coyote_remaining = 0.0
        self.jump_cut_requested = False
        self.edit_touch_key = None
        self.edit_touch_start = None
        self.edit_touch_origin = None
        self.double_jump_available = False
        self.used_double_jump = False
        self.landing_input_until = 0.0
        self.gravity_sign = -1
        self.zone_modes = {"gravity": "normal", "speed": "normal", "double_jump": False, "no_jump": False}
        self.bind(pos=self.redraw, size=self.redraw)
        self.rotation_wheel = RotationWheel(
            self._rotation_changed, size_hint=(None, None), size=(190, 190)
        )
        self.rotation_wheel.opacity = 0
        self.rotation_wheel.disabled = True
        # Render the rotation control in canvas.after, not as a normal child.
        # Normal children can be covered by editor panels/overlays; canvas.after
        # is drawn after the grid canvas and all child widgets.
        self.canvas.after.add(self.rotation_wheel.canvas)
        self.canvas.after.add(self.rotation_wheel.angle_label.canvas)
        self.rotation_wheel.angle_label.opacity = 0

    def _rotation_changed(self, value):
        key = self.selected_key
        if key is not None and key in self.grid_data and not self.app_ref.is_playing:
            angle = float(value) % 360.0
            self.grid_data[key]["rotation"] = angle
            self._mark_grid_changed()
            self.rotation_wheel.set_angle(angle)
            self.redraw()

    def _index_runtime_objects(self):
        """Keep per-ID, tile-size and spatial indexes; rebuild only after level edits."""
        if not self._runtime_index_dirty:
            return
        items = tuple(self.grid_data.items())
        by_id = {}
        dimensions = {}
        max_col = 0
        solid_items = []
        spatial = {}
        for key, obj in items:
            oid = obj.get("id", -1)
            by_id.setdefault(oid, []).append((key, obj))
            try:
                tw, th = parse_tile_dimensions(obj.get("length", "1 Tile W x 1 Tile L"))
            except (TypeError, ValueError):
                tw, th = 1.0, 1.0
            dimensions[key] = (id(obj), obj.get("length"), tw, th)
            try:
                max_col = max(max_col, int(key[0] + tw - 1))
            except (TypeError, ValueError, IndexError):
                pass
            if oid in self.SOLID_IDS:
                solid_items.append((key, obj))
            try:
                c0, r0 = int(key[0]), int(key[1])
                for cc in range(c0, c0 + max(1, int(math.ceil(tw)))):
                    for rr in range(r0, r0 + max(1, int(math.ceil(th)))):
                        spatial.setdefault((cc, rr), []).append((key, obj))
            except (TypeError, ValueError, IndexError):
                spatial.setdefault((0, 0), []).append((key, obj))
        self._all_object_items = items
        self._render_order_index = {key: index for index, (key, _obj) in enumerate(items)}
        self._objects_by_id = {oid: tuple(entries) for oid, entries in by_id.items()}
        self._dimensions_by_key = dimensions
        self._solid_objects_cache = tuple(solid_items)
        self._spatial_buckets = {tile: tuple(entries) for tile, entries in spatial.items()}
        self._indexed_auto_endpoint_col = min(max_col + 1, self.cols - 1)
        self._runtime_index_signature = None
        self._runtime_index_dirty = False

    def _active_stage_render_items(self, cell):
        """Render only the selected stage, using its stored object dictionary."""
        app = self.app_ref
        stages = getattr(app, "stages", None) or []
        index = int(getattr(app, "current_stage_index", 0))
        if 0 <= index < len(stages):
            stage = stages[index]
            active = stage.get("objects", {}) if isinstance(stage, dict) else {}
            if isinstance(active, dict):
                if getattr(app, "is_playing", False):
                    # Runtime grid is authoritative while playing.
                    if self.grid_data is not active:
                        stage["objects"] = self.grid_data
                elif self.grid_data is not active:
                    # Stage data is canonical in editor mode. This prevents an
                    # empty/stale canvas from hiding a populated selected stage.
                    self.grid_data = active
                    self._runtime_index_dirty = True
                    self._all_object_items = ()
                    self._spatial_buckets = {}
        return self._visible_render_items(cell)

    def _visible_render_items(self, cell):
        """Cull off-screen objects from the active grid only.

        The physics index is built from self.grid_data, which represents only
        the selected stage. Other stage dictionaries are never indexed or drawn.
        Original insertion order is retained to preserve drawing/z-order.
        """
        self._index_runtime_objects()
        # The editor is a design surface, not a camera viewport. Draw every
        # placed object so objects near the edges / in taller rows are never
        # silently hidden by the gameplay visibility buckets.
        if not getattr(self.app_ref, "is_playing", False):
            return self._all_object_items
        if not self._spatial_buckets or cell <= 0:
            return self._all_object_items
        left = int(math.floor((self.x - self.x) / cell)) - 1
        bottom = int(math.floor((self.y - self.y) / cell)) - 1
        right = int(math.ceil(self.width / cell)) + 1
        top = int(math.ceil(self.height / cell)) + 1
        visible = {}
        for col in range(left, right + 1):
            for row in range(bottom, top + 1):
                for key, obj in self._spatial_buckets.get((col, row), ()):
                    visible[key] = obj
        # Include objects shifted by Move Triggers even if their authored tile
        # is outside the visible buckets.
        for key, offset in self.move_offsets.items():
            if abs(offset[0]) > 0.01 or abs(offset[1]) > 0.01:
                obj = self.grid_data.get(key)
                if obj is not None:
                    visible[key] = obj
        return tuple((key, visible[key]) for key in sorted(
            visible, key=lambda item: self._render_order_index.get(item, 10**12)
        ))

    def _tile_dimensions(self, key, obj):
        cached = self._dimensions_by_key.get(key)
        length = obj.get("length", "1 Tile W x 1 Tile L")
        if cached is not None and cached[0] == id(obj) and cached[1] == length:
            return cached[2], cached[3]
        try:
            return parse_tile_dimensions(length)
        except (TypeError, ValueError):
            return 1.0, 1.0

    def _objects_for_ids(self, ids):
        result = []
        for oid in ids:
            result.extend(self._objects_by_id.get(oid, ()))
        return result

    def _nearby_runtime_objects(self, cell, pad=6):
        """Return unique objects in nearby tile buckets, including trigger-moved objects."""
        if not self._spatial_buckets or cell <= 0:
            return self._all_object_items
        col = int(math.floor((self.player_x - self.x) / cell))
        row = int(math.floor((self.player_y - self.y) / cell))
        found = {}
        for cc in range(col - pad, col + pad + 2):
            for rr in range(row - pad, row + pad + 2):
                for key, obj in self._spatial_buckets.get((cc, rr), ()):
                    found[key] = (key, obj)
        # A trigger can move an object far from its authored tile; never cull those.
        for key, offset in self.move_offsets.items():
            if abs(offset[0]) > 0.01 or abs(offset[1]) > 0.01:
                obj = self.grid_data.get(key)
                if obj is not None:
                    found[key] = (key, obj)
        return tuple(found.values())

    def cell(self):
        return self.width / self.cols if self.cols else 40

    def reset_controls(self):
        self.move_left = self.move_right = self.move_up = self.move_down = False
        self.player_vx = self.player_vy = 0.0
        self.player_angle = 0.0
        self.elapsed_time = 0.0
        self.land_bounce = 0.0
        self.has_key = False
        self.score = 0
        self.teleport_cooldown = 0.0
        self.is_grounded = False
        self.gravity_sign = -1
        self.zone_modes = {"gravity": "normal", "speed": "normal", "double_jump": False, "no_jump": False}
        self.double_jump_available = False
        self.used_double_jump = False
        self.landing_input_until = 0.0
        self.jump_buffer_remaining = 0.0
        self.coyote_remaining = 0.0
        self.jump_cut_requested = False
        self.timers = {}
        self.disappearing_states = {}
        self.broken_blocks = set()
        self.collected_ids = set()
        self.object_contact_latches = set()
        self.alpha = 1.0
        self.trigger_runtime = {}
        self.move_offsets = {}
        for sound in self.loaded_sounds.values():
            try:
                sound.stop()
            except Exception:
                pass
        self.loaded_sounds = {}
        for placed_obj in self.grid_data.values():
            placed_obj.pop("_trigger_latched", None)
            placed_obj.pop("_trigger_used", None)
            placed_obj.pop("_auto_spawn_activated", None)

    def spawn_player(self):
        self._runtime_index_dirty = True
        cell = self.cell()
        if self.active_spawn:
            self.player_x, self.player_y = self.active_spawn
        else:
            player_size = cell - 4
            self.player_x = self.x + 2
            self.player_y = self.y + self.height - player_size - cell * 0.25
        self.reset_controls()

    def get_auto_endpoint_col(self):
        if self._all_object_items:
            return self._indexed_auto_endpoint_col
        max_col = 0
        for key, obj in self.grid_data.items():
            col, row = key[0], key[1]
            tw, _ = parse_tile_dimensions(obj["length"])
            max_col = max(max_col, int(col + tw - 1))
        return min(max_col + 1, self.cols - 1)

    def get_platform_x_offset(self, obj_id, key=None):
        if obj_id == 4: return math.sin(self.elapsed_time * 2.5) * 1.0
        if obj_id == 48: return math.cos(self.elapsed_time * 4.0) * 1.5
        if obj_id == 49: return math.sin(self.elapsed_time * 5.0) * 2.0
        if obj_id == 19: return math.sin(self.elapsed_time * 1.8) * 1.4
        return 0.0

    def object_rect(self, key, obj, cell):
        # Keys may be (col, row) or (col, row, serial) when objects overlap.
        # Always use the first two values for the tile position.
        col, row = key[0], key[1]
        oid = obj["id"]
        tw, th = self._tile_dimensions(key, obj)
        off = self.get_platform_x_offset(oid, key) if oid in (4, 19, 48, 49) else 0.0
        move_dx, move_dy = self.move_offsets.get(key, (0.0, 0.0))
        bx, by = self.x + (col + off + move_dx) * cell, self.y + (row + move_dy) * cell
        if self.app_ref.is_playing and not obj.get("enabled", True):
            return bx, by, 0.0, 0.0
        return bx, by, tw * cell, th * cell

    def slope_surface(self, obj, cx, cy, cw, ch, world_x):
        if cw <= 0:
            return cy
        t = max(0.0, min(1.0, (world_x - cx) / cw))
        return cy + ch * t if obj.get("direction", "UP_RIGHT") == "UP_RIGHT" else cy + ch * (1.0 - t)

    def overlaps(self, a, b):
        return a[0] < b[0] + b[2] and a[0] + a[2] > b[0] and a[1] < b[1] + b[3] and a[1] + a[3] > b[1]

    def _teleport_position_is_blocked(self, x, y, player_size, cell):
        """Check a proposed portal destination against every active solid object."""
        player_rect = (x, y, player_size, player_size)
        objects = self._all_object_items or tuple(self.grid_data.items())
        for key, obj in objects:
            oid = obj.get("id")
            if oid not in self.SOLID_IDS or not obj.get("enabled", True):
                continue
            if oid == 20 and (key in self.broken_blocks or key in self.timers):
                continue
            if oid == 21 and self.disappearing_states.get(key, {}).get("state") == "hidden":
                continue
            if oid == 27 and key in self.timers:
                continue
            bx, by, bw, bh = self.object_rect(key, obj, cell)
            if bw > 0 and bh > 0 and self.overlaps(player_rect, (bx, by, bw, bh)):
                return True
        return False

    def _find_safe_teleport_position(self, base_x, base_y, player_size, cell):
        """Find a clear exit around a portal, rather than placing the player inside a solid."""
        offsets = [
            (0, 0),
            (-0.75, 0), (0.75, 0), (-1.5, 0), (1.5, 0),
            (0, 1), (-1, 1), (1, 1), (0, 2), (-1, 2), (1, 2),
            (0, -1), (-1, -1), (1, -1),
            (-2, 0), (2, 0), (0, 3), (0, -2),
        ]
        world_left = self.x
        world_bottom = self.y
        world_right = self.x + self.cols * cell
        world_top = self.y + self.rows * cell
        for ox, oy in offsets:
            x = base_x + ox * cell
            y = base_y + oy * cell
            if x < world_left or x + player_size > world_right:
                continue
            if y < world_bottom or y + player_size > world_top:
                continue
            if not self._teleport_position_is_blocked(x, y, player_size, cell):
                return x, y
        return None

    TRIGGER_IDS = {50, 54, 55, 56, 57}

    def _trigger_easing(self, name, t):
        t = max(0.0, min(1.0, t))
        if name == "Ease In": return t * t
        if name == "Ease Out": return 1.0 - (1.0 - t) * (1.0 - t)
        if name == "Ease In-Out": return 3*t*t - 2*t*t*t
        if name == "Bounce":
            if t < 1/2.75: return 7.5625*t*t
            if t < 2/2.75:
                t -= 1.5/2.75
                return 7.5625*t*t + 0.75
            if t < 2.5/2.75:
                t -= 2.25/2.75
                return 7.5625*t*t + 0.9375
            t -= 2.625/2.75
            return 7.5625*t*t + 0.984375
        if name == "Elastic":
            if t in (0.0, 1.0): return t
            return 2**(-10*t) * math.sin((t*10 - 0.75) * (2*math.pi/3)) + 1
        return t

    def _trigger_group_keys(self, group_id):
        gid = str(group_id or "").strip()
        if not gid:
            return []
        return [k for k, o in self.grid_data.items() if str(o.get("group_id", "")).strip() == gid]

    def _door_is_trigger_linked(self, door_obj):
        """A door with a group targeted by any trigger must only open via that trigger."""
        group_id = str(door_obj.get("group_id", "")).strip()
        if not group_id:
            return False
        return any(
            obj.get("id") in self.TRIGGER_IDS
            and str(obj.get("target_group_id", "")).strip() == group_id
            for obj in self.grid_data.values()
        )

    def _apply_trigger_action(self, trigger_key, trigger_obj):
        """Apply a lightweight group action to objects sharing the configured ID."""
        action = str(trigger_obj.get("trigger_action", "Toggle")).strip().upper()
        group_id = trigger_obj.get("effect_group_id", trigger_obj.get("target_group_id", ""))
        targets = self._trigger_group_keys(group_id)
        for target_key in targets:
            target = self.grid_data.get(target_key)
            if not target:
                continue
            if action in ("ON", "ENABLE"):
                target["enabled"] = True
            elif action in ("OFF", "DISABLE"):
                target["enabled"] = False
            else:
                target["enabled"] = not bool(target.get("enabled", True))

    def _start_move_trigger(self, trigger_key, trigger_obj):
        group_id = trigger_obj.get("effect_group_id", trigger_obj.get("target_group_id", ""))
        targets = self._trigger_group_keys(group_id)
        if not targets:
            return
        direction = str(trigger_obj.get("move_direction", "Right and left"))
        mx = max(0.0, float(trigger_obj.get("move_x_tiles", trigger_obj.get("move_distance", 1)) or 0))
        my = max(0.0, float(trigger_obj.get("move_y_tiles", trigger_obj.get("move_distance", 1)) or 0))
        if direction in ("Up", "Down", "Up and down"):
            dx, dy = 0.0, (my if direction != "Down" else -my)
        else:
            dx, dy = (mx if direction != "Left" else -mx), 0.0
        # move_offsets are expressed in grid tiles throughout physics and rendering.
        starts = {k: self.move_offsets.get(k, (0.0, 0.0)) for k in targets}
        duration = max(0.05, float(trigger_obj.get("move_time", 2.0) or 2.0))
        self.trigger_runtime[trigger_key] = {
            "kind": "move", "elapsed": 0.0, "duration": duration,
            "starts": starts, "delta": (dx, dy), "targets": targets,
            "loop": trigger_obj.get("move_loop", "Once") == "Loop",
            "pingpong": direction in ("Up and down", "Right and left"),
            "reverse": False,
        }

    def _play_trigger_sound(self, key, obj):
        action = str(obj.get("sound_action", "Play"))
        group_id = str(obj.get("effect_group_id", obj.get("target_group_id", ""))).strip()
        if action == "Stop":
            stop_id = str(obj.get("stop_effect_group_id", group_id)).strip()
            sound = self.loaded_sounds.get("group:" + stop_id)
            if sound is not None:
                try:
                    sound.stop()
                except Exception:
                    pass
            return
        path = str(obj.get("sound_path", "")).strip()
        if not path or not os.path.isfile(path):
            self.app_ref.status_label.text = "Sound Trigger: choose a valid audio file in Props"
            return
        sound_key = "group:" + (group_id or str(key))
        sound = self.loaded_sounds.get(sound_key)
        if sound is None or getattr(sound, "_trigger_path", None) != path:
            try:
                sound = SoundLoader.load(path)
                if sound is None:
                    self.app_ref.status_label.text = "This audio format is not supported by the current Kivy audio provider"
                    return
                sound._trigger_path = path
                self.loaded_sounds[sound_key] = sound
            except Exception as exc:
                self.app_ref.status_label.text = f"Could not load sound: {exc}"
                return
        try:
            sound.stop()
            sound.volume = max(0.0, min(1.0, float(obj.get("sound_volume", 100)) / 100.0))
            sound.loop = obj.get("sound_playback", "Once") == "Loop"
            sound.play()
        except Exception as exc:
            self.app_ref.status_label.text = f"Could not play sound: {exc}"

    def _activate_trigger_group(self, group_id):
        """Activate every trigger whose object Group ID matches the supplied ID."""
        gid = str(group_id or "").strip()
        if not gid:
            return 0
        activated_count = 0
        for target_key, target_obj in list(self.grid_data.items()):
            if int(target_obj.get("id", -1)) not in self.TRIGGER_IDS:
                continue
            if str(target_obj.get("group_id", "")).strip() != gid:
                continue
            if not target_obj.get("enabled", True):
                continue
            self._activate_trigger(target_key, target_obj)
            target_obj["_trigger_latched"] = True
            target_obj["_trigger_used"] = True
            activated_count += 1
        return activated_count

    def _activate_trigger(self, key, obj):
        oid = obj.get("id")
        if oid == 50:
            targets = self._trigger_group_keys(obj.get("target_group_id", ""))
            if not targets:
                self.app_ref.status_label.text = "Alpha: set matching Group IDs on target objects"
                return
            start_values = {tk: float(self.grid_data[tk].get("alpha", 1.0)) for tk in targets if tk in self.grid_data}
            target_alpha = max(0.0, min(1.0, float(obj.get("alpha_value", 0)) / 100.0))
            duration = max(0.05, float(obj.get("alpha_speed", 1.0)))
            self.trigger_runtime[key] = {"kind": "alpha", "elapsed": 0.0, "duration": duration, "starts": start_values, "target_alpha": target_alpha}
        elif oid == 57:
            self._apply_trigger_action(key, obj)
        elif oid == 54:
            duration = max(0.05, float(obj.get("timer_duration", 3.0) or 3.0))
            self.trigger_runtime[key] = {"kind": "timer", "remaining": duration, "duration": duration,
                                         "repeat": obj.get("timer_loop", "Once"), "action_done": False}
        elif oid == 55:
            self._start_move_trigger(key, obj)
        elif oid == 56:
            if obj.get("sound_action", "Play") == "Stop":
                self._play_trigger_sound(key, obj)
            else:
                delay = max(0.0, float(obj.get("sound_delay", 0.0) or 0.0))
                if delay > 0:
                    self.trigger_runtime[key] = {"kind": "sound_delay", "remaining": delay}
                else:
                    self._play_trigger_sound(key, obj)

    def _advance_trigger_runtime(self, dt):
        for key, state in list(self.trigger_runtime.items()):
            obj = self.grid_data.get(key)
            kind = state.get("kind")
            if kind == "alpha":
                if not obj:
                    self.trigger_runtime.pop(key, None); continue
                state["elapsed"] = min(state["duration"], state["elapsed"] + dt)
                t = state["elapsed"] / state["duration"]
                for target_key, start_alpha in state["starts"].items():
                    target = self.grid_data.get(target_key)
                    if target is not None:
                        target["alpha"] = max(0.0, min(1.0, start_alpha + (state["target_alpha"] - start_alpha) * t))
                if t >= 1.0: self.trigger_runtime.pop(key, None)
            elif kind == "move":
                if not obj:
                    self.trigger_runtime.pop(key, None); continue
                state["elapsed"] += dt
                t = min(1.0, state["elapsed"] / state["duration"])
                if state.get("reverse"):
                    t = 1.0 - t
                dx, dy = state["delta"]
                for target_key, (sx, sy) in state["starts"].items():
                    self.move_offsets[target_key] = (sx + dx*t, sy + dy*t)
                if state["elapsed"] >= state["duration"]:
                    if state.get("pingpong") and not state.get("reverse"):
                        # Bidirectional directions always complete the return leg, even with Loop=Once.
                        state["reverse"] = True
                        state["elapsed"] = 0.0
                    elif state.get("loop"):
                        state["elapsed"] = 0.0
                        state["reverse"] = False
                        if not state.get("pingpong"):
                            for target_key, start in state["starts"].items(): self.move_offsets[target_key] = start
                    else:
                        if state.get("pingpong"):
                            for target_key, start in state["starts"].items(): self.move_offsets[target_key] = start
                        self.trigger_runtime.pop(key, None)
            elif kind == "sound_delay":
                if not obj:
                    self.trigger_runtime.pop(key, None); continue
                state["remaining"] -= dt
                if state["remaining"] <= 0:
                    self._play_trigger_sound(key, obj); self.trigger_runtime.pop(key, None)
            elif kind == "timer":
                if not obj:
                    self.trigger_runtime.pop(key, None); continue
                state["remaining"] -= dt
                if state["remaining"] <= 0:
                    self._apply_trigger_action(key, obj)
                    if state.get("repeat") == "Loop":
                        state["remaining"] = state["duration"]
                    else:
                        obj["_trigger_used"] = True
                        self.trigger_runtime.pop(key, None)
                        # Once this timer finishes, it can start another trigger/group.
                        next_group = str(obj.get("next_trigger_group_id", "")).strip()
                        if next_group:
                            self._activate_trigger_group(next_group)

    def _activate_zone_effect(self, key, obj, entering=True):
        """Apply a trigger's in-zone effect or its optional out-zone effect."""
        oid = obj.get("id")
        if not entering and not obj.get("out_zone_enabled", False):
            return
        if oid == 50:
            targets = self._trigger_group_keys(obj.get("target_group_id", ""))
            if not targets:
                return
            if entering:
                percent = float(obj.get("in_zone_alpha_value", obj.get("alpha_value", 0)))
                duration = float(obj.get("in_zone_speed", obj.get("alpha_speed", 1.0)))
            else:
                mode = obj.get("out_zone_action", "Reverse Trigger Action")
                if mode == "Do Nothing": return
                percent = float(obj.get("out_zone_alpha_value", 100))
                duration = float(obj.get("out_zone_speed", 1.0))
            starts = {tk: float(self.grid_data[tk].get("alpha", 1.0)) for tk in targets if tk in self.grid_data}
            self.trigger_runtime[key] = {"kind":"alpha", "elapsed":0.0, "duration":max(.05,duration), "starts":starts, "target_alpha":max(0.0,min(1.0,percent/100.0))}
            return
        if entering:
            self._activate_trigger(key, obj)
            return
        mode = obj.get("out_zone_action", "Reverse Trigger Action")
        if mode == "Do Nothing": return
        if mode == "Run Trigger Action":
            self._activate_trigger(key, obj)
        elif oid == 57:
            action = obj.get("trigger_action", "Toggle")
            reverse = dict(Toggle="Toggle", Enable="Disable", Disable="Enable").get(action, "Toggle")
            copy_obj = dict(obj); copy_obj["trigger_action"] = reverse
            self._apply_trigger_action(key, copy_obj)
        elif oid == 55:
            copy_obj = dict(obj)
            copy_obj["move_direction"] = {"Right":"Left", "Left":"Right", "Up":"Down", "Down":"Up"}.get(obj.get("move_direction", "Right"), "Left")
            self._start_move_trigger(key, copy_obj)
        elif oid == 56:
            copy_obj = dict(obj); copy_obj["sound_action"] = "Stop"
            self._play_trigger_sound(key, copy_obj)
        elif oid == 54:
            self._apply_trigger_action(key, obj)

    def _update_trigger_system(self, dt, old_x, old_y):
        cell = self.cell()
        p_size = cell - 4
        player_rect = (self.player_x, self.player_y, p_size, p_size)
        for key, obj in self._objects_for_ids(self.TRIGGER_IDS):
            oid = obj.get("id")
            if not obj.get("enabled", True):
                continue
            mode = obj.get("activation_mode", "Normal")
            # Spawn mode fires exactly once when gameplay first processes the trigger.
            if mode == "Auto activate on spawn":
                if not obj.get("_auto_spawn_activated", False):
                    obj["_auto_spawn_activated"] = True
                    if not obj.get("_trigger_used", False):
                        self._activate_trigger(key, obj)
                        obj["_trigger_latched"] = True
                        obj["_trigger_used"] = True
                continue
            bx, by, bw, bh = self.object_rect(key, obj, cell)
            touched = self.overlaps(player_rect, (bx, by, bw, bh))
            line_x = bx + bw * 0.5
            direction = obj.get("normal_direction", "Both")
            crossed_lr = old_x + p_size <= line_x and self.player_x + p_size >= line_x
            crossed_rl = old_x >= line_x and self.player_x <= line_x
            crossed = (crossed_lr or crossed_rl)
            if direction == "Left to Right": crossed = crossed_lr
            elif direction == "Right to Left": crossed = crossed_rl
            # The normal detector is a virtual vertical column, 99 tiles tall; it has no collision.
            normal_hit = crossed and (old_y + p_size >= self.y - cell*99) and old_y <= self.y + self.rows*cell + cell*99
            activated = touched if mode in ("Touch", "In Touch") else normal_hit
            # Edge-based activation: avoid repeatedly firing while the player remains touching.
            was_touched = bool(obj.get("_was_touched", False))
            touch_entered = touched and not was_touched
            obj["_was_touched"] = touched
            normal_entered = bool(normal_hit)
            activated = (touch_entered if mode in ("Touch", "In Touch") else normal_entered)
            if normal_entered and obj.get("in_zone_enabled", False):
                entering = crossed_lr if obj.get("in_zone_action", "Run Trigger Action") != "Toggle Each Crossing" else not bool(obj.get("_in_zone_state", False))
                obj["_in_zone_state"] = entering
                if entering:
                    self._activate_zone_effect(key, obj, entering=True)
                elif obj.get("out_zone_enabled", False):
                    self._activate_zone_effect(key, obj, entering=False)
                continue
            # If zone mode is off, keep the conventional trigger behavior.
            if obj.get("_trigger_used", False):
                continue
            if activated:
                self._activate_trigger(key, obj)
                obj["_trigger_latched"] = True
                obj["_trigger_used"] = True

    def update_physics(self, dt):
        # Visual animation clock runs in both Edit and Play, independently of physics.
        dt = max(0.0, min(float(dt), 0.05))
        self.animation_time += dt
        self.visual_redraw_elapsed += dt
        if getattr(self.app_ref, "is_playing", False) and getattr(self.app_ref, "multiplayer_room_ready", False):
            self.app_ref.multiplayer_send_elapsed = getattr(self.app_ref, "multiplayer_send_elapsed", 0.0) + min(float(dt), 0.1)
            if self.app_ref.multiplayer_send_elapsed >= 0.10:
                self.app_ref.multiplayer_send_elapsed = 0.0
                self.app_ref.send_multiplayer_state()
        if self.width <= 0:
            return
        if not self.app_ref.is_playing:
            # Keep editor object previews gently animated without running gameplay physics.
            if self.visual_redraw_elapsed >= 1.0 / 12.0:
                self.visual_redraw_elapsed %= (1.0 / 12.0)
                self.redraw()
            return
        # The scheduler runs gameplay at 60 Hz. Do not clamp every physics
        # update to 1/30: that halves moving-platform and carried-player updates.
        self._index_runtime_objects()
        self.jump_buffer_remaining = max(0.0, self.jump_buffer_remaining - dt)
        self.coyote_remaining = max(0.0, self.coyote_remaining - dt)
        self._advance_trigger_runtime(dt)
        self.teleport_cooldown = max(0.0, self.teleport_cooldown - dt)
        for k in list(self.timers):
            self.timers[k] -= dt
            if self.timers[k] <= 0:
                self.timers.pop(k, None)
                obj = self.grid_data.get(k)
                # Breakable platforms are removed when their break timer ends.
                if obj and obj.get("id") == 20:
                    self.grid_data.pop(k, None)
                    self._runtime_index_dirty = True
                # Fake blocks return after their brief vanish period.
        for k in list(self.disappearing_states):
            state = self.disappearing_states[k]
            state["timer"] -= dt
            if state["timer"] <= 0:
                if state["state"] == "arming":
                    state["state"] = "hidden"
                    state["timer"] = 1.8
                elif state["state"] == "hidden":
                    state["state"] = "cooldown"
                    state["timer"] = 0.45
                else:
                    self.disappearing_states.pop(k, None)

        cell = self.cell()
        p_size = cell - 4
        player_rect = (self.player_x, self.player_y, p_size, p_size)
        old_x, old_y = self.player_x, self.player_y
        old_feet = old_y
        was_grounded = self.is_grounded

        gravity = 22.0
        speed = 5.0
        in_water = in_ice = in_sticky = in_slow = in_fast = False
        in_no_jump = in_double = in_ladder = in_fan = False
        in_gravity_up = in_gravity_down = False
        on_slippery_slope = False
        slope_slide_direction = 0
        effect_ids = {16, 17, 18, 24, 25, 30, 32, 33, 34, 35, 36, 37, 38, 40, 41, 51, 52}
        for key, obj in self._nearby_runtime_objects(cell, pad=6):
            if key in self.collected_ids:
                continue
            oid = obj["id"]
            if oid not in effect_ids:
                continue
            bx, by, bw, bh = self.object_rect(key, obj, cell)
            rect = (bx, by, bw, bh)
            # Solid surface effects must also work when standing ON the object,
            # where ordinary rectangle overlap is false.
            touching_top = (
                self.player_x < bx + bw and self.player_x + p_size > bx
                and abs(self.player_y - (by + bh)) <= max(5.0, cell * 0.12)
            )
            hit = self.overlaps(player_rect, rect)
            if oid == 18:
                # A fan blows through a tall air column above its base.
                hit = self.overlaps(player_rect, (bx, by, bw, bh + cell * 4.0))
            if oid in (17, 30) and touching_top:
                hit = True
            if oid in (24, 25) and self.gravity_sign == -1 and bx <= self.player_x + p_size * 0.5 <= bx + bw:
                surface_y = self.slope_surface(obj, bx, by, bw, bh, self.player_x + p_size * 0.5)
                if abs(self.player_y - surface_y) <= max(7.0, cell * 0.18):
                    on_slippery_slope = True
                    slope_slide_direction = -1 if oid == 24 else 1
                    hit = True
            if not hit:
                continue
            if oid == 16: in_water = True
            elif oid == 17: in_ice = True
            elif oid == 30: in_sticky = True
            elif oid == 36: in_slow = True
            elif oid == 37: in_fast = True
            elif oid == 38: in_double = True
            elif oid == 40: in_ladder = True
            elif oid == 41: in_no_jump = True
            elif oid == 18: in_fan = True
            elif oid == 32: in_gravity_up = True
            elif oid == 33: in_gravity_down = True
            elif oid == 34: pass
            elif oid == 35: pass
            elif oid == 51: pass
            elif oid == 52: pass
        # Zone effects latch when touched and remain active until a matching
        # zone changes the mode. This avoids effects flickering at tile edges.
        if in_gravity_up:
            self.zone_modes["gravity"] = "up"
        elif in_gravity_down:
            self.zone_modes["gravity"] = "normal"
        elif any(self.overlaps(player_rect, self.object_rect(k, o, cell)) for k, o in self._objects_by_id.get(34, ())):
            self.zone_modes["gravity"] = "low"
        elif any(self.overlaps(player_rect, self.object_rect(k, o, cell)) for k, o in self._objects_by_id.get(35, ())):
            self.zone_modes["gravity"] = "high"
        elif any(self.overlaps(player_rect, self.object_rect(k, o, cell)) for k, o in self._objects_by_id.get(51, ())):
            self.zone_modes["gravity"] = "normal"
        if in_slow:
            self.zone_modes["speed"] = "slow"
        elif in_fast:
            self.zone_modes["speed"] = "fast"
        elif any(self.overlaps(player_rect, self.object_rect(k, o, cell)) for k, o in self._objects_by_id.get(52, ())):
            self.zone_modes["speed"] = "normal"
        if in_double:
            self.zone_modes["double_jump"] = True
            self.zone_modes["no_jump"] = False
        if in_no_jump:
            self.zone_modes["no_jump"] = True
            self.zone_modes["double_jump"] = False
        gravity_mode = self.zone_modes["gravity"]
        self.gravity_sign = 1 if gravity_mode == "up" else -1
        if gravity_mode == "low":
            gravity = 8.0
        elif gravity_mode == "high":
            gravity = 40.0
        else:
            gravity = 22.0
        gravity *= self.gravity_sign
        if in_water:
            gravity *= 0.35
        if in_sticky:
            speed = min(speed, 1.8)
        if self.zone_modes["speed"] == "slow":
            speed = min(speed, 2.5)
        elif self.zone_modes["speed"] == "fast":
            speed = max(speed, 8.0)
        target_vx = (-speed if self.move_left else 0) + (speed if self.move_right else 0)
        if in_ice or on_slippery_slope:
            # Ice and ramps retain their deliberate low-friction momentum.
            if target_vx:
                self.player_vx += (target_vx - self.player_vx) * min(1.0, dt * 7.0)
            else:
                self.player_vx *= max(0.0, 1.0 - dt * (0.18 if on_slippery_slope else 0.28))
            if on_slippery_slope:
                self.player_vx += slope_slide_direction * 3.8 * dt
        else:
            # Smooth, responsive acceleration: quick start, controlled stop,
            # and slightly softer air control. This avoids the abrupt on/off
            # movement while keeping the original top speed unchanged.
            accelerating = abs(target_vx) > 0.001
            reversing = accelerating and self.player_vx * target_vx < -0.001
            if self.is_grounded:
                accel_rate = 30.0 if accelerating and not reversing else 38.0
                if not accelerating:
                    accel_rate = 42.0
            else:
                accel_rate = 22.0 if accelerating and not reversing else 28.0
                if not accelerating:
                    accel_rate = 25.0
            difference = target_vx - self.player_vx
            max_change = accel_rate * dt
            if difference > max_change:
                difference = max_change
            elif difference < -max_change:
                difference = -max_change
            self.player_vx += difference
            if abs(self.player_vx) < 0.015 and not accelerating:
                self.player_vx = 0.0
        if in_fan:
            self.player_vx += 4.5 * dt
            self.player_vy += 30.0 * dt
        if in_ladder:
            # Ladder automatically carries the player upward on contact.
            self.player_vy = max(self.player_vy, 4.5)
            self.player_vx *= 0.35

        # Horizontal movement uses swept substeps. A long frame after a lag spike
        # must not let the player jump from one side of a wall to the other.
        dx = self.player_vx * cell * dt * 5
        max_collision_step = max(1.0, cell * 0.20)
        horizontal_steps = max(1, int(math.ceil(abs(dx) / max_collision_step)))
        step_dx = dx / horizontal_steps
        for _ in range(horizontal_steps):
            self.player_x += step_dx
            player_step_rect = (self.player_x, self.player_y, p_size, p_size)
            hit_wall = False
            for key, obj in self._nearby_runtime_objects(cell, pad=7):
                oid = obj["id"]
                if oid not in self.SOLID_IDS:
                    continue
                if oid == 21 and self.disappearing_states.get(key, {}).get("state") == "hidden":
                    continue
                if oid == 20 and key in self.broken_blocks:
                    continue
                if oid == 27 and key in self.timers:
                    continue
                bx, by, bw, bh = self.object_rect(key, obj, cell)
                if self.overlaps(player_step_rect, (bx, by, bw, bh)):
                    if step_dx > 0:
                        self.player_x = bx - p_size
                    elif step_dx < 0:
                        self.player_x = bx + bw
                    self.player_vx = 0.0
                    hit_wall = True
                    break
            if hit_wall:
                break

        # Move between adjacent stages when the player crosses a horizontal edge.
        if self.player_x + p_size < self.x and self.app_ref.transition_stage(-1):
            self.redraw()
            return
        if self.player_x > self.x + self.width and self.app_ref.transition_stage(1):
            self.redraw()
            return

        # Gravity and vertical movement.
        self.player_vy += gravity * dt
        if in_water:
            self.player_vy = max(-4.0, min(4.0, self.player_vy))
        dy = self.player_vy * cell * dt * 5
        # Sweep vertical movement too. This prevents tunnelling through thin
        # platforms when Android briefly misses frames or a zone boosts speed.
        vertical_steps = max(1, int(math.ceil(abs(dy) / max_collision_step)))
        step_dy = dy / vertical_steps
        self.is_grounded = False
        for _ in range(vertical_steps):
            previous_y = self.player_y
            self.player_y += step_dy
            player_step_rect = (self.player_x, self.player_y, p_size, p_size)
            hit_vertical = False
            for key, obj in self._nearby_runtime_objects(cell, pad=7):
                oid = obj["id"]
                if oid not in self.SOLID_IDS:
                    continue
                if oid == 21 and self.disappearing_states.get(key, {}).get("state") == "hidden":
                    continue
                if oid == 20 and key in self.broken_blocks:
                    continue
                if oid == 27 and key in self.timers:
                    continue
                bx, by, bw, bh = self.object_rect(key, obj, cell)
                if not self.overlaps(player_step_rect, (bx, by, bw, bh)):
                    continue
                if step_dy < 0 and previous_y >= by + bh - 8:
                    self.player_y = by + bh
                    self.player_vy = 0.0
                    self.is_grounded = True
                    if oid == 20:
                        self.timers[key] = 0.45
                    if oid == 21 and key not in self.disappearing_states:
                        self.disappearing_states[key] = {"state": "arming", "timer": 0.55}
                    hit_vertical = True
                    break
                elif step_dy > 0 and previous_y + p_size <= by + 8:
                    self.player_y = by - p_size
                    self.player_vy = 0.0
                    if self.gravity_sign > 0:
                        self.is_grounded = True
                    hit_vertical = True
                    break
            if hit_vertical:
                break
        # The screen edges act as solid floor/ceiling. With gravity up, the
        # player can run along the ceiling and stays attached there.
        world_bottom = self.y
        world_top = self.y + min(self.height, self.rows * cell)
        if self.gravity_sign < 0 and self.player_y <= world_bottom:
            self.player_y = world_bottom
            self.player_vy = 0.0
            self.is_grounded = True
        elif self.gravity_sign > 0 and self.player_y + p_size >= world_top:
            self.player_y = world_top - p_size
            self.player_vy = 0.0
            self.is_grounded = True
        now_rect = (self.player_x, self.player_y, p_size, p_size)

        # Regular solids: resolve landing and head bumps.
        for key, obj in self._nearby_runtime_objects(cell, pad=7):
            oid = obj["id"]
            if oid not in self.SOLID_IDS:
                continue
            if oid not in self.SOLID_IDS:
                continue
            if oid == 21 and self.disappearing_states.get(key, {}).get("state") == "hidden":
                continue
            if oid == 20 and key in self.broken_blocks:
                continue
            if oid == 27 and key in self.timers:
                continue
            bx, by, bw, bh = self.object_rect(key, obj, cell)
            if not self.overlaps(now_rect, (bx, by, bw, bh)):
                if self.player_vy <= 0 and abs(self.player_y - (by + bh)) < 2 and self.player_x < bx + bw and self.player_x + p_size > bx:
                    self.is_grounded = True
                continue
            if self.player_vy < 0 and old_feet >= by + bh - 8:
                self.player_y = by + bh
                self.player_vy = 0
                self.is_grounded = True
                if oid == 20:
                    self.timers[key] = 0.45
                if oid == 21 and key not in self.disappearing_states:
                    self.disappearing_states[key] = {"state": "arming", "timer": 0.55}
            elif self.player_vy > 0 and old_y + p_size <= by + 8:
                self.player_y = by - p_size
                self.player_vy = 0
                if self.gravity_sign > 0:
                    self.is_grounded = True

        # One-way platforms: land only when crossing the top while falling.
        if self.player_vy <= 0:
            for key, obj in self._objects_by_id.get(42, ()):
                if obj["id"] != 42:
                    continue
                bx, by, bw, bh = self.object_rect(key, obj, cell)
                overlap_x = self.player_x < bx + bw and self.player_x + p_size > bx
                crossed_top = old_feet >= by + bh - 5 and self.player_y <= by + bh
                if overlap_x and crossed_top:
                    self.player_y = by + bh
                    self.player_vy = 0
                    self.is_grounded = True

        # Slopes are treated as triangular solids. Resolve the ramp top using
        # the player's center, and handle side entry separately so opposite-side
        # approaches cannot teleport between ramp tiles or pass through.
        slope_landing = None
        slope_landing_key = None
        player_center = self.player_x + p_size * 0.5
        old_center = old_x + p_size * 0.5
        horizontal_motion = abs(dx) > 0.001

        for key, obj in self._objects_for_ids((24, 25)):
            if obj["id"] not in (24, 25):
                continue
            bx, by, bw, bh = self.object_rect(key, obj, cell)
            if bw <= 0 or bh <= 0:
                continue

            # Side collision is based on the swept horizontal movement, and only
            # blocks when the player's lower body would enter the solid triangle.
            moving_right_into = dx > 0 and old_x + p_size <= bx + 1 and self.player_x + p_size > bx
            moving_left_into = dx < 0 and old_x >= bx + bw - 1 and self.player_x < bx + bw
            if moving_right_into or moving_left_into:
                edge_x = bx if moving_right_into else bx + bw
                edge_surface = self.slope_surface(obj, bx, by, bw, bh, edge_x)
                feet_after_vertical = self.player_y
                body_overlaps_triangle_height = (
                    feet_after_vertical < edge_surface - 1
                    and feet_after_vertical + p_size > by + 1
                )
                # Allow entry at the low end, and allow a player already standing
                # on a neighboring ramp to cross a shared edge without hitting an
                # invisible vertical wall at the join.
                low_edge = (
                    (obj.get("direction", "UP_RIGHT") == "UP_RIGHT" and moving_right_into)
                    or (obj.get("direction", "UP_RIGHT") == "UP_LEFT" and moving_left_into)
                )
                feet_match_edge = abs(old_feet - edge_surface) <= max(cell * 0.22, abs(dx) + 5.0)
                can_walk_up = (
                    self.gravity_sign == -1 and was_grounded and self.player_vy <= 0
                    and (
                        (low_edge and old_feet >= by - 3)
                        or feet_match_edge
                    )
                )
                if body_overlaps_triangle_height and not can_walk_up:
                    if moving_right_into:
                        self.player_x = bx - p_size
                    else:
                        self.player_x = bx + bw
                    self.player_vx = 0.0
                    player_center = self.player_x + p_size * 0.5

            # A ramp top can only catch the player if the center lies inside
            # the ramp's horizontal span and the player is descending or grounded.
            if bx <= player_center <= bx + bw and self.gravity_sign == -1:
                surface = self.slope_surface(obj, bx, by, bw, bh, player_center)
                old_sample_x = max(bx, min(bx + bw, old_center))
                old_surface = self.slope_surface(obj, bx, by, bw, bh, old_sample_x)
                feet = self.player_y
                close_to_old_ramp = (
                    was_grounded
                    and abs(old_feet - old_surface) <= max(cell * 0.22, abs(dx) + 5.0)
                )
                crossed_surface = old_feet >= surface - abs(dx) - abs(dy) - 5.0 and feet <= surface + 4.0
                following_ramp = close_to_old_ramp and horizontal_motion and self.player_vy <= 0
                already_on_surface = was_grounded and abs(feet - surface) <= max(5.0, abs(dx) + 2.0)
                can_land = (
                    self.player_vy <= 0 and feet + p_size > by
                    and (crossed_surface or following_ramp or already_on_surface)
                )
                if can_land and (slope_landing is None or surface > slope_landing):
                    slope_landing = surface
                    slope_landing_key = key

            # Solid underside when the player jumps into the bottom of a ramp.
            old_head = old_y + p_size
            new_head = self.player_y + p_size
            if (
                self.player_vy > 0 and old_head <= by + 2
                and new_head > by and self.player_x < bx + bw
                and self.player_x + p_size > bx and self.player_y < by
            ):
                self.player_y = by - p_size
                self.player_vy = 0.0

        if slope_landing is not None:
            self.player_y = slope_landing
            self.player_vy = 0.0
            self.is_grounded = True

        if self.is_grounded:
            self.coyote_remaining = 0.10
            if self.jump_buffer_remaining > 0.0:
                self.player_vy = -5.9 if self.gravity_sign > 0 else 5.9
                self.is_grounded = False
                self.coyote_remaining = 0.0
                self.jump_buffer_remaining = 0.0
                self.used_double_jump = False
        elif was_grounded:
            self.coyote_remaining = max(self.coyote_remaining, 0.10)

        if self.is_grounded and not was_grounded:
            self.land_bounce = 0.10
            contact_pad = max(4.0, cell * 0.15)
            for mover_key, mover_obj in self._objects_for_ids((4, 19, 48, 49)):
                mover_id = mover_obj.get("id")
                if not mover_obj.get("enabled", True):
                    continue
                moving_builtin = mover_id in (4, 19, 48, 49)
                move_dx, move_dy = self.move_offsets.get(mover_key, (0.0, 0.0))
                moving_by_trigger = abs(move_dx) > 0.001 or abs(move_dy) > 0.001
                if not (moving_builtin or moving_by_trigger):
                    continue
                mx, my, mw, mh = self.object_rect(mover_key, mover_obj, cell)
                overlap_x = self.player_x < mx + mw and self.player_x + p_size > mx
                near_surface = (abs(self.player_y - (my + mh)) <= contact_pad or
                                 abs((self.player_y + p_size) - my) <= contact_pad)
                if overlap_x and near_surface:
                    self.landing_input_until = time.monotonic() + 0.09
                    break

        touching_slope = slope_landing is not None
        # Carry player on moving platforms and apply conveyor movement.
        if was_grounded and self.player_vy == 0:
            for key, obj in self._objects_for_ids((4, 39)):
                oid = obj["id"]
                if oid == 4:
                    bx, by, bw, bh = self.object_rect(key, obj, cell)
                    if abs(old_feet - (by + bh)) < cell * 0.15 and self.player_x < bx + bw and self.player_x + p_size > bx:
                        self.player_x += (self.get_platform_x_offset(oid, key) - math.sin((self.elapsed_time - dt) * 2.5)) * cell
                elif oid == 39:
                    bx, by, bw, bh = self.object_rect(key, obj, cell)
                    if abs(self.player_y - (by + bh)) < 3 and self.player_x < bx + bw and self.player_x + p_size > bx:
                        self.player_x += cell * dt * 1.4

        self.player_angle += ((25.0 if touching_slope else 0.0) - self.player_angle) * min(1.0, dt * 12)
        player_rect = (self.player_x, self.player_y, p_size, p_size)
        self._update_trigger_system(dt, old_x, old_y)

        # Object contact effects.
        # A breakable platform starts its countdown while the player stands on it,
        # even if collision resolution has already placed the feet exactly on top.
        for key, obj in self._objects_by_id.get(20, ()):
            if obj["id"] != 20 or key in self.broken_blocks or key in self.timers:
                continue
            bx, by, bw, bh = self.object_rect(key, obj, cell)
            standing = (self.player_x < bx + bw and self.player_x + p_size > bx
                        and abs(self.player_y - (by + bh)) <= max(4.0, cell * 0.12))
            if standing and ((self.gravity_sign < 0 and self.is_grounded) or (self.gravity_sign > 0 and self.is_grounded)):
                self.timers[key] = 0.65
        # Contact tests must use the resolved current position, not the rectangle
        # captured before this frame's movement. This is especially important for portals.
        player_rect = (self.player_x, self.player_y, p_size, p_size)
        contact_ids = {2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 19, 22, 27, 29, 31, 46, 47, 48, 49}
        for key, obj in self._nearby_runtime_objects(cell, pad=7):
            if key in self.collected_ids:
                continue
            oid = obj["id"]
            if oid not in contact_ids:
                continue
            bx, by, bw, bh = self.object_rect(key, obj, cell)
            hit = self.overlaps(player_rect, (bx, by, bw, bh))
            if not hit:
                continue
            if oid in (2, 3, 15, 19, 31, 47, 48, 49):
                self.spawn_player()
                self.redraw()
                return
            if oid == 5:
                self.active_spawn = (bx, by + bh)
            elif oid in (6, 7):
                if key not in self.collected_ids:
                    self.score += 10 if oid == 6 else 50
                    self.collected_ids.add(key)
            elif oid == 8:
                self.has_key = True
                self.collected_ids.add(key)
            elif oid == 9 and self.has_key and not self._door_is_trigger_linked(obj):
                # Unlinked doors keep the old key behavior. A grouped door targeted
                # by a trigger stays closed until that trigger changes its state.
                self.collected_ids.add(key)
            elif oid == 10 and key not in self.object_contact_latches:
                self.toggle_states[key] = not self.toggle_states.get(key, False)
                self.object_contact_latches.add(key)
                self.timers[key] = 2.0
                for target_key, target_obj in self.grid_data.items():
                    if target_obj["id"] in (21, 27, 28):
                        if self.toggle_states[key]:
                            if target_obj["id"] == 21:
                                self.disappearing_states[target_key] = {"state": "hidden", "timer": 1.2}
                            elif target_obj["id"] == 27:
                                self.timers[target_key] = 1.2
                            else:
                                self.toggle_states[target_key] = True
                        else:
                            self.disappearing_states.pop(target_key, None)
                            self.timers.pop(target_key, None)
                            self.toggle_states[target_key] = False
            elif oid in (11, 12, 13, 14) and self.player_vy <= 0.5 and key not in self.object_contact_latches:
                self.player_vy = {11: math.sqrt(3.0 * 44.0 / 5.0), 12: math.sqrt(4.5 * 44.0 / 5.0), 13: math.sqrt(6.0 * 44.0 / 5.0), 14: math.sqrt(6.0 * 44.0 / 5.0)}[oid]
                self.is_grounded = False
                self.object_contact_latches.add(key)
            elif oid == 22 and self.teleport_cooldown <= 0:
                end = next((self.object_rect(k, o, cell) for k, o in self._objects_by_id.get(23, ())), None)
                if end:
                    base_x = end[0] + (end[2] - p_size) * 0.5
                    base_y = end[1] + end[3] + 2
                else:
                    base_x = self.player_x + cell * 4
                    base_y = self.player_y
                safe_position = self._find_safe_teleport_position(base_x, base_y, p_size, cell)
                if safe_position is not None:
                    self.player_x, self.player_y = safe_position
                    # Clear vertical momentum so a high-speed fall cannot tunnel
                    # through the first solid surface immediately after teleporting.
                    self.player_vy = 0.0
                    self.is_grounded = False
                    player_rect = (self.player_x, self.player_y, p_size, p_size)
                    self.teleport_cooldown = 0.75
                else:
                    # A blocked exit must not put the player inside a wall/platform.
                    self.app_ref.status_label.text = "Portal exit is blocked by a solid object"
                    self.teleport_cooldown = 0.25
            elif oid == 27:
                self.timers[key] = 0.15
            elif oid == 29:
                self.player_angle = 8.0 if self.move_right else (-8.0 if self.move_left else 0.0)
            elif oid == 46 and key not in self.object_contact_latches:
                self.toggle_states[key] = not self.toggle_states.get(key, False)
                self.object_contact_latches.add(key)
                for target_key, target_obj in self.grid_data.items():
                    if target_obj["id"] in (21, 27, 28):
                        if self.toggle_states[key]:
                            if target_obj["id"] == 21:
                                self.disappearing_states[target_key] = {"state": "hidden", "timer": 1.2}
                            elif target_obj["id"] == 27:
                                self.timers[target_key] = 1.2
                            else:
                                self.toggle_states[target_key] = True
                        else:
                            self.disappearing_states.pop(target_key, None)
                            self.timers.pop(target_key, None)
                            self.toggle_states[target_key] = False
        # Collected items are hidden for the current play session only. They stay
        # in grid_data so returning to Edit never destroys the level design.
        for key in list(self.object_contact_latches):
            obj = self.grid_data.get(key)
            if not obj:
                self.object_contact_latches.discard(key)
                continue
            rect = self.object_rect(key, obj, cell)
            if not self.overlaps(player_rect, rect):
                self.object_contact_latches.discard(key)

        for key, _obj in self._objects_by_id.get(19, ()):
            self.enemy_directions.setdefault(key, 1)

        end_col = self.get_auto_endpoint_col()
        end_x = self.x + end_col * cell
        if end_x <= self.player_x < end_x + cell:
            if self.app_ref.current_stage_index < len(self.app_ref.stages) - 1:
                if self.app_ref.transition_stage(1):
                    self.redraw()
                    return
            else:
                self.app_ref.show_win_popup()
                return

        # Render moving gameplay at the same 60 Hz cadence as physics.
        # A player standing on a moving platform may have near-zero velocity
        # while the platform itself moves, so detect animated movers directly.
        moving_ids = (4, 19, 48, 49)  # moving platform, enemy, saw, fireball
        has_animated_mover = any(self._objects_by_id.get(oid) for oid in moving_ids)
        has_trigger_motion = any(
            abs(offset[0]) > 0.001 or abs(offset[1]) > 0.001
            for offset in self.move_offsets.values()
        )
        moving_visually = (
            abs(self.player_vx) > 0.08 or abs(self.player_vy) > 0.08
            or self.move_left or self.move_right or self.move_up or self.move_down
            or has_animated_mover or has_trigger_motion
        )
        render_interval = (1.0 / 60.0) if moving_visually else (1.0 / 12.0)
        if self.visual_redraw_elapsed >= render_interval:
            self.visual_redraw_elapsed %= render_interval
            self.redraw()

    def redraw(self, *args):
        self.canvas.clear()
        cell = self.cell()
        total_h = self.rows * cell
        editor = not self.app_ref.is_playing
        palette = self.app_ref._theme() if hasattr(self.app_ref, "_theme") else THEMES["Midnight"]
        quality = getattr(self.app_ref, "settings", {}).get("graphics_quality", "Balanced")
        with self.canvas:
            # Each stage owns its background. Default follows the selected app theme.
            stage_list = getattr(self.app_ref, "stages", []) or []
            stage_index = int(getattr(self.app_ref, "current_stage_index", 0))
            stage_data = stage_list[stage_index] if 0 <= stage_index < len(stage_list) else {}
            background_name = stage_data.get("background", "Default") if isinstance(stage_data, dict) else "Default"
            background_colors = {
                "Midnight": (0.025, 0.04, 0.085, 1), "Deep Space": (0.012, 0.018, 0.055, 1),
                "Ocean": (0.015, 0.075, 0.12, 1), "Forest": (0.018, 0.075, 0.055, 1),
                "Sunset": (0.16, 0.045, 0.09, 1), "Violet": (0.075, 0.035, 0.14, 1),
                "Light Grid": (0.72, 0.80, 0.9, 1),
            }
            bg_color = palette["bg"] if background_name == "Default" else background_colors.get(background_name, palette["bg"])
            Color(*bg_color)
            Rectangle(pos=self.pos, size=self.size)
            if editor:
                Color(*palette["grid"])
                for c in range(self.cols + 1):
                    Line(points=[self.x + c * cell, self.y, self.x + c * cell, self.y + total_h], width=1)
                for r in range(self.rows + 1):
                    Line(points=[self.x, self.y + r * cell, self.x + self.cols * cell, self.y + r * cell], width=1)

            # Render only the currently active stage; future stages remain data-only.
            for key, obj in self._active_stage_render_items(cell):
                oid = obj["id"]
                if not editor and key in self.collected_ids:
                    continue
                if not editor and not obj.get("enabled", True):
                    continue
                if oid == 27 and key in self.timers:
                    continue
                if oid == 21 and self.disappearing_states.get(key, {}).get("state") == "hidden":
                    continue
                if oid == 20 and key in self.broken_blocks:
                    continue
                move_dx, move_dy = self.move_offsets.get(key, (0.0, 0.0))
                effective_col = key[0] + move_dx
                effective_row = key[1] + move_dy
                if not editor and oid in (4, 19, 48, 49):
                    effective_col += self.get_platform_x_offset(oid, key)
                cx, cy = self.x + effective_col * cell, self.y + effective_row * cell
                tw, th = self._tile_dimensions(key, obj)
                # Skip off-screen geometry before creating Kivy instructions.
                # A small margin keeps moving objects and edge highlights from popping.
                if oid not in self.TRIGGER_IDS and (
                        cx + cell * tw < self.x - cell or cx > self.right + cell or
                        cy + cell * th < self.y - cell or cy > self.top + cell):
                    continue
                pw, ph = cell * tw - 4, cell * th - 4 if th >= 1 else cell * th
                px, py = cx + 2, cy + 2
                # Collectibles float subtly; spinning hazards rotate continuously.
                if not editor and oid in (6, 7):
                    py += math.sin(self.animation_time * 4.0 + key[0] * 0.7 + key[1]) * cell * 0.055
                if oid in self.TRIGGER_IDS:
                    # Trigger objects are editor-only circular tokens; runtime keeps their hitboxes invisible.
                    if not editor:
                        continue
                    mode = obj.get("activation_mode", "Normal")
                    trigger_color = get_color_rgba(obj.get("color", "WHITE"))
                    Color(*trigger_color)
                    Ellipse(pos=(px + pw*0.08, py + ph*0.08), size=(pw*0.84, ph*0.84))
                    Color(1, 1, 1, 0.92)
                    Line(ellipse=(px + pw*0.14, py + ph*0.14, pw*0.72, ph*0.72), width=max(1.2, cell*0.045))
                    Color(0.035, 0.05, 0.09, 0.95)
                    Ellipse(pos=(px + pw*0.40, py + ph*0.40), size=(pw*0.20, ph*0.20))
                    Color(1, 1, 1, 0.95)
                    Ellipse(pos=(px + pw*0.455, py + ph*0.455), size=(pw*0.09, ph*0.09))
                    if mode == "In Touch":
                        Color(0.1, 0.85, 1.0, 0.22)
                        Line(ellipse=(px - pw*0.08, py - ph*0.08, pw*1.16, ph*1.16), width=1.6, dash_length=5, dash_offset=3)
                    else:
                        Color(1.0, 0.8, 0.2, 0.95)
                        detector_x = px + pw * 0.5
                        Line(points=[detector_x, self.y, detector_x, self.y + total_h], width=1.8, dash_length=5, dash_offset=3)
                    if key == self.selected_key:
                        Color(1, 0.9, 0.1, 1)
                        Line(ellipse=(px - 2, py - 2, pw + 4, ph + 4), width=2.5)
                    continue
                rgba = get_color_rgba(obj["color"])
                if not editor and "alpha" in obj:
                    rgba = (*rgba[:3], max(0.0, min(1.0, rgba[3] * float(obj.get("alpha", 1.0)))))
                if oid == 28 and not editor:
                    rgba = (0.9, 0.9, 0.9, 0.12)
                if oid in (32, 33, 34, 35, 36, 37, 38, 41, 51, 52):
                    rgba = (*rgba[:3], 0.24 if not editor else 0.38)
                PushMatrix()
                animated_rotation = float(obj.get("rotation", 0))
                if oid in (3, 48):
                    animated_rotation += self.animation_time * (250 if oid == 3 else -320)
                elif oid == 49:
                    animated_rotation += math.sin(self.animation_time * 7.0) * 12
                Rotate(angle=animated_rotation, origin=(px + pw/2, py + ph/2))
                Color(*rgba)
                shape = obj["shape"].upper()
                if oid == 5:
                    Color(0.1, 0.9, 0.4, 0.22)
                    Ellipse(pos=(px - cell * 0.15, py - cell * 0.15), size=(pw + cell * 0.3, ph + cell * 0.3))
                    Color(0.2, 1, 0.4, 1)
                    Rectangle(pos=(px + pw * 0.15, py), size=(max(2, cell * 0.08), ph))
                    Mesh(vertices=[px + pw * 0.2, py + ph * 0.85, 0, 0, px + pw, py + ph * 0.7, 0, 0, px + pw * 0.2, py + ph * 0.52, 0, 0], indices=[0, 1, 2], mode="triangles")
                elif oid == 8:
                    # Key: hollow circular bow, with its center aligned to the shaft.
                    ring_x, ring_y = px + pw * 0.08, py + ph * 0.25
                    ring_w, ring_h = pw * 0.38, ph * 0.38
                    Color(*rgba)
                    Ellipse(pos=(ring_x, ring_y), size=(ring_w, ring_h))
                    # Cut out the center so the bow looks like a real key ring.
                    Color(0.1, 0.1, 0.13, 1)
                    hole_w, hole_h = ring_w * 0.48, ring_h * 0.48
                    Ellipse(pos=(ring_x + (ring_w-hole_w)/2, ring_y + (ring_h-hole_h)/2), size=(hole_w, hole_h))
                    Color(*rgba)
                    shaft_y = py + ph * 0.365
                    Rectangle(pos=(px + pw * 0.39, shaft_y), size=(pw * 0.47, ph * 0.11))
                    Rectangle(pos=(px + pw * 0.69, shaft_y - ph * 0.13), size=(pw * 0.10, ph * 0.24))
                    Rectangle(pos=(px + pw * 0.79, shaft_y - ph * 0.13), size=(pw * 0.10, ph * 0.19))
                elif oid == 45:
                    # Text prop: draw text only, with no tile, background, or border.
                    text_value = str(obj.get("display_text", "Enter Your Text")) or "Enter Your Text"
                    font_size = max(14, min(48, int(cell * 0.62)))
                    # Respect the same runtime alpha as every other target object.
                    # Editor text remains fully visible so it can always be edited.
                    text_alpha = 1.0 if editor else max(0.0, min(1.0, float(obj.get("alpha", 1.0))))
                    text_cache_key = (text_value, font_size, round(text_alpha, 2))
                    texture = self._text_texture_cache.get(text_cache_key)
                    if texture is None:
                        text_label = CoreLabel(text=text_value, font_size=font_size,
                                               color=(1, 1, 1, text_alpha), font_name="Roboto")
                        text_label.refresh()
                        texture = text_label.texture
                        if len(self._text_texture_cache) >= 256:
                            self._text_texture_cache.clear()
                        self._text_texture_cache[text_cache_key] = texture
                    Color(1, 1, 1, text_alpha)
                    Rectangle(texture=texture,
                              pos=(px, py + max(0, (ph - texture.height) / 2)),
                              size=texture.size)
                elif "TRIANGLE" in shape:
                    Mesh(vertices=[px+pw/2,py+ph,0,0, px,py,0,0, px+pw,py,0,0], indices=[0,1,2], mode="triangles")
                elif "RAMP" in shape:
                    vertices = ([px,py,0,0, px+pw,py,0,0, px+pw,py+ph,0,0] if obj.get("direction", "UP_RIGHT") == "UP_RIGHT"
                                else [px,py,0,0, px+pw,py,0,0, px,py+ph,0,0])
                    Mesh(vertices=vertices, indices=[0,1,2], mode="triangles")
                elif "POLYGON" in shape:
                    Mesh(vertices=[px+pw/2,py+ph,0,0, px+pw,py+ph/2,0,0, px+pw/2,py,0,0, px,py+ph/2,0,0], indices=[0,1,2,0,2,3], mode="triangles")
                elif "CIRCLE" in shape or "OVAL" in shape:
                    Ellipse(pos=(px, py), size=(pw, ph))
                else:
                    Rectangle(pos=(px, py), size=(pw, ph))
                if quality != "Low":
                    # High adds an extra soft hazard aura; Balanced keeps the
                    # normal polished look without this additional overdraw.
                    if quality == "High" and not editor and oid in (2, 3, 43, 47, 48, 49):
                        pulse = 0.5 + 0.5 * math.sin(self.animation_time * 4.0 + key[0] * 0.7)
                        aura_color = (1.0, 0.16, 0.06, 0.07 + pulse * 0.06)
                        Color(*aura_color)
                        Ellipse(pos=(px - pw * 0.12, py - ph * 0.12),
                                size=(pw * 1.24, ph * 1.24))
                    # Trigger tokens are circular with a crisp double-ring and central marker.
                    if editor and oid in (50, 54, 55, 56, 57):
                        Color(1, 1, 1, 0.72)
                        Line(ellipse=(px + pw*0.10, py + ph*0.10, pw*0.80, ph*0.80), width=max(1.2, cell*0.045))
                        Color(0.04, 0.06, 0.10, 0.88)
                        Ellipse(pos=(px + pw*0.39, py + ph*0.39), size=(pw*0.22, ph*0.22))
                        Color(1, 1, 1, 0.95)
                        Ellipse(pos=(px + pw*0.45, py + ph*0.45), size=(pw*0.10, ph*0.10))
                    # Consistent highlights, bevels and accents make objects feel finished.
                    if oid in (1, 4, 9, 17, 20, 21, 26, 29, 39, 42, 44, 47):
                        Color(1, 1, 1, 0.20)
                        Line(points=[px + 2, py + ph - 2, px + pw - 2, py + ph - 2], width=max(1, cell * 0.035))
                        Color(0, 0, 0, 0.20)
                        Line(points=[px + 2, py + 2, px + pw - 2, py + 2], width=max(1, cell * 0.035))
                    if oid == 6 and quality != "Low":
                        pulse = 0.5 + 0.5 * math.sin(self.animation_time * 6.0 + key[0])
                        Color(1.0, 0.82, 0.18, 0.12 + pulse * 0.16)
                        Ellipse(pos=(px - pw * 0.18, py - ph * 0.18), size=(pw * 1.36, ph * 1.36))
                        Color(1.0, 1.0, 0.72, 0.9)
                        Line(points=[px + pw*.34, py + ph*.72, px + pw*.48, py + ph*.84], width=max(1, cell*.045))
                    elif oid == 7 and quality != "Low":
                        pulse = 0.5 + 0.5 * math.sin(self.animation_time * 5.0 + key[1])
                        Color(0.35, 0.9, 1.0, 0.12 + pulse * 0.20)
                        Ellipse(pos=(px - pw*.15, py - ph*.15), size=(pw*1.3, ph*1.3))
                        Color(1, 1, 1, 0.75)
                        Line(points=[px + pw*.5, py + ph*.78, px + pw*.62, py + ph*.58], width=max(1, cell*.04))
                    elif oid in (22, 23) and quality != "Low":
                        pulse = 0.5 + 0.5 * math.sin(self.animation_time * 3.5)
                        Color(0.5, 0.85, 1, 0.22 + pulse*.18)
                        Line(ellipse=(px - pw*.12, py - ph*.12, pw*1.24, ph*1.24), width=max(1, cell*.05))
                    elif oid in (15, 16) and quality != "Low":
                        wave = math.sin(self.animation_time * 5.0 + key[0]) * ph * .06
                        Color(1, 1, 1, .38)
                        Line(points=[px + pw*.08, py + ph*.72 + wave, px + pw*.42, py + ph*.72 - wave,
                                     px + pw*.72, py + ph*.72 + wave], width=max(1, cell*.035))
                    elif oid == 18 and quality != "Low":
                        fan_angle = self.animation_time * 420
                        Color(0.78, 0.95, 1, .9)
                        for blade in range(3):
                            a = math.radians(fan_angle + blade*120)
                            cx_f, cy_f = px + pw*.5, py + ph*.5
                            Line(points=[cx_f, cy_f, cx_f + math.cos(a)*pw*.28, cy_f + math.sin(a)*ph*.32], width=max(1, cell*.055))
                    if oid == 3:
                        Color(0.1, 0.1, 0.1, 1)
                        Line(circle=(px + pw/2, py + ph/2, min(pw, ph)*.38), width=1.5)
                    if oid == 31:
                        Color(1, 0, 0, .85)
                        Rectangle(pos=(px, py + ph*.4), size=(pw, max(2, ph*.2)))
                    if oid == 18:
                        Color(0.7, 0.9, 1, .9)
                        for n in range(3):
                            Line(points=[px + pw*.2, py + ph*(.25+n*.25), px + pw*.8, py + ph*(.25+n*.25)], width=1.2)
                    if oid == 40:
                        Color(0.25, 0.12, 0.03, 1)
                        for n in range(1, 6):
                            Line(points=[px, py + ph*n/6, px + pw, py + ph*n/6], width=1.2)
                    if oid == 42:
                        Color(0.2, 0.7, 1, 1)
                        Line(points=[px, py + ph*.15, px + pw, py + ph*.15], width=1.4)
                    if oid in (32, 33, 34, 35, 36, 37, 38, 41, 51, 52):
                        Color(*get_color_rgba(obj["color"] )[:3], 0.95)
                        Line(rectangle=(px, py, pw, ph), width=1.4)
                    # Extra hand-drawn object polish. These are ordinary Kivy canvas
                    # primitives (no GLSL, shader, texture pipeline, or physics edits).
                    if oid in (24, 25):
                        # Bright running edge makes both ramp directions readable.
                        Color(0.78, 0.91, 1.0, 0.88)
                        if obj.get("direction", "UP_RIGHT") == "UP_RIGHT":
                            Line(points=[px + pw*.06, py + ph*.08, px + pw*.92, py + ph*.92], width=max(1.4, cell*.055))
                            Color(1, 1, 1, .20)
                            Line(points=[px + pw*.12, py + ph*.08, px + pw*.92, py + ph*.88], width=max(1, cell*.025))
                        else:
                            Line(points=[px + pw*.08, py + ph*.92, px + pw*.94, py + ph*.08], width=max(1.4, cell*.055))
                            Color(1, 1, 1, .20)
                            Line(points=[px + pw*.08, py + ph*.86, px + pw*.88, py + ph*.08], width=max(1, cell*.025))
                    elif oid in (2, 43, 47):
                        # Sharp inner edge and small glint; fake spikes remain visual only.
                        Color(1.0, .72, .62, .88 if oid != 43 else .58)
                        Line(points=[px + pw*.50, py + ph*.88, px + pw*.50, py + ph*.54], width=max(1, cell*.035))
                        Color(.25, .035, .035, .45)
                        Line(points=[px + pw*.12, py + ph*.08, px + pw*.88, py + ph*.08], width=max(1, cell*.035))
                        if quality != "Low" and not editor:
                            pulse = .5 + .5 * math.sin(self.animation_time*4.0 + key[0]*.8)
                            Color(1, .12, .04, .07 + pulse*.08)
                            Line(points=[px + pw*.5, py + ph*.98, px + pw*.5, py + ph*1.12], width=max(1, cell*.06))
                    elif oid in (3, 48):
                        # A saw hub and radial teeth reinforce the existing rotation.
                        cx_s, cy_s = px + pw*.5, py + ph*.5
                        radius = min(pw, ph)*.34
                        Color(.16, .025, .025, .95)
                        Ellipse(pos=(cx_s-radius*.30, cy_s-radius*.30), size=(radius*.60, radius*.60))
                        Color(1.0, .72, .66, .95)
                        Ellipse(pos=(cx_s-radius*.13, cy_s-radius*.13), size=(radius*.26, radius*.26))
                        for tooth in range(8):
                            a = math.radians(tooth*45)
                            Line(points=[cx_s + math.cos(a)*radius*.72, cy_s + math.sin(a)*radius*.72,
                                         cx_s + math.cos(a)*radius*1.08, cy_s + math.sin(a)*radius*1.08],
                                 width=max(1.2, cell*.055))
                    elif oid == 9:
                        # Door frame, inset panels and a lit handle; door state logic untouched.
                        Color(.12, .055, .025, .95)
                        Line(rectangle=(px + pw*.08, py + ph*.05, pw*.84, ph*.90), width=max(1.5, cell*.055))
                        Color(1.0, .76, .34, .52)
                        Line(rectangle=(px + pw*.18, py + ph*.16, pw*.64, ph*.70), width=max(1, cell*.035))
                        Color(1.0, .82, .36, .95)
                        Ellipse(pos=(px + pw*.73, py + ph*.46), size=(max(2, pw*.07), max(2, ph*.07)))
                    elif oid in (32, 33, 34, 35, 36, 37, 38, 41, 51, 52):
                        # Animated directional marks make zone types easier to read.
                        pulse = .5 + .5*math.sin(self.animation_time*3.2 + key[0]*.6)
                        zone_rgb = get_color_rgba(obj["color"] )[:3]
                        Color(zone_rgb[0], zone_rgb[1], zone_rgb[2], .18 + pulse*.18)
                        for stripe in range(3):
                            yy = py + ph*(.22 + stripe*.25) + math.sin(self.animation_time*2.5 + stripe + key[1]) * ph*.025
                            Line(points=[px + pw*.18, yy, px + pw*.82, yy], width=max(1, cell*.025))
                        Color(1, 1, 1, .5)
                        if oid in (32, 33, 51):
                            direction = 1 if oid == 32 else -1
                            cx_z = px + pw*.5
                            cy_z = py + ph*(.5 + math.sin(self.animation_time*2.4)*.08)
                            Line(points=[cx_z, cy_z - direction*ph*.12, cx_z, cy_z + direction*ph*.12], width=max(1, cell*.04))
                            Line(points=[cx_z - pw*.10, cy_z + direction*ph*.02, cx_z, cy_z + direction*ph*.12,
                                         cx_z + pw*.10, cy_z + direction*ph*.02], width=max(1, cell*.04))
                if oid == 46 and self.toggle_states.get(key, False):
                    Color(0.1, 1, 0.2, 1)
                    Ellipse(pos=(px + pw*.3, py + ph*.3), size=(pw*.4, ph*.4))

                if editor and key == self.selected_key:
                    Color(1, 0.9, 0.1, 1)
                    Line(rectangle=(px, py, pw, ph), width=2.5)
                PopMatrix()

            if not editor:
                Color(0.2, 0.8, 0.2, 1)
                end_col = self.get_auto_endpoint_col()
                Rectangle(pos=(self.x + end_col*cell + 2, self.y + 2), size=(cell - 4, total_h - 4))
                # The owner/admin avatar is always red. Regular accounts can never
                # equip or load the admin-only red appearance from local settings.
                admin_check = getattr(self.app_ref, "_admin_allowed", None)
                is_admin_player = bool(callable(admin_check) and admin_check())
                skin_name = getattr(self.app_ref, "settings", {}).get("skin", "Green")
                skin_colors = {
                    "Green": (0.2, 0.9, 0.3, 1),
                    "Blue": (0.2, 0.55, 1.0, 1),
                    "Red": (1.0, 0.2, 0.2, 1),
                    "Purple": (0.7, 0.3, 1.0, 1),
                    "Gold": (1.0, 0.72, 0.12, 1),
                    "Cyan": (0.1, 0.9, 0.9, 1),
                    "Orange": (1.0, 0.42, 0.12, 1),
                    "Pink": (1.0, 0.28, 0.62, 1),
                    "White": (0.95, 0.95, 1.0, 1),
                }
                p_size = cell - 4
                skin = (1.0, 0.2, 0.2, 1) if is_admin_player else skin_colors.get(skin_name, skin_colors["Green"])
                # Low = deliberately simple September-style square; Balanced/High
                # retain the newer movement animation. Physics is identical.
                moving = abs(self.player_vx) > 0.12
                if quality == "Low":
                    sx = sy = 1.0
                elif not self.is_grounded:
                    sx, sy = 0.94, 1.07
                elif moving:
                    sx = 1.0 + math.sin(self.animation_time * 15.0) * 0.035
                    sy = 1.0 - math.sin(self.animation_time * 15.0) * 0.035
                else:
                    idle = math.sin(self.animation_time * 2.7) * 0.018
                    sx, sy = 1.0 + idle, 1.0 - idle
                if self.land_bounce > 0:
                    self.land_bounce = max(0.0, self.land_bounce - 1/60)
                    if quality != "Low":
                        sx += self.land_bounce * 1.8
                        sy -= self.land_bounce * 1.2
                draw_w, draw_h = p_size * sx, p_size * sy
                draw_x = self.player_x + (p_size - draw_w) * .5
                draw_y = self.player_y + (p_size - draw_h) * .5
                # Low quality skips the soft contact shadow to reduce overdraw.
                if quality != "Low":
                    Color(0, 0, 0, .24)
                    Ellipse(pos=(self.player_x + p_size*.12, self.player_y - cell*.08), size=(p_size*.76, cell*.16))
                # Equipped cosmetic trail is rendered in-game (not only in the shop).
                trail_name = getattr(self.app_ref, "settings", {}).get("trail", "None")
                # Cosmetic trails remain visible in every quality preset.
                # Low uses only two small particles to keep the September-style
                # look lightweight without hiding an equipped trail.
                if (moving or not self.is_grounded) and trail_name != "None":
                    trail_colors = {
                        "Spark": (1.0, 0.88, 0.18, 0.82),
                        "Flame": (1.0, 0.30, 0.06, 0.78),
                        "Ice": (0.20, 0.78, 1.0, 0.82),
                        "Rainbow": (0.9, 0.3, 0.9, 0.82),
                    }
                    trail_color = trail_colors.get(trail_name, skin)
                    trail_dir = -1 if self.player_vx > 0 else 1
                    quality_now = getattr(self.app_ref, "settings", {}).get("graphics_quality", "Balanced")
                    trail_count = 2 if quality_now == "Low" else (7 if quality_now == "High" else 5)
                    # Draw broad, thick streaks fully BEHIND the player's edge.
                    # The first particle starts outside the body instead of
                    # appearing as a tiny dot embedded inside the square.
                    trail_w = cell * (0.48 if quality_now == "Low" else 0.56)
                    trail_h = cell * (0.30 if quality_now == "Low" else 0.34)
                    gap = cell * 0.07
                    for trail_i in range(trail_count):
                        fade = (trail_count - trail_i) / float(trail_count)
                        if trail_dir < 0:
                            tx = self.player_x - gap - trail_w - trail_i * cell * 0.19
                        else:
                            tx = self.player_x + p_size + gap + trail_i * cell * 0.19
                        ty = self.player_y + (p_size - trail_h) * 0.50
                        particle_w = trail_w * (1.0 - trail_i * 0.055)
                        particle_h = trail_h * (1.0 - trail_i * 0.045)
                        if trail_name == "Rainbow":
                            palette = ((1, .2, .2, fade), (1, .65, .1, fade), (.2, .8, 1, fade))
                            Color(*palette[trail_i % len(palette)])
                        else:
                            Color(trail_color[0], trail_color[1], trail_color[2], trail_color[3] * fade)
                        if trail_name == "Spark":
                            Rectangle(pos=(tx, ty), size=(particle_w, particle_h))
                        else:
                            Ellipse(pos=(tx, ty), size=(particle_w, particle_h))
                # Lightweight player aura while airborne. It is drawn behind the
                # avatar and does not affect collision, controls, or movement.
                if quality != "Low" and not self.is_grounded:
                    pulse = .5 + .5*math.sin(self.animation_time*9.0)
                    aura_alpha = .08 + pulse*.07
                    Color(skin[0], skin[1], skin[2], aura_alpha)
                    Line(ellipse=(draw_x - cell*.10, draw_y - cell*.10,
                                  draw_w + cell*.20, draw_h + cell*.20),
                         width=max(1, cell*.045))
                # Low draws one plain square. Balanced/High keep the polished body.
                PushMatrix()
                Rotate(angle=self.player_angle, origin=(self.player_x + p_size/2, self.player_y + p_size/2))
                if quality == "Low":
                    Color(*skin)
                    Rectangle(pos=(draw_x, draw_y), size=(draw_w, draw_h))
                else:
                    Color(max(0, skin[0]*.48), max(0, skin[1]*.48), max(0, skin[2]*.48), 1)
                    Rectangle(pos=(draw_x-1.5, draw_y-1.5), size=(draw_w+3, draw_h+3))
                    Color(*skin)
                    Rectangle(pos=(draw_x, draw_y), size=(draw_w, draw_h))
                    Color(1, 1, 1, .24)
                    Rectangle(pos=(draw_x + draw_w*.10, draw_y + draw_h*.80), size=(draw_w*.80, max(1, draw_h*.08)))
                    Color(0, 0, 0, .10)
                    Rectangle(pos=(draw_x + draw_w*.08, draw_y + draw_h*.04),
                              size=(draw_w*.84, max(1, draw_h*.07)))
                PopMatrix()
                # Tiny speed pixels behind the square while running
                if quality != "Low" and moving and self.is_grounded:
                    Color(skin[0], skin[1], skin[2], .35)
                    trail_x = self.player_x - cell*.12 if self.player_vx > 0 else self.player_x + p_size
                    for trail_i in range(2):
                        Rectangle(pos=(trail_x, self.player_y + p_size*(.25 + trail_i*.25)),
                                  size=(cell*.10, max(1, cell*.045)))
                # Draw online players in blue; positions are normalized grid coordinates.
                remote_players = getattr(self.app_ref, "multiplayer_players", {})
                for remote_id, remote in list(remote_players.items()):
                    try:
                        rx = float(remote["x"])
                        ry = float(remote["y"])
                        if not (math.isfinite(rx) and math.isfinite(ry)):
                            continue
                        remote_x = self.x + rx * cell
                        remote_y = self.y + ry * cell
                        Color(0.16, 0.48, 1.0, 0.95)
                        Rectangle(pos=(remote_x, remote_y), size=(p_size, p_size))
                        remote_name = str(remote.get("name", "Player"))[:14]
                        name_key = ("remote", remote_name, max(10, int(cell * 0.32)))
                        name_texture = self._text_texture_cache.get(name_key)
                        if name_texture is None:
                            name_label = CoreLabel(text=remote_name, font_size=name_key[2], color=(0.75, 0.88, 1, 1))
                            name_label.refresh()
                            name_texture = name_label.texture
                            if name_texture is not None:
                                if len(self._text_texture_cache) >= 256:
                                    self._text_texture_cache.clear()
                                self._text_texture_cache[name_key] = name_texture
                        if name_texture is not None:
                            Color(0.75, 0.88, 1, 1)
                            Rectangle(texture=name_texture, pos=(remote_x, remote_y + p_size + 2), size=name_texture.size)
                    except (TypeError, ValueError, KeyError):
                        continue
        # Place the circular rotation ring around the selected object's centre.
        key = self.selected_key
        if editor and getattr(self.app_ref, "edit_tool", "select") == "rotate" and key is not None and key in self.grid_data:
            try:
                col, row = key[:2]
                cell = self.cell()
                # The object key is its top-left grid tile. Use the full object
                # dimensions so wide/tall objects keep the wheel centred on
                # their visual centre rather than on the anchor tile.
                tw, th = self._tile_dimensions(key, self.grid_data[key])
                object_w = max(1.0, float(tw)) * cell
                object_h = max(1.0, float(th)) * cell
                cx = self.x + (float(col) + float(tw) * 0.5) * cell
                cy = self.y + (float(row) + float(th) * 0.5) * cell
                # The ring must sit outside the entire rectangular object,
                # including its corners. RotationWheel's ring radius is 43%
                # of its widget diameter, so size it from the object's diagonal.
                object_diagonal = math.hypot(object_w, object_h)
                wheel_size = max(190.0, (object_diagonal + max(36.0, cell * 0.45)) / 0.86)
                self.rotation_wheel.size = (wheel_size, wheel_size)
                self.rotation_wheel.center = (cx, cy)
            except (TypeError, ValueError):
                self.rotation_wheel.center = self.center
            rotation = float(self.grid_data[key].get("rotation", 0)) % 360.0
            self.rotation_wheel.set_angle(rotation)
            self.rotation_wheel.opacity = 1
            self.rotation_wheel.angle_label.opacity = 1
            self.rotation_wheel.disabled = False
        else:
            self.rotation_wheel.opacity = 0
            self.rotation_wheel.angle_label.opacity = 0
            self.rotation_wheel.disabled = True

    def grid_cell_at(self, touch_pos):
        cell = self.cell()
        col = int((touch_pos[0] - self.x) // cell)
        row = int((touch_pos[1] - self.y) // cell)
        if 0 <= col < self.cols and 0 <= row < self.rows:
            return col, row
        return None

    def object_key_at(self, touch_pos):
        cell_pos = self.grid_cell_at(touch_pos)
        if cell_pos is None:
            return None
        col, row = cell_pos
        # Check top-most / most recently inserted objects first.
        for key, obj in reversed(tuple(self.grid_data.items())):
            tw, th = parse_tile_dimensions(obj["length"])
            if key[0] <= col < key[0] + tw and key[1] <= row < key[1] + th:
                return key
        return None

    def unique_object_key(self, col, row, exclude=None):
        """Return a unique key so multiple objects can share the same tile."""
        base = (int(col), int(row))
        if base not in self.grid_data or base == exclude:
            return base
        serial = 1
        while (base[0], base[1], serial) in self.grid_data:
            serial += 1
        return (base[0], base[1], serial)

    def _mark_grid_changed(self):
        """Invalidate cached render/physics indexes after an editor mutation."""
        self._runtime_index_dirty = True
        self._all_object_items = ()
        self._render_order_index = {}
        self._dimensions_by_key = {}
        self._solid_objects_cache = ()
        self._spatial_buckets = {}
        self._runtime_index_signature = None

    def handle_placement(self, touch_pos):
        cell_pos = self.grid_cell_at(touch_pos)
        if cell_pos is None:
            return
        col, row = cell_pos
        obj = self.app_ref.selected_object
        if not obj:
            return
        if obj.get("id") == -1:
            key = self.object_key_at(touch_pos)
            if key is not None:
                self.grid_data.pop(key, None)
                if self.selected_key == key:
                    self.selected_key = None
        else:
            object_id = int(obj.get("id", -1))
            # Hard per-level placement limits. Count existing objects before
            # placing, so editor taps cannot create unlimited reward objects.
            if object_id in (6, 7):
                limit = 10 if object_id == 6 else 5
                existing = sum(1 for value in self.grid_data.values()
                               if int(value.get("id", -1)) == object_id)
                if existing >= limit:
                    noun = "coins" if object_id == 6 else "gems"
                    self.app_ref.status_label.text = f"Level limit reached: maximum {limit} {noun}."
                    return
            new_key = self.unique_object_key(col, row)
            self.grid_data[new_key] = obj.copy()
            if self.grid_data[new_key].get("id") == 45:
                self.grid_data[new_key].setdefault("display_text", "Enter Your Text")
        self._mark_grid_changed()
        self.redraw()

    def editor_touch_down(self, touch):
        tool = self.app_ref.edit_tool
        key = self.object_key_at(touch.pos)
        cell_pos = self.grid_cell_at(touch.pos)
        if cell_pos is None:
            return False
        col, row = cell_pos
        if tool == "place":
            self.handle_placement(touch.pos)
        elif tool == "select":
            self.selected_key = key
            if key is not None:
                obj = self.grid_data[key]
                self.app_ref.status_label.text = f"Selected: {obj.get('name', 'Object')} at {key}"
            else:
                self.app_ref.status_label.text = "Selected: none"
            self.redraw()
        elif tool == "delete":
            if key is not None:
                self.grid_data.pop(key, None)
                self.selected_key = None
                self._mark_grid_changed()
                self.app_ref.status_label.text = "Object deleted"
                self.redraw()
        elif tool == "copy":
            if key is not None:
                obj = self.grid_data[key].copy()
                tw, _ = parse_tile_dimensions(obj["length"])
                new_col = min(self.cols - 1, key[0] + max(1, int(math.ceil(tw))))
                new_key = (new_col, key[1])
                if new_key == key:
                    new_key = (max(0, key[0] - 1), key[1])
                new_key = self.unique_object_key(new_key[0], new_key[1])
                self.grid_data[new_key] = obj
                self.selected_key = new_key
                self._mark_grid_changed()
                self.app_ref.status_label.text = f"Copied: {obj.get('name', 'Object')}"
                self.redraw()
        elif tool in ("move", "resize"):
            if key is not None:
                self.selected_key = key
                self.edit_touch_key = key
                self.edit_touch_start = (col, row)
                self.edit_touch_origin = key
                touch.grab(self)
                self.redraw()
            else:
                self.selected_key = None
                self.redraw()
        return True

    def on_touch_down(self, touch):
        if self.rotation_wheel.opacity and self.rotation_wheel.on_touch_down(touch):
            return True
        # Let the floating Show UI button receive taps before the editor canvas
        # interprets them as placing/selecting objects.
        show_btn = getattr(self.app_ref, "show_ui_btn", None)
        if self.app_ref.ui_hidden and show_btn is not None and show_btn.parent is self:
            if show_btn.collide_point(*touch.pos):
                return super().on_touch_down(touch)
        if not self.app_ref.is_playing and self.collide_point(*touch.pos):
            if self.editor_touch_down(touch):
                return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if not self.app_ref.is_playing and (touch.grab_current is self or self.collide_point(*touch.pos)):
            tool = self.app_ref.edit_tool
            cell_pos = self.grid_cell_at(touch.pos)
            if cell_pos is None:
                return True
            col, row = cell_pos
            if tool == "place":
                self.handle_placement(touch.pos)
            elif tool == "move" and self.edit_touch_key is not None:
                old_key = self.edit_touch_key
                obj = self.grid_data.pop(old_key, None)
                if obj is not None:
                    dx = col - self.edit_touch_start[0]
                    dy = row - self.edit_touch_start[1]
                    new_key = (max(0, min(self.cols-1, self.edit_touch_origin[0] + dx)), max(0, min(self.rows-1, self.edit_touch_origin[1] + dy)))
                    new_key = self.unique_object_key(new_key[0], new_key[1])
                    self.grid_data[new_key] = obj
                    self.edit_touch_key = new_key
                    self.selected_key = new_key
                    self._mark_grid_changed()
                    self.redraw()
            elif tool == "resize" and self.edit_touch_key is not None:
                key = self.edit_touch_key
                obj = self.grid_data.get(key)
                if obj:
                    width = max(0.2, min(float(self.cols-key[0]), col-key[0]+1.0))
                    height = max(0.2, min(float(self.rows-key[1]), row-key[1]+1.0))
                    obj["length"] = f"{width:g} Tiles W x {height:g} Tiles L"
                    self._mark_grid_changed()
                    self.redraw()
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            self.edit_touch_key = None
            self.edit_touch_start = None
            self.edit_touch_origin = None
            return True
        return super().on_touch_up(touch)

class ObjectCatalogPopup(Popup):
    """Searchable, categorized neon-styled object library for the level editor."""
    def __init__(self, app_ref, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app_ref
        self.title = "OBJECT LIBRARY"
        self.size_hint = (0.92, 0.90)
        self.auto_dismiss = True
        self.background = ""
        self.background_color = (0.018, 0.028, 0.065, 0.98)
        self.separator_color = app_ref._theme()["accent"]
        self._catalog_buttons = []
        self._category = "All"

        palette = app_ref._theme()
        content = BoxLayout(orientation="vertical", padding=12, spacing=10)
        with content.canvas.before:
            Color(0.018, 0.028, 0.065, 0.99)
            content._catalog_bg = Rectangle(pos=content.pos, size=content.size)
            Color(*palette["accent"][:3], 0.65)
            content._catalog_line = Line(points=[0, 0, 0, 0], width=1.2)
        content.bind(pos=lambda w, _v: setattr(w._catalog_bg, "pos", w.pos),
                     size=lambda w, _v: (setattr(w._catalog_bg, "size", w.size),
                                         setattr(w._catalog_line, "points", [w.x, w.y, w.right, w.y])))

        header = BoxLayout(size_hint_y=None, height=42, spacing=8)
        heading = Label(text="CHOOSE AN OBJECT", bold=True, font_size=20,
                        color=palette["text"], halign="left", valign="middle")
        heading.bind(size=lambda w, _v: setattr(w, "text_size", w.size))
        count = Label(text=f"{len(OBJECTS_DATA) + 1} ITEMS", size_hint_x=None, width=92,
                      font_size=13, bold=True, color=palette["accent"])
        header.add_widget(heading); header.add_widget(count)
        content.add_widget(header)

        self.search_input = TextInput(hint_text="Search objects by name or description...",
                                      multiline=False, size_hint_y=None, height=48,
                                      font_size=17, padding=(14, 12),
                                      background_normal="", background_active="",
                                      background_color=(0.055, 0.085, 0.15, 1),
                                      foreground_color=palette["text"],
                                      hint_text_color=(0.55, 0.66, 0.8, 1),
                                      cursor_color=palette["accent"])
        self.search_input.bind(text=lambda *_: self._refresh_items())
        content.add_widget(self.search_input)

        self.category_spinner = Spinner(text="All Categories",
            values=("All Categories", "Platforms", "Hazards", "Collectibles", "Zones", "Triggers", "Other"),
            size_hint_y=None, height=46, font_size=16,
            background_normal="", background_color=palette["panel"],
            color=palette["text"])
        self.category_spinner.bind(text=lambda _w, value: self._set_category(value))
        content.add_widget(self.category_spinner)

        self.scroll = ScrollView(do_scroll_x=False, bar_width=5, scroll_type=["bars", "content"])
        self.grid = GridLayout(cols=2, spacing=8, padding=(2, 4), size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter("height"))
        self.scroll.add_widget(self.grid)
        content.add_widget(self.scroll)

        footer = BoxLayout(size_hint_y=None, height=48, spacing=8)
        self.result_label = Label(text="Tap an item to select it", color=(0.62, 0.75, 0.9, 1),
                                  font_size=14, halign="left", valign="middle")
        self.result_label.bind(size=lambda w, _v: setattr(w, "text_size", w.size))
        close = Button(text="CLOSE", size_hint_x=None, width=112, bold=True, font_size=11,
                       halign="center", valign="middle", padding=(4, 2),
                       background_normal="", background_color=palette["secondary"],
                       color=palette["text"])
        close.bind(size=lambda w, _v: setattr(w, "text_size", (w.width - 8, w.height - 4)))
        close.bind(on_press=self.dismiss)
        footer.add_widget(self.result_label); footer.add_widget(close)
        content.add_widget(footer)
        self.content = content
        self._refresh_items()

    def _category_for(self, obj):
        oid = int(obj.get("id", -1))
        if oid == -1: return "Tools"
        if oid in (54, 55, 56, 57, 50, 46): return "Triggers"
        if oid in (2, 3, 15, 31, 47, 48, 49): return "Hazards"
        if oid in (6, 7, 8): return "Collectibles"
        if oid in (32, 33, 34, 35, 36, 37, 38, 41, 51, 52): return "Zones"
        if oid in (1, 4, 14, 20, 21, 26, 29, 39, 42, 44): return "Platforms"
        return "Other"

    def _set_category(self, value):
        self._category = "All" if value == "All Categories" else value
        self._refresh_items()

    def _refresh_items(self):
        if not hasattr(self, "grid"):
            return
        self.grid.clear_widgets()
        query = self.search_input.text.strip().lower()
        matches = []
        catalog_items = list(OBJECTS_DATA) + [{
            "id": -1, "name": "Erase", "shape": "TOOL", "color": "RED",
            "length": "Tool", "desc": "Remove placed objects from the level."
        }]
        for obj in catalog_items:
            category = self._category_for(obj)
            haystack = f"{obj.get('id','')} {obj.get('name','')} {obj.get('desc','')}".lower()
            if (self._category == "All" or category == self._category) and (not query or query in haystack):
                matches.append((obj, category))
        palette = self.app_ref._theme()
        for obj, category in matches:
            label = f"{int(obj.get('id', 0)):02d}  {obj.get('name', 'Object')}\n{category.upper()}  •  {obj.get('desc', '')}"
            btn = Button(text=label, font_size=14, bold=True, size_hint_y=None, height=72,
                         halign="left", valign="middle", padding=(12, 7),
                         background_normal="", background_down="",
                         background_color=(0.065, 0.10, 0.18, 1), color=palette["text"])
            btn.bind(size=lambda w, _v: setattr(w, "text_size", (w.width - 22, w.height - 10)))
            btn.bind(on_press=lambda _w, selected=obj: self.select_and_dismiss(selected))
            with btn.canvas.after:
                Color(*palette["accent"][:3], 0.65)
                btn._edge = Line(rounded_rectangle=(btn.x, btn.y, btn.width, btn.height, 9), width=1)
            btn.bind(pos=lambda w, _v: setattr(w._edge, "rounded_rectangle", (w.x, w.y, w.width, w.height, 9)),
                     size=lambda w, _v: setattr(w._edge, "rounded_rectangle", (w.x, w.y, w.width, w.height, 9)))
            self.grid.add_widget(btn)
        if not matches:
            self.grid.add_widget(Label(text="No objects found. Try another search.",
                color=palette["text"], size_hint_y=None, height=70))
        self.result_label.text = f"{len(matches)} OBJECTS FOUND  •  Tap to select"

    def select_and_dismiss(self, obj):
        self.app_ref.select_object(obj)
        self.dismiss()


class CommunityLevelThumbnail(Widget):
    """Small, offline-rendered preview of a community level's JSON grid."""
    def __init__(self, level_data=None, **kwargs):
        super().__init__(**kwargs)
        self.level_data = level_data or {}
        self.bind(pos=self.redraw_preview, size=self.redraw_preview)
        self.redraw_preview()

    def redraw_preview(self, *_):
        self.canvas.clear()
        data = self.level_data if isinstance(self.level_data, dict) else {}
        objects = data.get("objects", [])
        stages = data.get("stages")
        if (not isinstance(objects, list) or not objects) and isinstance(stages, list) and stages:
            stage = stages[0] if isinstance(stages[0], dict) else {}
            level = stage.get("level", stage)
            objects = level.get("objects", []) if isinstance(level, dict) else []
        if not isinstance(objects, list):
            objects = []
        cols = max(1, min(64, int(data.get("cols", 32) or 32)))
        rows = max(1, min(40, int(data.get("rows", 20) or 20)))
        cell_w = self.width / cols if cols else 1
        cell_h = self.height / rows if rows else 1
        color_by_id = {}
        for item in OBJECTS_DATA:
            name = str(item.get("color", "WHITE")).upper()
            colors = {
                "GREEN": (0.22, 0.95, 0.62, 1), "RED": (1, 0.2, 0.28, 1),
                "PURPLE": (0.72, 0.36, 1, 1), "YELLOW": (1, 0.82, 0.18, 1),
                "BLUE": (0.18, 0.55, 1, 1), "BROWN": (0.55, 0.34, 0.2, 1),
                "ORANGE": (1, 0.48, 0.12, 1), "PINK": (1, 0.28, 0.68, 1),
                "AQUA": (0.18, 0.9, 0.9, 1), "AQUA BLUE": (0.18, 0.75, 0.95, 1),
                "WHITE": (0.9, 0.95, 1, 1), "GRAY": (0.48, 0.55, 0.66, 1),
                "BLACK": (0.5, 0.6, 0.75, 1), "TRANSPARENT WHITE": (0.55, 0.65, 0.75, 0.7),
                "SURFACE-RED": (0.8, 0.22, 0.28, 1),
            }
            color_by_id[item.get("id")] = colors.get(name, (0.4, 0.8, 1, 1))
        with self.canvas:
            Color(0.025, 0.04, 0.085, 1)
            Rectangle(pos=self.pos, size=self.size)
            Color(0.12, 0.2, 0.3, 0.55)
            for c in range(cols + 1):
                x = self.x + c * cell_w
                Line(points=[x, self.y, x, self.top], width=0.35)
            for r in range(rows + 1):
                y = self.y + r * cell_h
                Line(points=[self.x, y, self.right, y], width=0.35)
            for entry in objects[:2500]:
                if not isinstance(entry, dict):
                    continue
                try:
                    c, r = int(entry.get("col", 0)), int(entry.get("row", 0))
                    obj = entry.get("object") or {}
                    if not (0 <= c < cols and 0 <= r < rows) or not isinstance(obj, dict):
                        continue
                    Color(*color_by_id.get(obj.get("id"), (0.35, 0.8, 1, 1)))
                    Rectangle(pos=(self.x + c * cell_w + 0.4, self.y + r * cell_h + 0.4),
                              size=(max(1, cell_w - 0.8), max(1, cell_h - 0.8)))
                except (TypeError, ValueError):
                    continue


ACHIEVEMENT_CATEGORIES = {
    "Beginner": [
        ("first_steps", "First Steps", "Start your platforming journey"),
        ("getting_started", "Getting Started", "Complete your first level"),
        ("warming_up", "Warming Up", "Finish 3 levels"),
        ("rookie_player", "Rookie Player", "Finish 5 different levels"),
        ("platformer_fan", "Platformer Fan", "Finish 10 levels"),
        ("dedicated_player", "Dedicated Player", "Finish 25 levels"),
        ("marathon_gamer", "Marathon Gamer", "Finish 50 levels"),
        ("regular_player", "Regular Player", "Finish 100 levels"),
        ("welcome_back", "Welcome Back", "Finish a level on a later play session"),
        ("never_give_up", "Never Give Up", "Finish a level after multiple attempts"),
    ],
    "Level Completion": [
        ("level_master_25", "Level Master", "Complete 25 different levels"),
        ("level_champion_50", "Level Champion", "Complete 50 different levels"),
        ("legendary_completionist_100", "Legendary Completionist", "Complete 100 different levels"),
        ("perfect_run", "Perfect Run", "Complete a level without dying"),
        ("untouchable", "Untouchable", "Complete 5 levels without dying"),
        ("speed_demon", "Speed Demon", "Beat a level's speed target"),
        ("lightning_fast", "Lightning Fast", "Beat 10 speed targets"),
        ("comeback_king", "Comeback King", "Complete a level after 10 failed attempts"),
        ("persistent", "Persistent", "Finish the same level 5 times"),
        ("stage_conqueror", "Stage Conqueror", "Complete a multi-stage level"),
    ],
    "Coins and Gems": [
        ("first_coin", "First Coin", "Collect your first level coin"),
        ("coin_collector", "Coin Collector", "Collect 100 unique level coins"),
        ("coin_hoarder", "Coin Hoarder", "Collect 500 unique level coins"),
        ("coin_millionaire", "Coin Millionaire", "Collect 1,000 unique level coins"),
        ("gem_finder", "Gem Finder", "Collect your first gem"),
        ("gem_hunter_25", "Gem Hunter", "Collect 25 gems"),
        ("gem_collector_100", "Gem Collector", "Collect 100 gems"),
        ("treasure_hunter", "Treasure Hunter", "Collect every coin in a level"),
        ("gem_perfectionist", "Gem Perfectionist", "Collect every gem in a level"),
        ("full_treasure", "Full Treasure", "Collect all coins and gems in 10 levels"),
    ],
    "Movement and Platforming": [
        ("jump_master", "Jump Master", "Jump 100 times"),
        ("high_jumper", "High Jumper", "Reach a high platform"),
        ("long_jumper", "Long Jumper", "Make a long jump"),
        ("airborne", "Airborne", "Stay in the air for 10 seconds"),
        ("double_trouble", "Double Trouble", "Use double jump 25 times"),
        ("edge_dancer", "Edge Dancer", "Land near a platform edge 10 times"),
        ("moving_target", "Moving Target", "Land on moving platforms 10 times"),
        ("platform_rider", "Platform Rider", "Ride moving platforms for 30 seconds"),
        ("gravity_breaker", "Gravity Breaker", "Use a gravity-changing mechanic"),
        ("wall_dodger", "Wall Dodger", "Avoid 20 hazards"),
    ],
    "Hazards and Survival": [
        ("close_call", "Close Call", "Survive a close hazard encounter"),
        ("spike_survivor", "Spike Survivor", "Complete a level containing spikes"),
        ("trap_dodger", "Trap Dodger", "Avoid 10 traps"),
        ("saw_survivor", "Saw Survivor", "Complete a level containing a saw"),
        ("fireball_escape", "Fireball Escape", "Dodge 10 fireballs"),
        ("fake_block_finder", "Fake Block Finder", "Discover a fake block"),
        ("one_way_wonder", "One-Way Wonder", "Land on one-way platforms 20 times"),
        ("checkpoint_saved", "Checkpoint Saved", "Use your first checkpoint"),
        ("checkpoint_champion", "Checkpoint Champion", "Use checkpoints 25 times"),
        ("survival_expert", "Survival Expert", "Finish 10 hazard levels without dying"),
    ],
    "Triggers and Special Mechanics": [
        ("trigger_happy", "Trigger Happy", "Activate your first trigger"),
        ("trigger_tester", "Trigger Tester", "Activate 50 triggers"),
        ("gravity_guru", "Gravity Guru", "Use gravity triggers 10 times"),
        ("invisible_journey", "Invisible Journey", "Finish a level using transparency triggers"),
        ("speed_control", "Speed Control", "Use a speed trigger"),
        ("teleport_traveler", "Teleport Traveler", "Teleport 10 times"),
        ("switch_operator", "Switch Operator", "Activate switches 25 times"),
        ("timer_expert", "Timer Expert", "Complete a timer-trigger challenge"),
        ("sound_explorer", "Sound Explorer", "Activate a sound trigger"),
        ("trigger_completionist", "Trigger Completionist", "Use 5 different trigger types"),
    ],
    "Editor and Building": [
        ("first_creation", "First Creation", "Save your first level"),
        ("builder_5", "Builder", "Save 5 levels"),
        ("architect_25", "Architect", "Save 25 levels"),
        ("master_architect_100", "Master Architect", "Save 100 levels"),
        ("object_collector", "Object Collector", "Place 25 objects in one level"),
        ("object_expert", "Object Expert", "Use 20 different object types"),
        ("trigger_architect", "Trigger Architect", "Place 10 triggers in one level"),
        ("stage_designer", "Stage Designer", "Create a level with 5 stages"),
        ("playtester", "Playtester", "Playtest your own level 10 times"),
        ("perfect_designer", "Perfect Designer", "Complete your own level without dying"),
    ],
    "Community and Online": [
        ("community_explorer", "Community Explorer", "Play a community level"),
        ("community_regular", "Community Regular", "Play 25 community levels"),
        ("community_champion", "Community Champion", "Play 100 community levels"),
        ("first_download", "First Download", "Download a community level"),
        ("level_supporter", "Level Supporter", "Like 10 community levels"),
        ("first_publication", "First Publication", "Publish your first level"),
        ("popular_creator", "Popular Creator", "Receive 10 likes on your levels"),
        ("community_star", "Community Star", "Receive 100 likes on your levels"),
        ("helpful_reporter", "Helpful Reporter", "Submit a valid community report"),
        ("rating_expert", "Rating Expert", "Rate 25 community levels"),
    ],
}

class LevelEditorApp(App):
    # Configure these with the values from Supabase Project Settings.
    # The publishable key is safe for client apps; never put a secret/service-role key here.
    SUPABASE_URL = "https://krzsljciejmzdpltnqeg.supabase.co"
    SUPABASE_PUBLISHABLE_KEY = "sb_publishable_3s52YcO1m3Jl0LDxXhFbpA_YRQ0Nu2k"

    def _api_headers(self, access_token=None, prefer=None):
        key = self.SUPABASE_PUBLISHABLE_KEY.strip()
        token = access_token or key
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        if prefer:
            headers["Prefer"] = prefer
        return headers

    def _api_request(self, method, path, payload=None, params=None, access_token=None, prefer=None):
        import requests
        if not self.SUPABASE_PUBLISHABLE_KEY or "PASTE_YOUR_" in self.SUPABASE_PUBLISHABLE_KEY:
            raise RuntimeError("Add your Supabase publishable key in the game file first.")
        url = self.SUPABASE_URL.rstrip("/") + path
        response = requests.request(
            method, url, headers=self._api_headers(access_token, prefer),
            json=payload, params=params, timeout=20
        )
        if response.status_code >= 400:
            try:
                detail = response.json()
            except Exception:
                detail = response.text[:300]
            raise RuntimeError(f"Supabase {response.status_code}: {detail}")
        if not response.text.strip():
            return []
        try:
            return response.json()
        except Exception:
            return []

    def _auth_request(self, endpoint, payload):
        return self._api_request("POST", "/auth/v1/" + endpoint, payload)

    def _session_file(self):
        # Private app storage persists across app restarts and Python file updates.
        folder = self.user_data_dir
        os.makedirs(folder, exist_ok=True)
        return os.path.join(folder, "supabase_session.json")

    def _save_auth_session(self, result):
        try:
            data = {
                "access_token": result.get("access_token"),
                "refresh_token": result.get("refresh_token"),
                "expires_at": result.get("expires_at"),
                "user": result.get("user") or self.current_user or {},
                "email": self.current_email,
                "username": self.current_username,
            }
            if data["refresh_token"]:
                with open(self._session_file(), "w", encoding="utf-8") as f:
                    json.dump(data, f)
        except Exception:
            pass

    def _clear_auth_session(self):
        try:
            path = self._session_file()
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass

    def _restore_auth_session(self):
        try:
            path = self._session_file()
            if not os.path.isfile(path):
                return
            with open(path, "r", encoding="utf-8") as f:
                saved = json.load(f)
            refresh_token = saved.get("refresh_token")
            if not refresh_token:
                return
            # Refresh at startup so expired access tokens are replaced safely.
            result = self._auth_request("token?grant_type=refresh_token", {"refresh_token": refresh_token})
            if not result.get("access_token"):
                self._clear_auth_session()
                return
            self.access_token = result.get("access_token")
            self.current_user = result.get("user") or saved.get("user") or {}
            self.current_email = (self.current_user.get("email") or saved.get("email") or "").strip()
            metadata = self.current_user.get("user_metadata") or {}
            self.current_username = metadata.get("username") or saved.get("username") or (self.current_email.split("@")[0] if self.current_email else "Guest")
            self._save_auth_session(result)
        except Exception:
            # If offline, keep the saved session data; user can retry when connected.
            try:
                with open(self._session_file(), "r", encoding="utf-8") as f:
                    saved = json.load(f)
                if saved.get("access_token") and saved.get("refresh_token"):
                    self.access_token = saved["access_token"]
                    self.current_user = saved.get("user") or {}
                    self.current_email = (saved.get("email") or self.current_user.get("email") or "").strip()
                    self.current_username = saved.get("username") or (self.current_email.split("@")[0] if self.current_email else "Guest")
            except Exception:
                pass

    def _initialize_unity_bridge(self, *_args):
        """Initialize the native Unity Ads bridge on Android."""
        try:
            from kivy.utils import platform
            if platform != "android":
                return
            from jnius import autoclass
            Activity = autoclass("org.kivy.android.PythonActivity")
            Bridge = autoclass("org.adnanzamangames.platformer.UnityAdsHelper")
            self._unity_bridge = Bridge
            Bridge.initialize(
                Activity.mActivity,
                UNITY_GAME_ID,
                UNITY_REWARDED_PLACEMENT_ID,
                UNITY_INTERSTITIAL_PLACEMENT_ID,
                UNITY_TEST_MODE,
            )
            if self._unity_poll_event is None:
                self._unity_poll_event = Clock.schedule_interval(self._poll_unity_events, 0.25)
        except Exception as exc:
            self._unity_bridge = None
            print("Unity Ads initialization failed:", repr(exc))

    def _poll_unity_events(self, _dt):
        """Poll native event codes; this avoids cross-thread Python callbacks."""
        bridge = self._unity_bridge
        if bridge is None:
            return
        try:
            if bridge.isReady():
                self._unity_ready = True
            event = int(bridge.consumeEvent())
        except Exception as exc:
            print("Unity Ads event polling failed:", repr(exc))
            return
        if event == 1:  # Reward earned: grant once, only after Unity Ads callback.
            popup = self._unity_pending_reward_popup
            bonus = self._unity_pending_bonus
            level_key = getattr(self, "_unity_pending_level_key", None)
            self._unity_pending_reward_popup = None
            self._unity_pending_bonus = 0
            self._unity_pending_level_key = None
            self._grant_rewarded_bonus(bonus, popup, level_key)
        elif event == 2:  # Closed without reward; leave reward choices available.
            if self._unity_pending_reward_popup is not None:
                self._show_notice("No reward earned", "Watch the rewarded ad until completion to receive the bonus coins.")
            self._unity_pending_reward_popup = None
            self._unity_pending_bonus = 0
            self._unity_pending_level_key = None
        elif event == 3:  # Rewarded ad unavailable/failed.
            self._unity_pending_reward_popup = None
            self._unity_pending_bonus = 0
            self._unity_pending_level_key = None
            self._show_notice("Ad unavailable", "The rewarded ad could not be shown. You can skip to the main menu.")
        elif event in (4, 5):  # Interstitial closed or failed; continue either way.
            self._unity_pending_interstitial = False
            self._after_level_reward_navigation(self._reward_was_community, self._reward_was_builtin)

    def on_start(self):
        Clock.schedule_once(self._initialize_unity_bridge, 1.0)

    def build(self):
        # Request landscape orientation on supported mobile platforms.
        try:
            from kivy.utils import platform
            if platform == "android":
                from jnius import autoclass
                Activity = autoclass("org.kivy.android.PythonActivity")
                Activity.mActivity.setRequestedOrientation(0)
        except Exception:
            pass
        self.selected_object = OBJECTS_DATA[0]
        self.is_playing = False
        self.stages = [{"name": "Stage 1", "objects": {}, "background": "Default"}]
        self.current_stage_index = 0
        self._play_stages_snapshot = None
        self._play_start_stage_index = 0
        # Runtime-only collectible state is keyed by stage index because grid
        # coordinates repeat between stages. elapsed_time and score remain run-wide.
        self._play_stage_collected = {}
        self._community_play_row = None
        self._community_play_mode = False
        self._builtin_play_mode = False
        self._builtin_editor_mode = False
        self.edit_tool = "place"
        self._reward_flow_active = False
        self._reward_bonus_claimed = False
        self._unity_bridge = None
        self._unity_ready = False
        self._unity_pending_reward_popup = None
        self._unity_pending_bonus = 0
        self._unity_pending_level_key = None
        self._unity_pending_interstitial = False
        self._unity_poll_event = None
        self.current_user = None
        self.access_token = None
        self.current_email = ""
        self.current_username = "Guest"
        self._restore_auth_session()
        self.settings = self._load_skin_preferences()
        self._apply_theme()
        self.root_layout = BoxLayout(orientation="vertical", padding=4, spacing=4)
        root = self.root_layout
        top = BoxLayout(size_hint_y=None, height=72, spacing=10, padding=(6, 5))
        self.top_bar_layout = top
        top.add_widget(Label(text="Level Editor", font_size=16, size_hint_x=None, width=115))
        self.status_label = Label(text=f"Brush: {self.selected_object['name']}", font_size=15)
        top.add_widget(self.status_label)
        self.play_btn = Button(text="Play", font_size=22, size_hint_x=None, width=124, background_color=(0.2, 0.8, 0.3, 1))
        self.play_btn.bind(on_press=self.toggle_play_mode)
        top.add_widget(self.play_btn)
        self.clear_btn = Button(text="Clear", font_size=22, size_hint_x=None, width=112, background_color=(0.8, 0.2, 0.2, 1))
        self.clear_btn.bind(on_press=self.clear_map)
        top.add_widget(self.clear_btn)
        self.hide_ui_btn = Button(text="Hide UI", font_size=21, size_hint_x=None, width=140, background_color=(0.45, 0.35, 0.7, 1))
        self.hide_ui_btn.bind(on_press=self.hide_ui)
        top.add_widget(self.hide_ui_btn)
        self.admin_editor_btn = Button(text="Admin", font_size=18, size_hint_x=None, width=100, background_color=(0.55, 0.25, 0.65, 1))
        self.admin_editor_btn.bind(on_press=self.open_admin_menu)
        # The Admin button is only attached to the UI for the signed-in owner.
        if (self.current_email or "").strip().lower() == "adnanzamanador@gmail.com" and self.access_token:
            top.add_widget(self.admin_editor_btn)
        self.exit_editor_btn = Button(text="Menu", font_size=20, size_hint_x=None, width=110, background_color=(0.75, 0.35, 0.2, 1))
        self.exit_editor_btn.bind(on_press=self.return_to_menu)
        top.add_widget(self.exit_editor_btn)
        for top_button in top.children:
            if isinstance(top_button, Button):
                top_button.font_size = max(21, top_button.font_size)
                top_button.bold = True
                top_button.background_normal = ""
                top_button.background_down = ""
                top_button.color = self._theme()["text"]
        self.play_btn.background_color = self._theme()["good"]
        self.clear_btn.background_color = (0.72, 0.18, 0.22, 1)
        self.hide_ui_btn.background_color = self._theme()["secondary"]
        self.exit_editor_btn.background_color = self._theme()["accent"]
        root.add_widget(top)
        self.editor_canvas = FullScreenGridCanvas(self)
        # The canvas is recreated whenever the editor opens. Reattach the
        # currently selected stage immediately so its objects are visible in
        # the editor (play mode already reloads this data independently).
        if self.stages and 0 <= self.current_stage_index < len(self.stages):
            self.editor_canvas.grid_data = self.stages[self.current_stage_index].get("objects", {})
        else:
            self.editor_canvas.grid_data = {}
        self.editor_canvas._runtime_index_dirty = True
        self.editor_canvas._render_stage_index = self.current_stage_index
        self.ui_hidden = False
        self.show_ui_btn = Button(text="Show UI", font_size=18, size_hint=(None, None), size=(132, 58), background_color=(0.15, 0.55, 0.85, 1))
        self.show_ui_btn.bind(on_press=self.show_ui)
        self.editor_canvas.bind(pos=self._position_show_ui_button, size=self._position_show_ui_button)
        self.bottom_bar_layout = BoxLayout(orientation="vertical", size_hint_y=None, height=226, spacing=10, padding=10)
        row1 = BoxLayout(spacing=6)
        row2 = BoxLayout(spacing=6)
        self.objects_btn = Button(text="Objects / Catalog", font_size=22, background_color=(0.2, 0.6, 0.86, 1))
        self.objects_btn.bind(on_press=self.open_objects_popup)
        row1.add_widget(self.objects_btn)
        for label, tool in (("Place", "place"), ("Select", "select"), ("Move", "move"), ("Copy", "copy"), ("Erase", "delete")):
            btn = Button(text=label, font_size=24, background_normal="", background_down="", background_color=self._theme()["panel"], color=self._theme()["text"])
            btn.bind(on_press=lambda instance, t=tool: self.set_edit_tool(t))
            row1.add_widget(btn)
        for label, tool in (("Resize", "resize"),):
            btn = Button(text=label, font_size=24, background_normal="", background_down="", background_color=self._theme()["panel"], color=self._theme()["text"])
            btn.bind(on_press=lambda instance, t=tool: self.set_edit_tool(t))
            row2.add_widget(btn)
        self.stages_btn = Button(text="Stages", font_size=22, background_color=(0.15, 0.58, 0.62, 1))
        self.stages_btn.bind(on_press=self.open_stages_popup)
        row2.add_widget(self.stages_btn)
        self.background_btn = Button(text="BG", font_size=20, background_color=self._theme()["panel"])
        self.background_btn.bind(on_press=self.open_background_popup)
        row2.add_widget(self.background_btn)
        self.rotate_btn = Button(text="Rotate", font_size=20, background_color=(0.55, 0.38, 0.75, 1))
        self.rotate_btn.bind(on_press=self.rotate_selected_object)
        row2.add_widget(self.rotate_btn)
        self.properties_btn = Button(text="Props", font_size=22, background_color=(0.3, 0.5, 0.7, 1))
        self.properties_btn.bind(on_press=self.open_properties_popup)
        row2.add_widget(self.properties_btn)
        self.save_btn = Button(text="Save", font_size=22, background_color=(0.2, 0.6, 0.3, 1))
        self.save_btn.bind(on_press=self.open_save_popup)
        row2.add_widget(self.save_btn)
        self.load_btn = Button(text="Load", font_size=22, background_color=(0.5, 0.4, 0.8, 1))
        self.load_btn.bind(on_press=self.open_load_popup)
        row2.add_widget(self.load_btn)
        self.upload_btn = Button(text="Upload", font_size=24, background_color=self._theme()["accent"])
        self.upload_btn.bind(on_press=self.upload_from_editor)
        row2.add_widget(self.upload_btn)
        # Give all editor tool buttons a consistent, larger touch-friendly design.
        for tool_row in (row1, row2):
            for tool_button in tool_row.children:
                if isinstance(tool_button, Button):
                    tool_button.font_size = max(23, tool_button.font_size)
                    tool_button.bold = True
                    tool_button.background_normal = ""
                    tool_button.background_down = ""
                    tool_button.background_color = self._theme()["panel"]
                    tool_button.color = self._theme()["text"]
        self.objects_btn.background_color = self._theme()["accent"]
        self.stages_btn.background_color = self._theme()["secondary"]
        self.save_btn.background_color = self._theme()["good"]
        self.load_btn.background_color = self._theme()["secondary"]
        self.upload_btn.background_color = self._theme()["accent"]
        self.bottom_bar_layout.add_widget(row1)
        self.bottom_bar_layout.add_widget(row2)
        root.add_widget(self.bottom_bar_layout)
        root.add_widget(self.editor_canvas)
        # Redraw after the layout has assigned the canvas its final viewport size.
        Clock.schedule_once(lambda _dt: self.editor_canvas.redraw(), 0)
        # 60 Hz gameplay/physics tick for smoother input and movement.
        Clock.schedule_interval(self.editor_canvas.update_physics, 1 / 60)
        # Multiplayer room state (online relay server URL is configurable on the Multiplayer screen).
        self.multiplayer_server_url = "wss://platformer-multiplayer-server.onrender.com/ws"
        self.multiplayer_room_code = ""
        self.multiplayer_mode = "race"
        self.multiplayer_socket = None
        self.multiplayer_listener_thread = None
        self.multiplayer_status = "Not connected"
        self.multiplayer_last_message = ""
        self.multiplayer_player_id = None
        self.multiplayer_players = {}
        self.multiplayer_send_lock = __import__("threading").Lock()
        self.multiplayer_send_elapsed = 0.0
        self.multiplayer_room_ready = False
        self.multiplayer_manual_disconnect = False
        self.multiplayer_selected_level = None
        self.main_root = BoxLayout(orientation="vertical", padding=18, spacing=10)
        self.show_main_menu()
        # Show the welcome guide once on the first launch, then remember dismissal.
        if not self.settings.get("welcome_seen", False):
            Clock.schedule_once(self.show_first_launch_guide, 0.5)
        return self.main_root

    def show_first_launch_guide(self, *_):
        if self.settings.get("welcome_seen", False):
            return
        content = BoxLayout(orientation="vertical", padding=18, spacing=12)
        guide_text = (
            "Welcome to 2D Platformer!\n\n"
            "• Play Built-in / Local Levels: choose a level and play.\n"
            "• Level Editor: build your own levels. Choose an object, then tap the grid to place it. "
            "Use Select, Move, Copy, Resize, Rotate and Props to edit objects. Save stores your level; Load opens a saved level.\n"
            "• Online Community: browse and play levels shared by other players. Internet is needed for online features.\n"
            "• Leaderboards: compare scores and level completions.\n"
            "• Achievements & Progress: check your goals and progress.\n"
            "• Settings: change the menu theme, sound, sign in or register, and save/load your levels and progress to the cloud.\n\n"
            "Tip: save your edited levels regularly. Have fun!"
        )
        guide = Label(text=guide_text, font_size=17, color=self._theme()["text"],
                      halign="left", valign="top", size_hint_y=None)
        guide.bind(width=lambda inst, width: setattr(inst, "text_size", (width - 12, None)),
                   texture_size=lambda inst, size: setattr(inst, "height", size[1]))
        scroll = ScrollView(do_scroll_x=False, bar_width=8)
        scroll.add_widget(guide)
        content.add_widget(scroll)
        ok_btn = Button(text="OK, LET'S PLAY", size_hint_y=None, height=58, font_size=21,
                        bold=True, background_normal="", background_down="",
                        background_color=self._theme()["accent"], color=self._theme()["text"])
        popup = Popup(title="Welcome to 2D Platformer", content=content,
                      size_hint=(0.92, 0.88), auto_dismiss=False)
        def dismiss_guide(*_):
            self.settings["welcome_seen"] = True
            self._save_skin_preferences()
            popup.dismiss()
        ok_btn.bind(on_release=dismiss_guide)
        content.add_widget(ok_btn)
        popup.open()

    def _replace_screen(self, widget):
        """Fade the current page out, then fade the next page in."""
        if not hasattr(self, "_screen_transition_id"):
            self._screen_transition_id = 0
        self._screen_transition_id += 1
        transition_id = self._screen_transition_id

        old_widgets = list(self.main_root.children)
        if not old_widgets:
            self.main_root.clear_widgets()
            self.main_root.add_widget(widget)
            widget.opacity = 0
            Animation(opacity=1, duration=0.24, t="out_quad").start(widget)
            return

        # Prevent overlapping navigation animations from leaving a blank screen.
        for old_widget in old_widgets:
            Animation.cancel_all(old_widget, "opacity")

        def finish_switch(*_):
            if transition_id != self._screen_transition_id:
                return
            self.main_root.clear_widgets()
            widget.opacity = 0
            self.main_root.add_widget(widget)
            Animation(opacity=1, duration=0.25, t="out_quad").start(widget)

        fade_out = Animation(opacity=0, duration=0.13, t="in_quad")
        fade_out.bind(on_complete=finish_switch)
        for old_widget in old_widgets:
            fade_out.start(old_widget)

    def _theme(self):
        name = getattr(self, "settings", {}).get("theme", "Midnight")
        return THEMES.get(name, THEMES["Midnight"])

    def _apply_theme(self):
        palette = self._theme()
        Window.clearcolor = palette["bg"]
        canvas = getattr(self, "editor_canvas", None)
        if canvas is not None and canvas.get_parent_window() is not None:
            Clock.schedule_once(lambda _dt, target=canvas: target.redraw(), 0)

    def cycle_theme(self, *_):
        names = list(THEMES)
        current = self.settings.get("theme", "Midnight")
        self.settings["theme"] = names[(names.index(current) + 1) % len(names)] if current in names else names[0]
        self._save_skin_preferences()
        self._apply_theme()
        self.open_settings()

    def _menu_button(self, text, callback):
        palette = self._theme()
        btn = Button(text=text, font_size=27, bold=True, size_hint_y=None, height=88,
                     background_normal="", background_down="",
                     background_color=palette["panel"], color=palette["text"],
                     padding=(18, 10), halign="center", valign="middle")
        # Rounded-feeling clean panel with a crisp theme-colored outline.
        with btn.canvas.after:
            Color(*palette["accent"][:3], 0.95)
            btn._theme_border = Line(rounded_rectangle=(btn.x, btn.y, btn.width, btn.height, 10), width=1.5)
        def _sync_border(widget, _value):
            widget._theme_border.rounded_rectangle = (widget.x, widget.y, widget.width, widget.height, 10)
        btn.bind(pos=_sync_border, size=_sync_border)
        def _press_feedback(widget, *_):
            Animation.cancel_all(widget, "opacity")
            (Animation(opacity=0.78, duration=0.06) + Animation(opacity=1.0, duration=0.16)).start(widget)
        btn.bind(on_press=_press_feedback)
        btn.bind(on_press=callback)
        return btn

    def show_main_menu(self, *_):
        # Scrollable full-height menu prevents controls being pushed off-screen
        # on short landscape phones, while using larger touch targets.
        page = BoxLayout(orientation="vertical", padding=(28, 20), spacing=16)
        palette = self._theme()
        with page.canvas.before:
            Color(*palette["bg"])
            page._menu_bg = Rectangle(pos=(page.x, page.y), size=(page.width, page.height))
            # Subtle neon arcade atmosphere: distant glow rings and a perspective grid.
            Color(*palette["accent"][:3], 0.10)
            page._glow_one = Ellipse(pos=(page.x + page.width * 0.68, page.y + page.height * 0.58),
                                     size=(page.width * 0.38, page.width * 0.38))
            Color(*palette["secondary"][:3], 0.09)
            page._glow_two = Ellipse(pos=(page.x - page.width * 0.16, page.y - page.height * 0.15),
                                     size=(page.width * 0.42, page.width * 0.42))
            Color(*palette["accent"][:3], 0.13)
            page._grid_lines = []
            for index in range(1, 13):
                line = Line(points=[page.x, page.y + index * 34, page.right, page.y + index * 34], width=0.55)
                page._grid_lines.append(line)
            for index in range(1, 18):
                line = Line(points=[page.x + index * 58, page.y, page.x + index * 58, page.top], width=0.45)
                page._grid_lines.append(line)
            Color(*palette["accent"][:3], 0.45)
            page._top_edge = Line(points=[page.x, page.top - 2, page.right, page.top - 2], width=1.1)
        def sync_menu_backdrop(widget, _value):
            widget._menu_bg.pos = (widget.x, widget.y); widget._menu_bg.size = (widget.width, widget.height)
            widget._glow_one.pos = (widget.x + widget.width * 0.68, widget.y + widget.height * 0.58)
            widget._glow_one.size = (widget.width * 0.38, widget.width * 0.38)
            widget._glow_two.pos = (widget.x - widget.width * 0.16, widget.y - widget.height * 0.15)
            widget._glow_two.size = (widget.width * 0.42, widget.width * 0.42)
            for index, line in enumerate(widget._grid_lines[:12]):
                y = widget.y + (index + 1) * widget.height / 14.0
                line.points = [widget.x, y, widget.right, y]
            for index, line in enumerate(widget._grid_lines[12:]):
                x = widget.x + (index + 1) * widget.width / 19.0
                line.points = [x, widget.y, x, widget.top]
            widget._top_edge.points = [widget.x, widget.top - 2, widget.right, widget.top - 2]
        page.bind(pos=sync_menu_backdrop, size=sync_menu_backdrop)
        title = Label(text="BLOCKY PLATFORMER", font_size=46, bold=True, color=palette["text"],
                      size_hint_y=None, height=82)
        page.add_widget(title)
        title_pulse = Animation(font_size=49, duration=1.0) + Animation(font_size=46, duration=1.0)
        title_pulse.repeat = True
        title_pulse.start(title)
        page.add_widget(Label(text="ADNANZAMANGAMES  •  BUILD YOUR WORLD",
                              font_size=13, bold=True, color=palette["accent"],
                              size_hint_y=None, height=24))
        page.add_widget(Label(text=f"Player: {self.current_username}", font_size=22,
                              size_hint_y=None, height=42))
        wallet = self._load_progress_data()
        page.add_widget(Label(text=f"COINS: {int(wallet.get('currency_balance', 0))}",
                              font_size=27, bold=True, color=NEON_GREEN,
                              size_hint_y=None, height=52))
        scroll = ScrollView(do_scroll_x=False, bar_width=8)
        menu_items = BoxLayout(orientation="vertical", padding=(6, 6), spacing=14,
                               size_hint_y=None)
        menu_items.bind(minimum_height=menu_items.setter("height"))
        menu_items.add_widget(self._menu_button("Play Built-in / Local Levels", self.open_level_menu))
        # Multiplayer is an admin-only feature for now. Do not show it to regular players or guests.
        if self._admin_allowed():
            menu_items.add_widget(self._menu_button("MULTI-PLAYER — Create / Join Room", self.open_multiplayer_menu))
        menu_items.add_widget(self._menu_button("Level Editor", self.open_normal_editor))
        menu_items.add_widget(self._menu_button("Online Community", self.open_community))
        menu_items.add_widget(self._menu_button("Online Leaderboards", self.open_leaderboards))
        menu_items.add_widget(self._menu_button("Completed Levels & Orbs Leaderboards", self.open_completion_leaderboards))
        menu_items.add_widget(self._menu_button("Achievements & Progress", self.open_achievements))
        menu_items.add_widget(self._menu_button("Cosmetics", self.open_skins))
        menu_items.add_widget(self._menu_button("Settings", self.open_settings))
        scroll.add_widget(menu_items)
        page.add_widget(scroll)
        self._replace_screen(page)

    def open_multiplayer_menu(self, *_):
        # Large, spaced, scrollable multiplayer UI for Android phones.
        page = BoxLayout(orientation="vertical", padding=(16, 12), spacing=10)
        scroll = ScrollView(do_scroll_x=False, bar_width=8, scroll_type=["bars", "content"])
        content = BoxLayout(orientation="vertical", padding=(8, 10), spacing=16,
                            size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(Label(text="ONLINE MULTIPLAYER", font_size=32, bold=True,
                                 size_hint_y=None, height=62, halign="center", valign="middle"))
        intro = Label(text="Create a room or enter your friend's room code.", font_size=20,
                      size_hint_y=None, height=54, halign="center", valign="middle",
                      text_size=(Window.width - 64, None))
        content.add_widget(intro)

        content.add_widget(Label(text="SERVER WEBSOCKET URL", font_size=19, bold=True,
                                 size_hint_y=None, height=34, halign="left", valign="middle"))
        server_input = TextInput(text=self.multiplayer_server_url, multiline=False,
                                 size_hint_y=None, height=64, font_size=19,
                                 padding=(14, 18), write_tab=False,
                                 hint_text="wss://your-server.onrender.com/ws")
        content.add_widget(server_input)
        server_help = Label(text="Paste your deployed server address ending in /ws.",
                            font_size=16, size_hint_y=None, height=42,
                            halign="left", valign="middle", text_size=(Window.width - 64, None))
        content.add_widget(server_help)

        content.add_widget(Label(text="ROOM CODE", font_size=19, bold=True,
                                 size_hint_y=None, height=34, halign="left", valign="middle"))
        # Do not uppercase through input_filter: Kivy calls input_filter with
        # (substring, from_undo), so treating the second argument as text can
        # crash the Android app while typing or pasting. Normalize on JOIN instead.
        room_input = TextInput(text=self.multiplayer_room_code, multiline=False,
                               size_hint_y=None, height=64, font_size=24,
                               padding=(14, 18), hint_text="e.g. ABC123")
        content.add_widget(room_input)

        content.add_widget(Label(text="GAME MODE", font_size=19, bold=True,
                                 size_hint_y=None, height=34, halign="left", valign="middle"))
        mode_spinner = Spinner(text=self.multiplayer_mode.upper(), values=("RACE", "CO-OP", "PVP"),
                               size_hint_y=None, height=60, font_size=21)
        content.add_widget(mode_spinner)

        status = Label(text=self.multiplayer_status or "Not connected", font_size=18,
                       size_hint_y=None, height=82, halign="center", valign="middle",
                       text_size=(Window.width - 64, None))
        content.add_widget(status)

        def connect_room(code=None, create=False):
            self.multiplayer_server_url = server_input.text.strip()
            self.multiplayer_mode = mode_spinner.text.lower().replace("-", "")
            if not self.multiplayer_server_url.startswith(("ws://", "wss://")) or not self.multiplayer_server_url.endswith("/ws"):
                status.text = "Enter your deployed WebSocket URL ending in /ws."
                return
            room_code = (code if code is not None else room_input.text).strip().upper()
            if not create and not room_code:
                status.text = "Enter your friend's room code first."
                return
            if getattr(self, "multiplayer_socket", None) is not None:
                status.text = "Disconnect first before connecting to another room."
                return
            status.text = "Connecting to multiplayer server..."
            server_url = self.multiplayer_server_url
            player_name = str(self.current_username or "Player")[:24]
            action = "create_room" if create else "join_room"
            self.multiplayer_status = "Connecting..."
            self.multiplayer_players = {}
            self.multiplayer_room_ready = False

            self.multiplayer_manual_disconnect = False

            def worker():
                import threading
                import time
                import websocket
                first_action = action
                current_code = room_code
                attempt = 0
                while not getattr(self, "multiplayer_manual_disconnect", False):
                    sock = None
                    joined = False
                    try:
                        attempt += 1
                        if attempt == 1:
                            Clock.schedule_once(lambda _dt: setattr(status, "text", "Connecting to multiplayer server..."), 0)
                        else:
                            Clock.schedule_once(lambda _dt, n=attempt: setattr(status, "text", f"Reconnecting (attempt {n})..."), 0)
                        sock = websocket.create_connection(server_url, timeout=15)
                        sock.settimeout(25)
                        with self.multiplayer_send_lock:
                            if self.multiplayer_manual_disconnect:
                                sock.close()
                                break
                            self.multiplayer_socket = sock
                            request = {"action": first_action, "player_name": player_name}
                            if first_action == "join_room":
                                request["room_code"] = current_code
                            sock.send(json.dumps(request))
                        last_seen = time.time()
                        while not getattr(self, "multiplayer_manual_disconnect", False):
                            try:
                                raw = sock.recv()
                            except websocket.WebSocketTimeoutException:
                                # WebSocket timeout is a health check. Send a ping so
                                # mobile/network idle timeouts do not silently kill the room.
                                with self.multiplayer_send_lock:
                                    if self.multiplayer_socket is sock:
                                        sock.ping("keepalive")
                                continue
                            if not raw:
                                raise ConnectionError("Server closed the connection")
                            last_seen = time.time()
                            self.multiplayer_last_message = raw
                            try:
                                message = json.loads(raw)
                            except Exception:
                                continue
                            kind = message.get("type")
                            if kind == "room_joined":
                                joined = True
                                self.multiplayer_player_id = message.get("player_id")
                                current_code = str(message.get("room_code", current_code)).upper()
                                self.multiplayer_room_code = current_code
                                self.multiplayer_room_ready = True
                                self.multiplayer_status = "Connected"
                                self.multiplayer_selected_level = message.get("selected_level")
                                self.multiplayer_players = {
                                    pl.get("id"): {"name": pl.get("name", "Player"), **(pl.get("state") or {})}
                                    for pl in message.get("players", [])
                                    if pl.get("id") and pl.get("id") != self.multiplayer_player_id
                                }
                                # Reconnects must join the existing room, never create a new one.
                                first_action = "join_room"
                                code_text = current_code
                                Clock.schedule_once(lambda _dt, c=code_text: setattr(room_input, "text", c), 0)
                                Clock.schedule_once(lambda _dt, c=code_text: setattr(status, "text", "CONNECTED — ROOM CODE: " + c), 0)
                                if self.multiplayer_selected_level:
                                    level = self.multiplayer_selected_level
                                    Clock.schedule_once(lambda _dt, lv=level: self._load_multiplayer_level(lv), 0)
                            elif kind == "state":
                                pid = message.get("player_id")
                                if pid and pid != self.multiplayer_player_id:
                                    state = message.get("data") or {}
                                    self.multiplayer_players[pid] = {"name": state.get("name", "Player"), **state}
                                    Clock.schedule_once(lambda _dt: self.editor_canvas.redraw(), 0)
                            elif kind == "player_joined":
                                pid = message.get("player_id")
                                if pid and pid != self.multiplayer_player_id:
                                    self.multiplayer_players.setdefault(pid, {"name": message.get("player_name", "Player")})
                                    Clock.schedule_once(lambda _dt: self.editor_canvas.redraw(), 0)
                            elif kind == "player_left":
                                self.multiplayer_players.pop(message.get("player_id"), None)
                                Clock.schedule_once(lambda _dt: self.editor_canvas.redraw(), 0)
                            elif kind == "players":
                                for pl in message.get("players", []):
                                    pid = pl.get("id")
                                    if pid and pid != self.multiplayer_player_id:
                                        self.multiplayer_players[pid] = {"name": pl.get("name", "Player"), **(pl.get("state") or {})}
                                Clock.schedule_once(lambda _dt: self.editor_canvas.redraw(), 0)
                            elif kind in ("room_level_selected", "select_level"):
                                level = message.get("level")
                                if level:
                                    self.multiplayer_selected_level = level
                                    Clock.schedule_once(lambda _dt, lv=level: self._load_multiplayer_level(lv), 0)
                            elif kind == "ping":
                                try:
                                    with self.multiplayer_send_lock:
                                        if self.multiplayer_socket is sock:
                                            sock.send(json.dumps({"type": "pong"}))
                                except Exception:
                                    raise
                            elif kind == "error":
                                err = str(message.get("message", "Server error"))[:140]
                                Clock.schedule_once(lambda _dt, e=err: setattr(status, "text", "Server: " + e), 0)
                                # A failed room join cannot be fixed by retrying the same code forever.
                                if not joined and first_action == "join_room":
                                    raise RuntimeError("Room join failed: " + err)
                        if getattr(self, "multiplayer_manual_disconnect", False):
                            break
                        raise ConnectionError("Connection interrupted")
                    except Exception as exc:
                        if getattr(self, "multiplayer_manual_disconnect", False):
                            break
                        # If creation failed before a room code was received, retry the
                        # original create request once; otherwise reconnect to the same room.
                        if not current_code and first_action == "create_room":
                            first_action = "create_room"
                        elif current_code:
                            first_action = "join_room"
                        err = str(exc)[:100]
                        Clock.schedule_once(lambda _dt, e=err: setattr(status, "text", "Connection lost; retrying: " + e), 0)
                        time.sleep(min(8, 2 + attempt))
                    finally:
                        if sock is not None:
                            try:
                                sock.close()
                            except Exception:
                                pass
                        if self.multiplayer_socket is sock:
                            self.multiplayer_socket = None
                        if not getattr(self, "multiplayer_manual_disconnect", False):
                            self.multiplayer_room_ready = False
                self.multiplayer_room_ready = False
                if self.multiplayer_socket is not None:
                    self.multiplayer_socket = None
                self.multiplayer_status = "Disconnected"
                Clock.schedule_once(lambda _dt: setattr(status, "text", "Disconnected."), 0)
                Clock.schedule_once(lambda _dt: self.editor_canvas.redraw(), 0)

            self.multiplayer_listener_thread = __import__("threading").Thread(target=worker, daemon=True)
            self.multiplayer_listener_thread.start()

        def create_room(*_):
            connect_room(create=True)

        def join_room(*_):
            connect_room(room_input.text, create=False)

        actions = BoxLayout(orientation="vertical", size_hint_y=None, height=148, spacing=12)
        create_btn = self._menu_button("CREATE ROOM", create_room)
        create_btn.height = 66
        join_btn = self._menu_button("JOIN ROOM", join_room)
        join_btn.height = 66
        actions.add_widget(create_btn)
        actions.add_widget(join_btn)
        content.add_widget(actions)

        # Room connection and gameplay are separate steps: expose a clear action
        # that actually opens the level and switches the editor canvas into player mode.
        def enter_multiplayer_game(*_):
            if not getattr(self, "multiplayer_room_ready", False):
                status.text = "Connect to a room first, then enter the level."
                return
            try:
                if getattr(self, "multiplayer_selected_level", None):
                    self._load_multiplayer_level(self.multiplayer_selected_level)
                self.open_editor()
                if not self.is_playing:
                    self.toggle_play_mode()
                self.status_label.text = "MULTIPLAYER — " + str(self.multiplayer_room_code or "ROOM")
            except Exception as exc:
                status.text = "Could not enter level: " + str(exc)[:120]

        play_btn = self._menu_button("ENTER LEVEL / PLAY", enter_multiplayer_game)
        play_btn.height = 70
        content.add_widget(play_btn)

        disconnect_btn = self._menu_button("DISCONNECT", self.disconnect_multiplayer)
        disconnect_btn.height = 66
        content.add_widget(disconnect_btn)
        back_btn = self._menu_button("BACK TO MENU", self.show_main_menu)
        back_btn.height = 66
        content.add_widget(back_btn)

        scroll.add_widget(content)
        page.add_widget(scroll)
        self._replace_screen(page)

    def _load_multiplayer_level(self, level):
        """Load a room-selected community level into the normal playable editor."""
        if not isinstance(level, dict):
            return False
        payload = level.get("level_data") or level.get("data") or {}
        if isinstance(payload, dict) and not isinstance(payload.get("objects"), list):
            stage_list = payload.get("stages")
            if isinstance(stage_list, list) and stage_list:
                first_stage = stage_list[0]
                if isinstance(first_stage, dict):
                    if isinstance(first_stage.get("objects"), dict):
                        payload = {**payload, "objects": [
                            {"col": int(k[0]), "row": int(k[1]), "object": v}
                            for k, v in first_stage["objects"].items()
                            if isinstance(k, (tuple, list)) and len(k) >= 2 and isinstance(v, dict)
                        ]}
                    elif isinstance(first_stage.get("objects"), list):
                        payload = {**payload, "objects": first_stage["objects"]}
        objects = payload.get("objects", []) if isinstance(payload, dict) else []
        if not isinstance(objects, list):
            return False
        grid = {}
        for item in objects:
            if not isinstance(item, dict):
                continue
            try:
                col, row = int(item.get("col", 0)), int(item.get("row", 0))
            except (TypeError, ValueError):
                continue
            obj = item.get("object", item.get("obj"))
            if isinstance(obj, dict):
                grid[(col, row)] = copy.deepcopy(obj)
        if not grid:
            return False
        level_name = str(level.get("name") or "Multiplayer Level")[:60]
        self._builtin_editor_mode = False
        self._builtin_play_mode = False
        self.stages = [{"name": level_name, "objects": grid, "background": "Default"}]
        self.current_stage_index = 0
        self.editor_canvas.grid_data = copy.deepcopy(grid)
        self.editor_canvas.selected_key = None
        self.editor_canvas.redraw()
        self.multiplayer_selected_level = level
        return True

    def send_multiplayer_state(self, *_):
        """Send the local player's position in grid coordinates to the room."""
        sock = getattr(self, "multiplayer_socket", None)
        if sock is None or not getattr(self, "multiplayer_room_ready", False):
            return
        canvas = getattr(self, "editor_canvas", None)
        if canvas is None or not getattr(self, "is_playing", False):
            return
        cell = max(1.0, float(canvas.cell()))
        data = {
            "x": round((float(canvas.player_x) - float(canvas.x)) / cell, 4),
            "y": round((float(canvas.player_y) - float(canvas.y)) / cell, 4),
            "angle": float(getattr(canvas, "player_angle", 0.0)),
            "skin": str(getattr(self, "settings", {}).get("skin", "Green")),
            "name": str(getattr(self, "current_username", "Player") or "Player")[:24],
        }
        try:
            with self.multiplayer_send_lock:
                if self.multiplayer_socket is sock and self.multiplayer_room_ready:
                    sock.send(json.dumps({"type": "state", "data": data}))
        except Exception:
            pass

    def disconnect_multiplayer(self, *_):
        self.multiplayer_manual_disconnect = True
        sock = getattr(self, "multiplayer_socket", None)
        self.multiplayer_room_ready = False
        self.multiplayer_socket = None
        self.multiplayer_player_id = None
        self.multiplayer_players = {}
        if sock is not None:
            try:
                with self.multiplayer_send_lock:
                    sock.send(json.dumps({"type": "leave"}))
            except Exception:
                pass
            try:
                sock.close()
            except Exception:
                pass
        self.multiplayer_status = "Disconnected"
        try:
            self.editor_canvas.redraw()
        except Exception:
            pass
        self.open_multiplayer_menu()

    LEADERBOARD_FUNCTION = "/functions/v1/platformer-leaderboard"

    def _leaderboard_request(self, payload):
        """Call the Edge Function; never write leaderboard rows directly from the client."""
        import requests
        if not self.SUPABASE_URL or not self.SUPABASE_PUBLISHABLE_KEY:
            raise RuntimeError("Supabase is not configured.")
        token = getattr(self, "access_token", None)
        # The function's gateway JWT check must be disabled in Supabase config
        # because the function validates real user access tokens itself. For public
        # list requests, do not send the publishable key as a fake Bearer JWT.
        headers = {
            "apikey": self.SUPABASE_PUBLISHABLE_KEY.strip(),
            "Content-Type": "application/json",
        }
        if token:
            headers["Authorization"] = "Bearer " + token
        response = requests.post(self.SUPABASE_URL.rstrip("/") + self.LEADERBOARD_FUNCTION,
                                 headers=headers, json=payload, timeout=20)
        try:
            body = response.json() if response.text.strip() else {}
        except Exception:
            body = {"error": response.text[:250]}
        if response.status_code == 404:
            # Include the actual endpoint and gateway response. This helps distinguish
            # a stale APK/wrong project URL from a function that is not deployed.
            project_ref = response.headers.get("sb-project-ref", "unknown")
            detail = str(body.get("error") or body.get("message") or body.get("msg") or response.text or "No response body")
            raise RuntimeError(
                "Leaderboard endpoint returned HTTP 404. "
                f"URL: {self.SUPABASE_URL.rstrip('/') + self.LEADERBOARD_FUNCTION}; "
                f"project: {project_ref}; response: {detail[:180]}"
            )
        if response.status_code >= 400:
            detail = body.get("error") or body.get("message") or body.get("msg") or response.text or "Leaderboard request failed"
            raise RuntimeError(f"Leaderboard HTTP {response.status_code}: {str(detail)[:220]}")
        if not isinstance(body, dict):
            raise RuntimeError("Unexpected leaderboard response.")
        return body

    def open_leaderboards(self, *_):
        page = self._simple_page("Online Leaderboards")
        page.add_widget(Label(text="Best submissions for trusted built-in and approved community levels",
                              font_size=16, size_hint_y=None, height=48))
        status = Label(text="Loading online scores...", font_size=16,
                       size_hint_y=None, height=42)
        page.add_widget(status)
        scroll = ScrollView(do_scroll_x=False)
        listing = GridLayout(cols=1, spacing=7, padding=5, size_hint_y=None)
        listing.bind(minimum_height=listing.setter("height"))
        scroll.add_widget(listing)
        page.add_widget(scroll)
        page.add_widget(self._menu_button("Refresh", lambda *_: self._load_leaderboard_rows(status, listing)))
        page.add_widget(self._menu_button("Back", self.show_main_menu))
        self._replace_screen(page)
        Clock.schedule_once(lambda _dt: self._load_leaderboard_rows(status, listing), 0.05)

    def _load_leaderboard_rows(self, status, listing):
        listing.clear_widgets()
        try:
            result = self._leaderboard_request({"action": "list"})
            rows = result.get("rows", [])
            if not rows:
                status.text = "No scores yet. Finish an approved built-in or community level while logged in."
                return
            status.text = f"TOP SCORES — {len(rows)} entries"
            for index, row in enumerate(rows[:100], 1):
                name = str(row.get("username") or "Player")[:32]
                level = str(row.get("level_name") or row.get("level_key") or "Level")[:48]
                score = max(0, int(row.get("score", 0) or 0))
                elapsed = max(0.0, float(row.get("elapsed_seconds", 0) or 0))
                listing.add_widget(Label(
                    text=f"#{index}  {name}\n{level}  |  Score: {score}  |  Time: {elapsed:.2f}s",
                    font_size=16, size_hint_y=None, height=62, halign="left", valign="middle"))
        except Exception as exc:
            status.text = "Could not load leaderboard: " + str(exc)[:180]

    def _submit_leaderboard_result(self, result):
        """Submit a completion for a server-approved built-in or community level."""
        if not getattr(self, "access_token", None) or not getattr(self, "current_user", None):
            return "Log in to submit leaderboard scores."
        if getattr(self, "_community_play_mode", False):
            row = getattr(self, "_community_play_row", None) or {}
            raw_id = row.get("id") or row.get("display_id")
            if raw_id is None or not str(raw_id).strip():
                return "This community level has no stable ID, so it cannot be submitted."
            level_key = "community:" + str(raw_id).strip().lower()
            level_name = str(row.get("name") or "Community Level")[:80]
        elif getattr(self, "_builtin_play_mode", False):
            filename = os.path.basename(getattr(self, "_builtin_current_filename", "") or "")
            if not filename.lower().endswith(".json") or not filename:
                return "This level is not registered for online leaderboards."
            level_key = "offline:" + filename.lower()
            level_name = filename[:-5]
        else:
            return "Only approved built-in or community levels qualify for online leaderboards."
        payload = {
            "action": "submit",
            "level_key": level_key,
            "level_name": level_name,
            "score": max(0, int(getattr(self.editor_canvas, "score", 0) or 0)),
            "elapsed_seconds": round(max(0.0, float(result.get("time", 0.0))), 3),
            "coins": max(0, int(result.get("coins", 0) or 0)),
            "gems": max(0, int(result.get("gems", 0) or 0)),
        }
        try:
            response = self._leaderboard_request(payload)
            return str(response.get("message") or "Score submitted for server validation.")[:180]
        except Exception as exc:
            return "Leaderboard not submitted: " + str(exc)[:180]

    def open_completion_leaderboards(self, *_):
        page = self._simple_page("Completions & Orbs")
        page.add_widget(Label(text="Each approved level counts once per account. Replaying it cannot farm orbs.",
                              font_size=15, size_hint_y=None, height=48))
        status = Label(text="Loading rankings...", font_size=15, size_hint_y=None, height=38)
        page.add_widget(status)
        scroll = ScrollView(do_scroll_x=False)
        listing = GridLayout(cols=1, spacing=7, padding=5, size_hint_y=None)
        listing.bind(minimum_height=listing.setter("height"))
        scroll.add_widget(listing); page.add_widget(scroll)
        page.add_widget(self._menu_button("Refresh", lambda *_: self._load_completion_leaderboards(status, listing)))
        page.add_widget(self._menu_button("Back", self.show_main_menu))
        self._replace_screen(page)
        Clock.schedule_once(lambda _dt: self._load_completion_leaderboards(status, listing), 0.05)

    def _load_completion_leaderboards(self, status, listing):
        listing.clear_widgets()
        try:
            result = self._leaderboard_request({"action": "stats_leaderboard"})
            rows = result.get("rows", [])
            if not rows:
                status.text = "No approved level completions recorded yet."
                return
            status.text = f"PLAYER RANKINGS — {len(rows)} players"
            for heading, field in (("MOST COMPLETED LEVELS", "completed_levels"), ("MOST ORBS", "orbs")):
                listing.add_widget(Label(text=heading, font_size=20, bold=True,
                                         size_hint_y=None, height=42, color=NEON_CYAN))
                ranked = sorted(rows, key=lambda r: int(r.get(field, 0) or 0), reverse=True)
                if not any(int(r.get(field, 0) or 0) for r in ranked):
                    listing.add_widget(Label(text="No records yet.", size_hint_y=None, height=36))
                for i, row in enumerate(ranked[:20], 1):
                    value = int(row.get(field, 0) or 0)
                    if value <= 0: continue
                    listing.add_widget(Label(text=f"#{i}  {str(row.get('username') or 'Player')[:32]} — {value} {('levels' if field == 'completed_levels' else 'orbs')}",
                                             font_size=16, size_hint_y=None, height=38, halign="left"))
        except Exception as exc:
            status.text = ("Could not load rankings: " + str(exc))[:200]

    def rate_community_level(self, level):
        if not self.access_token or not self.current_user:
            self.community_status.text = "Log in to rate a community level. Your rating is anonymous in the public details."
            return
        content = BoxLayout(orientation="vertical", padding=12, spacing=10)
        content.add_widget(Label(text="How difficult did this level feel to you? This is a player rating, not the admin difficulty.",
                                 size_hint_y=None, height=70, font_size=15))
        rating = Spinner(text="5 stars", values=("1 star", "2 stars", "3 stars", "4 stars", "5 stars"),
                         size_hint_y=None, height=54, font_size=18)
        content.add_widget(rating)
        status = Label(text="Your rating contributes only to the public average and count.", size_hint_y=None, height=42, font_size=13)
        content.add_widget(status)
        popup = Popup(title="Rate Level", content=content, size_hint=(0.92, 0.45))
        buttons = BoxLayout(size_hint_y=None, height=48, spacing=8)
        def send(*_):
            try:
                stars = int(rating.text.split()[0])
                result = self._leaderboard_request({"action": "rate_level", "level_id": str(level.get("id") or ""), "rating": stars})
                level["rating_average"] = result.get("rating_average", level.get("rating_average", 0))
                level["rating_count"] = result.get("rating_count", level.get("rating_count", 0))
                popup.dismiss()
                self.community_status.text = f"Rating saved: {float(level.get('rating_average') or 0):.1f}/5 from {int(level.get('rating_count') or 0)} player ratings."
                self._render_community_levels(self._community_rows)
            except Exception as exc:
                status.text = ("Rating not saved: " + str(exc))[:180]
        buttons.add_widget(self._menu_button("Submit Rating", send))
        buttons.add_widget(self._menu_button("Cancel", popup.dismiss))
        content.add_widget(buttons); popup.open()

    def _progress_file(self):
        """Per-install progress storage; works offline and does not require new Supabase tables."""
        base = getattr(self, "user_data_dir", None) or os.path.join(os.path.expanduser("~"), ".2d_platformer")
        os.makedirs(base, exist_ok=True)
        return os.path.join(base, "player_progress.json")

    def _load_progress_data(self):
        try:
            with open(self._progress_file(), "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("Invalid progress data")
        except (OSError, ValueError, TypeError):
            data = {}
        data.setdefault("levels", {})
        data.setdefault("achievements", {})
        data.setdefault("total_coins_collected", 0)
        data.setdefault("total_completions", 0)
        # Spendable in-game currency. Collectible rewards are granted only once
        # per level/object identity, when the player finishes the level.
        data.setdefault("currency_balance", 0)
        data.setdefault("claimed_collectibles", [])
        if not isinstance(data.get("claimed_collectibles"), list):
            data["claimed_collectibles"] = []
        data.setdefault("claimed_level_ad_bonuses", [])
        if not isinstance(data.get("claimed_level_ad_bonuses"), list):
            data["claimed_level_ad_bonuses"] = []
        data["currency_balance"] = max(0, int(data.get("currency_balance", 0) or 0))
        return data

    def _save_progress_data(self, data):
        path = self._progress_file()
        temp_path = path + ".tmp"
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(temp_path, path)
            return True
        except OSError:
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except OSError:
                pass
            return False

    def _current_progress_level(self):
        if getattr(self, "_community_play_mode", False):
            row = getattr(self, "_community_play_row", None) or {}
            level_id = row.get("id") or row.get("display_id") or row.get("name") or "unknown"
            return "community:" + str(level_id), str(row.get("name") or "Community Level")
        if getattr(self, "_builtin_play_mode", False):
            filename = os.path.basename(getattr(self, "_builtin_current_filename", "") or "Level.json")
            return "offline:" + filename.lower(), filename[:-5] if filename.lower().endswith(".json") else filename
        stage = (getattr(self, "stages", None) or [{"name": "Custom Level"}])[getattr(self, "current_stage_index", 0)]
        name = str(stage.get("name") or "Custom Level")
        return "custom:" + name.lower(), name

    def _record_level_completion(self):
        canvas = self.editor_canvas
        level_key, level_name = self._current_progress_level()
        # Include every stage in the run. The current stage may not yet have
        # been saved by a transition, so overlay its live grid and collection set.
        stage_rows = []
        for stage_index, stage in enumerate(getattr(self, "stages", []) or []):
            stage_grid = stage.get("objects", {}) if isinstance(stage, dict) else {}
            stage_collected = set(getattr(self, "_play_stage_collected", {}).get(stage_index, set()))
            if stage_index == getattr(self, "current_stage_index", 0):
                stage_grid = canvas.grid_data
                stage_collected = set(canvas.collected_ids)
            stage_rows.append((stage_index, stage_grid, stage_collected))
        if not stage_rows:
            stage_rows = [(0, canvas.grid_data, set(canvas.collected_ids))]

        level_coins = sum(1 for _i, grid, collected in stage_rows
                          for key, obj in grid.items()
                          if obj.get("id") == 6 and key in collected)
        total_coins_in_level = sum(1 for _i, grid, _collected in stage_rows
                                   for obj in grid.values() if obj.get("id") == 6)
        gems = sum(1 for _i, grid, collected in stage_rows
                   for key, obj in grid.items()
                   if obj.get("id") == 7 and key in collected)
        total_gems_in_level = sum(1 for _i, grid, _collected in stage_rows
                                  for obj in grid.values() if obj.get("id") == 7)
        run_time = max(0.0, float(getattr(canvas, "elapsed_time", 0.0)))
        data = self._load_progress_data()
        levels = data["levels"]
        record = levels.setdefault(level_key, {"name": level_name, "completed": False,
                                                "completions": 0, "best_time": None,
                                                "best_coins": 0, "total_coins": total_coins_in_level})
        record["name"] = level_name
        record["completed"] = True
        record["completions"] = int(record.get("completions", 0)) + 1
        record["last_time"] = round(run_time, 3)
        record["last_coins"] = level_coins
        record["total_coins"] = total_coins_in_level
        record["best_coins"] = max(int(record.get("best_coins", 0)), level_coins)
        previous_best = record.get("best_time")
        if previous_best is None or run_time < float(previous_best):
            record["best_time"] = round(run_time, 3)

        # Anti-farming: currency is paid only after a win, and each collectible
        # at a given level/object position can pay once on this installation.
        # Coin = 100 wallet coins; gem = 150 wallet coins.
        claimed = set(str(v) for v in data.get("claimed_collectibles", []))
        claimed_before = set(claimed)
        wallet_reward = 0
        newly_claimed = 0
        # Economy rewards are disabled in the live editor/custom test level.
        # Community levels made by the current player are also ineligible.
        # This blocks the easiest self-created-level farming route.
        reward_eligible = bool(getattr(self, "_builtin_play_mode", False))
        if getattr(self, "_community_play_mode", False):
            community_row = getattr(self, "_community_play_row", None) or {}
            owner_id = str(community_row.get("creator_id") or "")
            current_id = str((getattr(self, "current_user", None) or {}).get("id") or "")
            owner_name = str(community_row.get("creator_username") or "").strip().lower()
            current_name = str(getattr(self, "current_username", "")).strip().lower()
            reward_eligible = not ((owner_id and current_id and owner_id == current_id)
                                   or (owner_name and current_name and owner_name == current_name))
        coin_paid = 0
        gem_paid = 0
        newly_claimed_coin_ids = []
        newly_claimed_gem_ids = []
        for stage_index, stage_grid, stage_collected in stage_rows:
            for key, obj in sorted(stage_grid.items(), key=lambda pair: repr(pair[0])):
                oid = int(obj.get("id", -1))
                if oid not in (6, 7) or key not in stage_collected:
                    continue
                # Reward caps apply to the whole level pack, not separately to
                # each stage: maximum 10 coins and 5 gems per completed pack.
                if oid == 6:
                    if coin_paid >= 10:
                        continue
                    coin_paid += 1
                else:
                    if gem_paid >= 5:
                        continue
                    gem_paid += 1

                legacy_id = f"{level_key}|{oid}|{repr(key)}"
                claim_id = (legacy_id if stage_index == 0 else
                            f"{level_key}|stage:{stage_index}|{oid}|{repr(key)}")
                # Preserve old single-stage claim IDs. For later stages, a
                # legacy claim at the same coordinate is treated as paid too,
                # preventing a migration from accidentally granting it twice.
                already_claimed = claim_id in claimed or (stage_index > 0 and legacy_id in claimed)
                if already_claimed:
                    claimed.add(claim_id)
                    continue
                claimed.add(claim_id)
                newly_claimed += 1
                if oid == 6:
                    newly_claimed_coin_ids.append(claim_id)
                else:
                    newly_claimed_gem_ids.append(claim_id)
                if reward_eligible:
                    wallet_reward += 100 if oid == 6 else 150
        data["claimed_collectibles"] = sorted(claimed)
        data["currency_balance"] = max(0, int(data.get("currency_balance", 0))) + wallet_reward
        # Lifetime collectible totals count newly claimed unique objects across
        # all stages, and never increase on replay of an already-claimed item.
        data["total_coins_collected"] = int(data.get("total_coins_collected", 0)) + len(newly_claimed_coin_ids)
        data["total_gems_collected"] = int(data.get("total_gems_collected", 0)) + len(newly_claimed_gem_ids)
        data["total_completions"] = int(data.get("total_completions", 0)) + 1

        achievements = data["achievements"]
        previously_unlocked = set(achievements)
        completed_count = len([v for v in levels.values() if v.get("completed")])
        total_coins = int(data.get("total_coins_collected", 0))
        total_gems = int(data.get("total_gems_collected", 0))
        record_key = level_key
        record_now = levels.get(record_key, {})
        def unlock(key):
            for _category, items in ACHIEVEMENT_CATEGORIES.items():
                for item_key, title, description in items:
                    if item_key == key and key not in achievements:
                        achievements[key] = {"title": title, "description": description, "unlocked": True, "unlocked_at": int(time.time())}
                        return
        # Achievements supported by reliable progress data in this build.
        if data["total_completions"] >= 1: unlock("getting_started"); unlock("first_steps")
        if completed_count >= 3: unlock("warming_up")
        if completed_count >= 5: unlock("rookie_player"); unlock("five_levels")
        if completed_count >= 10: unlock("platformer_fan")
        if completed_count >= 25: unlock("dedicated_player"); unlock("level_master_25")
        if completed_count >= 50: unlock("marathon_gamer"); unlock("level_champion_50")
        if completed_count >= 100: unlock("regular_player"); unlock("legendary_completionist_100")
        if total_coins >= 1: unlock("first_coin")
        if total_coins >= 100: unlock("coin_collector"); unlock("coin_100")
        if total_coins >= 500: unlock("coin_hoarder")
        if total_coins >= 1000: unlock("coin_millionaire")
        if gems > 0: unlock("gem_finder"); unlock("gem_hunter")
        if run_time <= 30: unlock("speed_demon"); unlock("speedrun_30")
        if total_coins_in_level > 0 and level_coins >= total_coins_in_level: unlock("treasure_hunter")
        if total_gems_in_level > 0 and gems >= total_gems_in_level: unlock("gem_perfectionist")
        if getattr(self, "_community_play_mode", False):
            data["community_levels_played"] = int(data.get("community_levels_played", 0)) + 1
            unlock("community_explorer")
            if data["community_levels_played"] >= 25: unlock("community_regular")
            if data["community_levels_played"] >= 100: unlock("community_champion")
        if record_now.get("completions", 0) >= 5: unlock("persistent")
        if len(getattr(self, "stages", []) or []) >= 5: unlock("stage_designer")
        saved = self._save_progress_data(data)
        newly_unlocked = {k: v for k, v in achievements.items() if k not in previously_unlocked}
        return {"name": level_name, "level_key": level_key, "time": run_time, "coins": level_coins,
                "total_coins": total_coins_in_level, "gems": gems,
                "total_gems": total_gems_in_level,
                "currency_reward": wallet_reward, "currency_balance": data["currency_balance"],
                "new_currency_collectibles": newly_claimed,
                "unlocked": newly_unlocked, "saved": saved, "data": data}

    def open_achievements(self, *_):
        data = self._load_progress_data()
        page = self._simple_page("Achievements & Progress")
        all_items = [(category, item) for category, items in ACHIEVEMENT_CATEGORIES.items() for item in items]
        unlocked = data.get("achievements", {})
        completed = [v for v in data.get("levels", {}).values() if v.get("completed")]
        page.add_widget(Label(text=f"ACHIEVEMENTS: {len(unlocked)} / {len(all_items)} unlocked    |    LEVELS: {len(completed)}    |    FINISHES: {data.get('total_completions', 0)}",
                              font_size=17, size_hint_y=None, height=46))
        page.add_widget(Label(text=f"UNIQUE COINS: {int(data.get('total_coins_collected', 0))}    |    GEMS: {int(data.get('total_gems_collected', 0))}",
                              font_size=16, size_hint_y=None, height=36))
        scroll = ScrollView(do_scroll_x=False, bar_width=8)
        listing = GridLayout(cols=1, spacing=5, padding=4, size_hint_y=None)
        listing.bind(minimum_height=listing.setter("height"))
        for category, items in ACHIEVEMENT_CATEGORIES.items():
            listing.add_widget(Label(text=f"[b]{category.upper()}[/b]", markup=True, font_size=19,
                                     size_hint_y=None, height=42, halign="left"))
            for key, title, description in items:
                done = key in unlocked
                mark = "[UNLOCKED]" if done else "[LOCKED]"
                line = Label(text=f"{mark}  {title}\n{description}", font_size=15,
                             color=NEON_GREEN if done else (0.58, 0.65, 0.75, 1),
                             size_hint_y=None, height=56, halign="left", valign="middle")
                line.bind(size=lambda w, _v: setattr(w, "text_size", (w.width, None)))
                listing.add_widget(line)
        listing.add_widget(Label(text="Progress is saved locally on this device. Some movement, trigger, and community achievements need their specific event trackers wired in a future update.",
                                 font_size=13, size_hint_y=None, height=60, color=(0.7, 0.78, 0.86, 1)))
        scroll.add_widget(listing)
        page.add_widget(scroll)
        self._replace_screen(page)

    def open_normal_editor(self, *_):
        """Open the regular editor; admins may publish here like any other user."""
        self._builtin_editor_mode = False
        self._builtin_current_filename = ""
        self._builtin_play_mode = False
        self.open_editor()

    def open_editor(self, *_):
        # The active stage dictionary is canonical. Editing mutates this same
        # dictionary, so copying a stale canvas back here is unnecessary and
        # was capable of replacing a populated stage with {}.
        if hasattr(self, "stages") and self.stages and 0 <= self.current_stage_index < len(self.stages):
            active_stage = self.stages[self.current_stage_index]
            if isinstance(active_stage, dict):
                active_objects = active_stage.get("objects", {})
                if not isinstance(active_objects, dict):
                    active_objects = {}
                    active_stage["objects"] = active_objects
                old_canvas = getattr(self, "editor_canvas", None)
                if old_canvas is not None and old_canvas.grid_data is not active_objects:
                    old_canvas.grid_data = active_objects
                    old_canvas._runtime_index_dirty = True
                    old_canvas._all_object_items = ()
                    old_canvas._spatial_buckets = {}
        is_owner = bool(self.access_token) and (self.current_email or "").strip().lower() == "adnanzamanador@gmail.com"
        if hasattr(self, "admin_editor_btn") and hasattr(self, "top_bar_layout"):
            if is_owner and self.admin_editor_btn.parent is None:
                self.top_bar_layout.add_widget(self.admin_editor_btn, index=max(0, len(self.top_bar_layout.children)-1))
            elif not is_owner and self.admin_editor_btn.parent is self.top_bar_layout:
                self.top_bar_layout.remove_widget(self.admin_editor_btn)
        # Built-in/admin packs are local JSON only; never offer community publishing there.
        if hasattr(self, "upload_btn"):
            builtin_mode = bool(getattr(self, "_builtin_editor_mode", False))
            self.upload_btn.disabled = builtin_mode
            self.upload_btn.opacity = 0.35 if builtin_mode else 1
            self.upload_btn.text = "Admin: Local Only" if builtin_mode else "Upload"
        if hasattr(self, "editor_canvas"):
            self.editor_canvas._runtime_index_dirty = True
            self.editor_canvas._all_object_items = ()
            self.editor_canvas._spatial_buckets = {}
            self.editor_canvas._render_stage_index = self.current_stage_index
            Clock.schedule_once(lambda _dt: self.editor_canvas.redraw(), 0)
            Clock.schedule_once(lambda _dt: self.editor_canvas.redraw(), 0.15)
        self._replace_screen(self.root_layout)

    def return_to_menu(self, *_):
        if self.is_playing:
            self.toggle_play_mode()
        self.show_main_menu()

    def _simple_page(self, title, back=True):
        page = BoxLayout(orientation="vertical", padding=14, spacing=10)
        page.add_widget(Label(text=title, font_size=28, bold=True, size_hint_y=None, height=52))
        if back:
            page.add_widget(self._menu_button("Back to Main Menu", self.show_main_menu))
        return page

    def _cloud_account_id(self):
        user = getattr(self, "current_user", None) or {}
        uid = user.get("id")
        if not self.access_token or not uid:
            raise RuntimeError("Log in to a registered account before using cloud saves.")
        return str(uid)

    def _cloud_upsert_json(self, folder, filename, data):
        """Store one private JSON document in the signed-in player's cloud."""
        uid = self._cloud_account_id()
        safe_folder = folder if folder in ("levels", "offline_levels", "account") else "account"
        payload = [{"user_id": uid, "folder": safe_folder, "filename": os.path.basename(filename),
                    "file_data": data, "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}]
        self._api_request("POST", "/rest/v1/player_cloud_json?on_conflict=user_id,folder,filename",
                          payload=payload, access_token=self.access_token,
                          prefer="resolution=merge-duplicates,return=minimal")

    def save_all_to_cloud(self, *_):
        """Upload local level JSON, downloaded/offline JSON, progress, and preferences."""
        try:
            uid = self._cloud_account_id()
            uploaded = 0
            folders = (("levels", self.levels_directory()),
                       ("offline_levels", self._builtin_levels_directory()))
            for cloud_folder, local_folder in folders:
                for filename in sorted(os.listdir(local_folder)):
                    if not filename.lower().endswith(".json"):
                        continue
                    path = os.path.join(local_folder, filename)
                    if not os.path.isfile(path):
                        continue
                    try:
                        with open(path, "r", encoding="utf-8") as handle:
                            data = json.load(handle)
                        if not isinstance(data, (dict, list)):
                            continue
                        self._cloud_upsert_json(cloud_folder, filename, data)
                        uploaded += 1
                    except (OSError, ValueError, RuntimeError) as exc:
                        raise RuntimeError(f"Could not save {filename}: {exc}")
            for filename, data in (("player_progress.json", self._load_progress_data()),
                                   ("skin_preferences.json", getattr(self, "settings", {}))):
                self._cloud_upsert_json("account", filename, data)
                uploaded += 1
            self._cloud_status(f"CLOUD SAVE COMPLETE: {uploaded} JSON FILE(S) uploaded.")
        except Exception as exc:
            self._cloud_status("CLOUD SAVE FAILED: " + str(exc)[:220])

    def load_all_from_cloud(self, *_):
        """Download this account's cloud files, merging level files without deleting local work."""
        try:
            uid = self._cloud_account_id()
            rows = self._api_request("GET", "/rest/v1/player_cloud_json", params={
                "select": "folder,filename,file_data,updated_at",
                "user_id": "eq." + uid,
                "order": "updated_at.asc",
                "limit": "2000",
            }, access_token=self.access_token)
            if not isinstance(rows, list):
                raise RuntimeError("Cloud response was not a file list.")
            restored = 0
            conflicts = 0
            for row in rows:
                folder = row.get("folder")
                filename = os.path.basename(str(row.get("filename") or ""))
                data = row.get("file_data")
                if not filename or not isinstance(data, (dict, list)):
                    continue
                if folder in ("levels", "offline_levels"):
                    local_folder = self.levels_directory() if folder == "levels" else self._builtin_levels_directory()
                    target = os.path.join(local_folder, filename)
                    if os.path.isfile(target):
                        try:
                            with open(target, "r", encoding="utf-8") as handle:
                                local_data = json.load(handle)
                        except Exception:
                            local_data = None
                        if local_data == data:
                            continue
                        # Keep both copies if names collide, so loading cloud cannot destroy unsynced work.
                        stem, ext = os.path.splitext(filename)
                        target = os.path.join(local_folder, "Cloud - " + filename)
                        n = 2
                        while os.path.exists(target):
                            target = os.path.join(local_folder, f"Cloud - {stem} ({n}){ext}")
                            n += 1
                        conflicts += 1
                    with open(target, "w", encoding="utf-8") as handle:
                        json.dump(data, handle, ensure_ascii=False, indent=2)
                    restored += 1
                elif folder == "account":
                    if filename == "player_progress.json" and isinstance(data, dict):
                        # Merge cloud progress with this device instead of deleting either side's records.
                        local_progress = self._load_progress_data()
                        merged = dict(local_progress)
                        merged.update({k: v for k, v in data.items() if k not in ("levels", "achievements", "claimed_collectibles")})
                        merged_levels = dict(local_progress.get("levels", {}))
                        merged_levels.update(data.get("levels", {}) if isinstance(data.get("levels"), dict) else {})
                        merged["levels"] = merged_levels
                        merged_achievements = dict(local_progress.get("achievements", {}))
                        merged_achievements.update(data.get("achievements", {}) if isinstance(data.get("achievements"), dict) else {})
                        merged["achievements"] = merged_achievements
                        merged_claimed = set(local_progress.get("claimed_collectibles", []))
                        merged_claimed.update(data.get("claimed_collectibles", []) if isinstance(data.get("claimed_collectibles"), list) else [])
                        merged["claimed_collectibles"] = sorted(merged_claimed, key=str)
                        for counter in ("total_coins_collected", "total_completions", "currency_balance"):
                            try:
                                merged[counter] = max(int(local_progress.get(counter, 0) or 0), int(data.get(counter, 0) or 0))
                            except (TypeError, ValueError):
                                pass
                        with open(self._progress_file(), "w", encoding="utf-8") as handle:
                            json.dump(merged, handle, ensure_ascii=False, indent=2)
                        restored += 1
                    elif filename == "skin_preferences.json" and isinstance(data, dict):
                        with open(self._skin_preferences_file(), "w", encoding="utf-8") as handle:
                            json.dump(data, handle, ensure_ascii=False, indent=2)
                        self.settings = data
                        restored += 1
            self._cloud_status(f"CLOUD LOAD COMPLETE: {restored} file(s) restored; {conflicts} name conflict(s) kept as separate Cloud - files. Reopen Levels to see them.")
        except Exception as exc:
            self._cloud_status("CLOUD LOAD FAILED: " + str(exc)[:220])

    def _cloud_status(self, message):
        try:
            if hasattr(self, "status_label"):
                self.status_label.text = message[:260]
            else:
                popup = Popup(title="Cloud Save", content=Label(text=message, text_size=(420, None)),
                              size_hint=(0.9, 0.35))
                popup.open()
        except Exception:
            pass

    def open_level_menu(self, *_):
        page = self._simple_page("Levels")
        page.add_widget(self._menu_button("Start / Test Current Level", self.open_editor))
        page.add_widget(self._menu_button("Load Saved Local Level", self._load_from_menu))
        page.add_widget(self._menu_button("SAVE ALL LEVELS & PROGRESS TO CLOUD", self.save_all_to_cloud))
        page.add_widget(self._menu_button("LOAD LEVELS & PROGRESS FROM CLOUD", self.load_all_from_cloud))
        page.add_widget(self._menu_button("Play Built-in / Downloaded Levels (Offline)", self.open_builtin_player_menu))
        page.add_widget(Label(text="Cloud buttons require login and the Supabase cloud table setup. Downloaded JSON levels stay on this device for offline play.", font_size=14))
        self._replace_screen(page)

    def open_builtin_player_menu(self, *_):
        page = self._simple_page("Built-in Levels - Offline")
        folder = self._builtin_levels_directory()
        # The offline player menu intentionally starts with only the level
        # the creator has actually made: Tutorial.json. Generated samples and
        # placeholder campaign levels must not appear here.
        tutorial_file = next(
            (f for f in os.listdir(folder)
             if f.lower() == "tutorial.json" and os.path.isfile(os.path.join(folder, f))),
            None,
        )
        files = [tutorial_file] if tutorial_file else []
        if not files:
            page.add_widget(Label(text="Tutorial.json was not found in offline_levels.", font_size=16))
        scroll = ScrollView()
        listing = GridLayout(cols=1, spacing=7, size_hint_y=None, padding=4)
        listing.bind(minimum_height=listing.setter("height"))
        for filename in files:
            listing.add_widget(self._menu_button(filename[:-5] + "  -  PLAY OFFLINE", lambda *_a, f=filename: self.play_builtin_level(f)))
        scroll.add_widget(listing)
        page.add_widget(scroll)
        self._replace_screen(page)

    def _load_from_menu(self, *_):
        self.open_editor()
        self.open_load_popup()

    def _level_payload(self, name, description="", category="Other"):
        return {
            "name": name,
            "creator_username": self.current_username,
            "creator_id": (self.current_user or {}).get("id"),
            "description": description,
            "level_data": {
                "version": 1,
                "cols": self.editor_canvas.cols,
                "rows": self.editor_canvas.rows,
                "category": category if category in self.COMMUNITY_CATEGORIES[1:] else "Other",
                "objects": [
                    {"col": int(k[0]), "row": int(k[1]), "object": copy.deepcopy(o)}
                    for k, o in self.editor_canvas.grid_data.items()
                ],
            },
        }

    def open_auth_menu(self, *_):
        page = self._simple_page("Account")
        page.add_widget(Label(text="Registration requires email verification. Check your inbox and open the confirmation link.", font_size=16))
        page.add_widget(self._menu_button("Register", self.open_register))
        page.add_widget(self._menu_button("Login", self.open_login))
        page.add_widget(self._menu_button("Forgot Password", self.open_forgot_password))
        page.add_widget(self._menu_button("Continue as Guest", self.continue_guest))
        self._replace_screen(page)

    def _auth_form(self, title, fields, submit_callback, extra_note=""):
        page = BoxLayout(orientation="vertical", padding=18, spacing=9)
        page.add_widget(Label(text=title, font_size=26, bold=True, size_hint_y=None, height=48))
        widgets = {}
        for key, label, password in fields:
            inp = TextInput(hint_text=label, multiline=False, password=password, size_hint_y=None, height=64, padding=(14, 16), font_size=21)
            widgets[key] = inp
            page.add_widget(inp)
        self.auth_status = Label(text=extra_note, font_size=15)
        page.add_widget(self.auth_status)
        page.add_widget(self._menu_button("Submit", lambda *_: submit_callback(widgets)))
        page.add_widget(self._menu_button("Back", self.open_auth_menu))
        self._replace_screen(page)

    def open_register(self, *_):
        self._auth_form("Create Account", [
            ("username", "Username", False), ("email", "Email", False),
            ("password", "Password (at least 6 characters)", True)
        ], self._do_register, "You'll need access to this email address.")

    def _do_register(self, fields):
        username, email, password = fields["username"].text.strip(), fields["email"].text.strip(), fields["password"].text
        if not username or not email or len(password) < 6:
            self.auth_status.text = "Enter a username, valid email, and password of at least 6 characters."
            return
        try:
            result = self._auth_request("signup", {"email": email, "password": password, "data": {"username": username}})
            self.current_email = email
            self.auth_status.text = ("Signup request sent. Open the email and tap Confirm. "
                                     "If the link opens localhost:3000, fix Supabase Auth URL Configuration: "
                                     "set Site URL to a real URL, not localhost, and save.")
        except Exception as exc:
            self.auth_status.text = str(exc)[:240]

    def open_login(self, *_):
        self._auth_form("Login", [("email", "Email", False), ("password", "Password", True)], self._do_login)

    def _do_login(self, fields):
        email, password = fields["email"].text.strip(), fields["password"].text
        try:
            result = self._auth_request("token?grant_type=password", {"email": email, "password": password})
            self.access_token = result.get("access_token")
            self.current_user = result.get("user") or {}
            self.current_email = email
            metadata = self.current_user.get("user_metadata") or {}
            self.current_username = metadata.get("username") or email.split("@")[0]
            if self.access_token:
                self._save_auth_session(result)
            if not self.access_token:
                self.auth_status.text = "Login did not return a session. Confirm your email first."
                return
            self.auth_status.text = "Logged in successfully."
            self.show_main_menu()
        except Exception as exc:
            self.auth_status.text = str(exc)[:240]

    def open_forgot_password(self, *_):
        self._auth_form("Reset Password", [("email", "Email", False)], self._do_forgot_password,
                        "Supabase sends a reset link to this email.")

    def _do_forgot_password(self, fields):
        email = fields["email"].text.strip()
        try:
            self._api_request("POST", "/auth/v1/recover", {"email": email})
            self.auth_status.text = "If the email is registered, a password reset link will be sent."
        except Exception as exc:
            self.auth_status.text = str(exc)[:240]

    def continue_guest(self, *_):
        self.current_user = None
        self.access_token = None
        self.current_username = "Guest"
        self.show_main_menu()

    COMMUNITY_CATEGORIES = ("All Categories", "Platforming", "Puzzle", "Speedrun", "Beginner", "Hard", "Other")

    def open_community(self, *_):
        page = BoxLayout(orientation="vertical", padding=(20, 14), spacing=10)
        with page.canvas.before:
            Color(0.018, 0.025, 0.055, 1)
            page._bg_rect = Rectangle(pos=page.pos, size=page.size)
        page.bind(pos=lambda w, v: setattr(w._bg_rect, "pos", v),
                  size=lambda w, v: setattr(w._bg_rect, "size", v))

        header = BoxLayout(orientation="horizontal", size_hint_y=None, height=76, spacing=12)
        title = Label(text="[b][color=35DAFF]ONLINE[/color] [color=FF3898]COMMUNITY[/color][/b]",
                      markup=True, font_size=38, halign="left", valign="middle")
        title.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        header.add_widget(title)
        page.add_widget(header)
        page.add_widget(Label(text="COMMUNITY LEVELS  -  DISCOVER, DOWNLOAD & PLAY",
                              font_size=18, color=(0.55, 0.75, 0.88, 1),
                              size_hint_y=None, height=30, halign="left"))

        actions = BoxLayout(orientation="horizontal", size_hint_y=None, height=52, spacing=10)
        menu_btn = self._menu_button("<- MAIN MENU", self.show_main_menu)
        menu_btn.height = 52; menu_btn.font_size = 18; menu_btn.size_hint_y = None
        menu_btn.background_color = (0.22, 0.09, 0.25, 1)
        refresh_btn = self._menu_button("RETRY REFRESH", self.refresh_community)
        refresh_btn.height = 52; refresh_btn.font_size = 18; refresh_btn.size_hint_y = None
        refresh_btn.background_color = (0.035, 0.22, 0.32, 1)
        actions.add_widget(menu_btn); actions.add_widget(refresh_btn)
        page.add_widget(actions)

        search_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=58, spacing=8)
        self.community_search_input = TextInput(hint_text="Search level name or ID", multiline=False,
                                                size_hint_y=None, height=56, padding=(12, 12), font_size=21)
        search_row.add_widget(self.community_search_input)
        search_btn = self._menu_button("SEARCH", self.search_community_levels)
        search_btn.height = 56; search_btn.font_size = 18
        search_row.add_widget(search_btn)
        page.add_widget(search_row)

        filter_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=52, spacing=8)
        self.community_category_spinner = Spinner(text="All Categories", values=self.COMMUNITY_CATEGORIES,
                                                   size_hint_x=0.42, size_hint_y=None, height=50,
                                                   font_size=18, background_color=(0.07, 0.22, 0.32, 1))
        self.community_category_spinner.bind(text=self.filter_community_category)
        filter_row.add_widget(self.community_category_spinner)
        self.community_user_search_input = TextInput(hint_text="Search creator username", multiline=False,
                                                     size_hint_y=None, height=50, padding=(10, 10), font_size=18)
        filter_row.add_widget(self.community_user_search_input)
        user_btn = self._menu_button("USER", self.search_community_user)
        user_btn.height = 50; user_btn.font_size = 16
        filter_row.add_widget(user_btn)
        page.add_widget(filter_row)

        scroll = ScrollView(do_scroll_x=False, bar_width=7, scroll_type=["bars", "content"])
        self.community_list = GridLayout(cols=1, spacing=10, padding=(2, 5, 7, 5), size_hint_y=None)
        self.community_list.bind(minimum_height=self.community_list.setter("height"))
        scroll.add_widget(self.community_list)
        page.add_widget(scroll)
        self.community_status = Label(text="CONNECTING TO COMMUNITY...", font_size=18,
                                      color=NEON_CYAN, size_hint_y=None, height=36,
                                      halign="left", valign="middle")
        self.community_status.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        page.add_widget(self.community_status)
        self._community_rows = []
        self._replace_screen(page)
        self.refresh_community()

    def _community_category(self, row):
        data = row.get("level_data") or {}
        category = data.get("category") if isinstance(data, dict) else None
        if category in self.COMMUNITY_CATEGORIES[1:]:
            return category
        # Older published levels have no category metadata; classify them as Other.
        return "Other"

    def refresh_community(self, *_):
        try:
            rows = self._api_request("GET", "/rest/v1/levels", params={
                "select": "id,display_id,name,creator_username,creator_id,description,level_data,likes,play_count,difficulty,rating_average,rating_count,created_at",
                "order": "created_at.desc", "limit": "200"
            })
            self._community_rows = rows if isinstance(rows, list) else []
            self._render_community_levels(self._community_rows)
        except Exception as exc:
            self.community_list.clear_widgets()
            self.community_status.text = ("COMMUNITY CONNECTION ERROR: " + str(exc))[:250]

    def filter_community_category(self, *_):
        if hasattr(self, "_community_rows"):
            self._render_community_levels(self._community_rows)

    def _render_community_levels(self, rows):
        self._community_rows = rows if isinstance(rows, list) else []
        self.community_list.clear_widgets()
        category = getattr(self, "community_category_spinner", None)
        selected_category = category.text if category else "All Categories"
        visible_rows = [r for r in self._community_rows
                        if selected_category == "All Categories" or self._community_category(r) == selected_category]
        for row in visible_rows:
            card = BoxLayout(orientation="vertical", size_hint_y=None, height=286, spacing=8, padding=(12, 10))
            with card.canvas.before:
                Color(0.045, 0.065, 0.12, 1)
                card._panel_rect = Rectangle(pos=card.pos, size=card.size)
            with card.canvas.after:
                Color(0.12, 0.68, 0.88, 0.9)
                card._panel_line = Line(rectangle=(card.x, card.y, card.width, card.height), width=1.1)
            def _sync_card(w, _v):
                w._panel_rect.pos = w.pos; w._panel_rect.size = w.size
                w._panel_line.rectangle = (w.x, w.y, w.width, w.height)
            card.bind(pos=_sync_card, size=_sync_card)

            top = BoxLayout(orientation="horizontal", spacing=12)
            preview = CommunityLevelThumbnail(level_data=row.get("level_data") or {},
                                              size_hint=(None, None), size=(190, 112))
            top.add_widget(preview)
            info = Label(text=(f"[b][color=F2FAFF]#{row.get('display_id', '?')} - {row.get('name') or 'Untitled'}[/color][/b]\n"
                               f"[color=8AA9C4]Creator: {row.get('creator_username') or 'Guest'}[/color]\n"
                               f"[color=75DFFF]{self._community_category(row)}[/color]  -  "
                               f"[color=FFD166]Difficulty: {row.get('difficulty') or 'Easy'}[/color]\n"
                               f"[color=FF6AB5]LIKES {int(row.get('likes') or 0)}[/color]  "
                               f"[color=45DFFF]PLAYS {int(row.get('play_count') or 0)}[/color]  "
                               f"[color=E5A4FF]Rating {float(row.get('rating_average') or 0):.1f}/5 ({int(row.get('rating_count') or 0)})[/color]\n"
                               f"[color=B8C8D9]{(row.get('description') or 'No description')[:100]}[/color]"),
                         markup=True, font_size=17, halign="left", valign="middle")
            info.bind(size=lambda inst, val: setattr(inst, "text_size", val))
            top.add_widget(info)
            card.add_widget(top)

            buttons = BoxLayout(orientation="horizontal", size_hint_y=None, height=54, spacing=8)
            play = self._menu_button("[PLAY] PLAY", lambda *_a, r=row: self.play_community_level(r)); play.height = 54; play.font_size = 17
            download = self._menu_button("v DOWNLOAD", lambda *_a, r=row: self.download_community_level(r)); download.height = 54; download.font_size = 16
            like = self._menu_button("LIKES LIKE", lambda *_a, r=row: self.like_community_level(r)); like.height = 54; like.font_size = 16
            report = self._menu_button("REPORT", lambda *_a, r=row: self.report_level_prompt(level=r)); report.height = 54; report.font_size = 16
            rate = self._menu_button("RATE", lambda *_a, r=row: self.rate_community_level(r)); rate.height = 54; rate.font_size = 16
            buttons.add_widget(play); buttons.add_widget(download); buttons.add_widget(like); buttons.add_widget(rate); buttons.add_widget(report)
            card.add_widget(buttons)
            self.community_list.add_widget(card)
        self.community_status.text = f"{len(visible_rows)} LEVEL(S) SHOWN / {len(self._community_rows)} TOTAL"

    def search_community_levels(self, *_):
        query = (getattr(self, "community_search_input", None).text or "").strip() if hasattr(self, "community_search_input") else ""
        if not query:
            self.refresh_community(); return
        try:
            if query.isdigit():
                rows = self._api_request("GET", "/rest/v1/levels", params={
                    "select":"id,display_id,name,creator_username,creator_id,description,level_data,likes,play_count,difficulty,rating_average,rating_count,created_at",
                    "display_id":"eq." + query, "limit":"50"
                })
                if not rows:
                    rows = self._api_request("GET", "/rest/v1/levels", params={
                        "select":"id,display_id,name,creator_username,creator_id,description,level_data,likes,play_count,difficulty,rating_average,rating_count,created_at",
                        "id":"eq." + query, "limit":"50"
                    })
            else:
                rows = self._api_request("GET", "/rest/v1/levels", params={
                    "select":"id,display_id,name,creator_username,creator_id,description,level_data,likes,play_count,difficulty,rating_average,rating_count,created_at",
                    "name":"ilike.*" + query.replace("*", "" ) + "*", "order":"created_at.desc", "limit":"100"
                })
            self._community_rows = rows if isinstance(rows, list) else []
            self._render_community_levels(self._community_rows)
            if not rows: self.community_status.text = "No levels matched that ID or name."
        except Exception as exc:
            self.community_status.text = ("Level search failed: " + str(exc))[:250]

    def search_community_user(self, *_):
        query = (getattr(self, "community_user_search_input", None).text or "").strip() if hasattr(self, "community_user_search_input") else ""
        if not query:
            self.community_status.text = "Enter a username to search."; return
        try:
            users = self._api_request("GET", "/rest/v1/game_profiles", params={
                "select":"user_id,display_name,avatar_url,created_at",
                "display_name":"ilike.*" + query.replace("*", "") + "*", "limit":"30"
            })
            if not users:
                self.community_status.text = "No profile rows matched. Check whether game_profiles contains users and whether display_name is populated."; return
            self.community_list.clear_widgets()
            for user in users:
                box = BoxLayout(orientation="vertical", size_hint_y=None, height=190, spacing=12, padding=(16, 14))
                info = Label(text=f"[b]{user.get('display_name') or 'Player'}[/b]\nUser details - Joined: {str(user.get('created_at') or 'Unknown')[:10]}", markup=True, font_size=24, halign="left", valign="middle")
                info.bind(size=lambda inst, val: setattr(inst, "text_size", val))
                box.add_widget(info)
                btn = self._menu_button("VIEW THIS USER'S LEVELS", lambda *_a, u=user: self.browse_user_levels(u)); btn.height = 68; btn.font_size = 20
                box.add_widget(btn); self.community_list.add_widget(box)
            self.community_status.text = f"{len(users)} USER(S) FOUND"
        except Exception as exc:
            self.community_status.text = ("User search failed: " + str(exc))[:250]

    def browse_user_levels(self, user):
        try:
            params = {"select":"id,display_id,name,creator_username,creator_id,description,level_data,likes,play_count,difficulty,rating_average,rating_count,created_at",
                      "creator_id":"eq." + str(user.get("user_id")), "order":"created_at.desc", "limit":"200"}
            rows = self._api_request("GET", "/rest/v1/levels", params=params)
            # For older levels without creator_id, use the exact display name only.
            if not rows and user.get("display_name"):
                rows = self._api_request("GET", "/rest/v1/levels", params={
                    "select":"id,display_id,name,creator_username,creator_id,description,level_data,likes,play_count,difficulty,rating_average,rating_count,created_at",
                    "creator_username":"eq." + str(user.get("display_name")), "order":"created_at.desc", "limit":"200"})
            self._render_community_levels(rows)
            self.community_status.text = f"LEVELS BY {user.get('display_name') or 'PLAYER'}: {len(rows)}" if rows else f"No public levels found for {user.get('display_name') or 'this user'}."
        except Exception as exc:
            self.community_status.text = ("Could not load this user's levels: " + str(exc))[:250]

    def _load_community_grid(self, level):
        data = level.get("level_data") or {}
        new_grid = {}
        for item in data.get("objects", []):
            col, rownum = int(item["col"]), int(item["row"])
            obj = item.get("object")
            if isinstance(obj, dict) and 0 <= col < self.editor_canvas.cols and 0 <= rownum < self.editor_canvas.rows:
                key = (col, rownum)
                if key in new_grid:
                    serial = 1
                    while (col, rownum, serial) in new_grid:
                        serial += 1
                    key = (col, rownum, serial)
                new_grid[key] = copy.deepcopy(obj)
        self.editor_canvas.grid_data = new_grid
        self.editor_canvas.selected_key = None
        self.editor_canvas.active_spawn = None
        self.editor_canvas.reset_controls()
        self.editor_canvas.redraw()

    def download_community_level(self, row):
        """Save a community level into the app's offline_levels folder."""
        try:
            data = row.get("level_data")
            if not isinstance(data, dict) or not (isinstance(data.get("objects"), list) or isinstance(data.get("stages"), list)):
                raise ValueError("This community level has invalid or unsupported level data.")
            folder = self._builtin_levels_directory()
            base = re.sub(r"[^A-Za-z0-9 _-]", "_", str(row.get("name") or "CommunityLevel"))[:55].strip(" ._") or "CommunityLevel"
            base = "Community - " + base
            filename = base + ".json"
            counter = 2
            while os.path.exists(os.path.join(folder, filename)):
                filename = f"{base} ({counter}).json"
                counter += 1
            saved = copy.deepcopy(data)
            saved.setdefault("name", row.get("name") or base)
            saved.setdefault("category", self._community_category(row))
            saved["community_source"] = {
                "level_id": row.get("id"),
                "display_id": row.get("display_id"),
                "creator_username": row.get("creator_username") or "Guest",
            }
            target = os.path.join(folder, filename)
            with open(target, "w", encoding="utf-8") as f:
                json.dump(saved, f, ensure_ascii=False, indent=2)
            cloud_note = ""
            if self.access_token:
                try:
                    self._cloud_upsert_json("offline_levels", filename, saved)
                    cloud_note = " + CLOUD BACKUP SAVED"
                except Exception as cloud_exc:
                    cloud_note = " (offline copy saved; cloud backup failed: " + str(cloud_exc)[:90] + ")"
            self.community_status.text = f"DOWNLOADED OFFLINE: {filename}" + cloud_note
            progress = self._load_progress_data()
            for category, items in ACHIEVEMENT_CATEGORIES.items():
                for key, title, description in items:
                    if key == "first_download":
                        progress.setdefault("achievements", {}).setdefault(key, {"title": title, "description": description, "unlocked": True, "unlocked_at": int(time.time())})
            self._save_progress_data(progress)
        except Exception as exc:
            self.community_status.text = ("Download failed: " + str(exc))[:250]

    def _community_rpc_count(self, rpc_name, level):
        """Call a server-side anti-abuse RPC. Requires a signed-in user."""
        level_id = str(level.get("id") or "")
        if not level_id:
            raise RuntimeError("This level has no database ID.")
        if not getattr(self, "access_token", None):
            raise RuntimeError("Log in to like levels or count plays safely.")
        result = self._api_request(
            "POST", f"/rest/v1/rpc/{rpc_name}",
            payload={"p_level_id": level_id},
            access_token=self.access_token,
        )
        try:
            return int(result)
        except (TypeError, ValueError):
            if isinstance(result, list) and result:
                return int(result[0])
            if isinstance(result, dict) and rpc_name in result:
                return int(result[rpc_name])
            raise RuntimeError("Counter RPC returned an unexpected response. Run the anti-spam SQL setup first.")

    def play_community_level(self, level):
        try:
            self._load_community_grid(level)
            self._community_play_row = level
            self._community_play_mode = True
            self._builtin_editor_mode = False
            self._builtin_play_mode = False
            self.open_editor()
            if not self.is_playing:
                self.toggle_play_mode()
            self.status_label.text = f"Playing community level #{level.get('display_id', '?')}: {level.get('name','Untitled')}"
            try:
                count = self._community_rpc_count("record_level_play", level)
                self.community_status.text = f"PLAY COUNT SAVED  -  {count} PLAYS"
            except Exception as counter_exc:
                # Gameplay still starts even if database permissions reject the counter update.
                self.community_status.text = ("Level started, but play count was not saved: " + str(counter_exc))[:250]
        except Exception as exc:
            self._community_play_mode = False
            self.community_status.text = f"Could not start level: {exc}"

    def like_community_level(self, level):
        try:
            count = self._community_rpc_count("like_community_level", level)
            self.community_status.text = f"LIKE SAVED (or already liked)  -  {count} LIKES"
            self.refresh_community()
        except Exception as exc:
            self.community_status.text = ("LIKE NOT SAVED: " + str(exc))[:250]

    def upload_from_editor(self, *_):
        """Start verification before publishing a user-created level."""
        if getattr(self, "_builtin_editor_mode", False):
            self.status_label.text = "Admin built-in levels can only be saved as local JSON files."
            return
        self.publish_current_level()

    def _verify_current_user_level(self):
        """Basic automatic checks before a user level can be published."""
        grid = getattr(self.editor_canvas, "grid_data", {})
        if not isinstance(grid, dict) or not grid:
            return False, "Your level is empty. Add some objects before uploading."
        if len(grid) > self.editor_canvas.cols * self.editor_canvas.rows * 4:
            return False, "Too many objects. Reduce the object count and try again."
        for key, obj in grid.items():
            if not isinstance(key, tuple) or len(key) < 2:
                return False, "A level object has invalid position data."
            try:
                col, row = int(key[0]), int(key[1])
            except (TypeError, ValueError):
                return False, "A level object has invalid coordinates."
            if not (0 <= col < self.editor_canvas.cols and 0 <= row < self.editor_canvas.rows):
                return False, "An object is outside the level grid. Move it inside the grid."
            if not isinstance(obj, dict) or "id" not in obj:
                return False, "An object has invalid data. Remove it and place it again."
        return True, "Passed basic checks"

    def publish_current_level(self, *_):
        if getattr(self, "_builtin_editor_mode", False):
            self.status_label.text = "Admin built-in levels cannot be uploaded to the community. Save the JSON instead."
            return
        if not self.access_token:
            self.status_label.text = "Log in first (Menu -> Register / Login) to upload."
            return
        passed, reason = self._verify_current_user_level()
        if not passed:
            self.status_label.text = "Verification failed: " + reason
            return
        content = BoxLayout(orientation="vertical", padding=10, spacing=8)
        name_input = TextInput(hint_text="Level name", multiline=False, size_hint_y=None, height=58, padding=(12, 12), font_size=20)
        desc_input = TextInput(hint_text="Description (optional)", multiline=False, size_hint_y=None, height=58, padding=(12, 12), font_size=20)
        category_input = Spinner(text="Other", values=self.COMMUNITY_CATEGORIES[1:], size_hint_y=None, height=54, font_size=18)
        content.add_widget(Label(text="LEVEL VERIFICATION PASSED\n" + reason, size_hint_y=None, height=58, font_size=17, color=(0.3, 0.95, 0.6, 1)))
        content.add_widget(Label(text="Difficulty starts at Easy. Only the admin can change it after upload.", size_hint_y=None, height=42, font_size=14))
        content.add_widget(Label(text="Duplicate level name + description combinations are rejected.", size_hint_y=None, height=32, font_size=13))
        content.add_widget(name_input)
        content.add_widget(desc_input)
        content.add_widget(Label(text="Choose a category", size_hint_y=None, height=30, font_size=16))
        content.add_widget(category_input)
        agreement = Switch(active=False, size_hint_y=None, height=44)
        agreement_row = BoxLayout(size_hint_y=None, height=52, spacing=8)
        agreement_row.add_widget(agreement)
        agreement_row.add_widget(Label(text="I checked my level: it is playable and does not contain offensive, hateful, or inappropriate content.", font_size=14, halign="left", valign="middle"))
        content.add_widget(agreement_row)
        buttons = BoxLayout(size_hint_y=None, height=48, spacing=8)
        popup = Popup(title="Verify & Publish Level", content=content, size_hint=(0.92, 0.72), auto_dismiss=False)
        def do_publish(*_):
            name = name_input.text.strip()
            if not name:
                self.status_label.text = "Enter a level name."
                return
            if not agreement.active:
                self.status_label.text = "Verification required: confirm the community rules first."
                return
            # Re-check at publish time so changing the level cannot bypass validation.
            ok, message = self._verify_current_user_level()
            if not ok:
                self.status_label.text = "Verification failed: " + message
                popup.dismiss()
                return
            try:
                description = desc_input.text.strip()
                existing = self._api_request("GET", "/rest/v1/levels", params={
                    "select": "id,name,description", "name": "eq." + name, "description": "eq." + description, "limit": "1"
                }, access_token=self.access_token)
                if existing:
                    self.status_label.text = "This exact level name and description already exists in the community. Change the text before uploading."
                    return
                payload = self._level_payload(name, description, category_input.text)
                self._api_request("POST", "/rest/v1/levels", payload, access_token=self.access_token, prefer="return=representation")
                popup.dismiss()
                self.status_label.text = "Verified level uploaded! Open Online Community to refresh and view it."
            except Exception as exc:
                self.status_label.text = ("Upload failed: " + str(exc))[:250]
        publish_btn = self._menu_button("VERIFY & PUBLISH", do_publish)
        cancel_btn = self._menu_button("Cancel", lambda *_: popup.dismiss())
        buttons.add_widget(publish_btn)
        buttons.add_widget(cancel_btn)
        content.add_widget(buttons)
        popup.open()

    def _skin_preferences_file(self):
        base = getattr(self, "user_data_dir", None) or os.path.join(os.path.expanduser("~"), ".2d_platformer")
        os.makedirs(base, exist_ok=True)
        return os.path.join(base, "skin_preferences.json")

    def _load_skin_preferences(self):
        settings = {"skin": "Green", "trail": "None", "sound": True, "theme": "Midnight",
                    "graphics_quality": "Balanced",
                    "unlocked_skins": ["Green"], "unlocked_trails": ["None"]}
        try:
            with open(self._skin_preferences_file(), "r", encoding="utf-8") as f:
                saved = json.load(f)
            if isinstance(saved, dict):
                settings.update(saved)
        except (OSError, ValueError, TypeError):
            pass
        if settings.get("theme") not in THEMES:
            settings["theme"] = "Midnight"
        if settings.get("graphics_quality") not in ("Low", "Balanced", "High"):
            settings["graphics_quality"] = "Balanced"
        if not isinstance(settings.get("unlocked_skins"), list):
            settings["unlocked_skins"] = ["Green"]
        if "Green" not in settings["unlocked_skins"]:
            settings["unlocked_skins"].append("Green")
        if settings.get("skin") not in settings["unlocked_skins"]:
            settings["skin"] = "Green"
        if not isinstance(settings.get("unlocked_trails"), list):
            settings["unlocked_trails"] = ["None"]
        if "None" not in settings["unlocked_trails"]:
            settings["unlocked_trails"].append("None")
        if settings.get("trail") not in settings["unlocked_trails"]:
            settings["trail"] = "None"
        return settings

    def _save_skin_preferences(self):
        path = self._skin_preferences_file()
        temp_path = path + ".tmp"
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            os.replace(temp_path, path)
            return True
        except (OSError, TypeError, ValueError):
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except OSError:
                pass
            return False

    def open_skins(self, *_):
        """Cosmetics shop: preview, buy, and equip player skins and movement trails."""
        page = self._simple_page("COSMETICS")
        data = self._load_progress_data()
        balance = max(0, int(data.get("currency_balance", 0)))
        displayed_skin = "Red (Admin)" if self._admin_allowed() else self.settings.get("skin", "Green")
        page.add_widget(Label(
            text=f"Wallet: {balance} Coins    Skin: {displayed_skin}    Trail: {self.settings.get('trail', 'None')}",
            font_size=19, size_hint_y=None, height=48, color=self._theme()["text"]))
        scroll = ScrollView(do_scroll_x=False, bar_width=8, scroll_type=["bars", "content"])
        items = BoxLayout(orientation="vertical", spacing=10, padding=(6, 8), size_hint_y=None)
        items.bind(minimum_height=items.setter("height"))
        items.add_widget(Label(text="PLAYER SKINS", font_size=25, bold=True,
                               size_hint_y=None, height=48, color=self._theme()["accent"]))
        skin_rows = [
            ("Green", 0, "Default", (0.2, 0.9, 0.3, 1)),
            ("Blue", 1000, "Ocean", (0.2, 0.55, 1.0, 1)),
            ("Purple", 5000, "Mystic", (0.7, 0.3, 1.0, 1)),
            ("Gold", 10000, "Royal", (1.0, 0.72, 0.12, 1)),
            ("Cyan", 15000, "Bright", (0.1, 0.9, 0.9, 1)),
            ("Orange", 20000, "Flame", (1.0, 0.42, 0.12, 1)),
            ("Pink", 25000, "Candy", (1.0, 0.28, 0.62, 1)),
            ("White", 30000, "Frost", (0.95, 0.95, 1.0, 1)),
        ]
        if self._admin_allowed():
            skin_rows.insert(2, ("Red", 0, "ADMIN ONLY", (1.0, 0.2, 0.2, 1)))
        unlocked = set(self.settings.get("unlocked_skins", ["Green"]))
        if self._admin_allowed():
            unlocked.add("Red")
        for skin, cost, subtitle, rgba in skin_rows:
            row = BoxLayout(orientation="horizontal", size_hint_y=None, height=112, spacing=12,
                            padding=(8, 4))
            preview = CosmeticPreview(kind="skin", name=skin, rgba=rgba,
                                      size_hint=(None, None), size=(112, 92))
            row.add_widget(preview)
            if skin in unlocked:
                state = ("ADMIN ONLY · ACTIVE" if skin == "Red" and self._admin_allowed()
                         else ("EQUIPPED" if self.settings.get("skin") == skin else "OWNED — EQUIP"))
                action = self._menu_button(f"{skin} · {subtitle}\n{state}",
                                           lambda *_, name=skin: self.set_skin(name))
            else:
                action = self._menu_button(f"{skin} · {subtitle}\nBUY · {cost} COINS",
                                           lambda *_, name=skin, price=cost: self.unlock_skin(name, price))
            row.add_widget(action)
            items.add_widget(row)

        items.add_widget(Label(text="PLAYER TRAILS", font_size=25, bold=True,
                               size_hint_y=None, height=52, color=self._theme()["accent"]))
        trail_rows = [
            ("None", 0, "Default", (0.8, 0.9, 1, 1), "○"),
            ("Spark", 800, "Bright sparks", (1.0, 0.9, 0.2, 1), "✦ ✦ ✦"),
            ("Flame", 1800, "Fire trail", (1.0, 0.35, 0.08, 1), "● ● ●"),
            ("Ice", 3000, "Frost trail", (0.2, 0.8, 1.0, 1), "◆ ◆ ◆"),
            ("Rainbow", 6000, "Color trail", (0.9, 0.3, 0.9, 1), "● ● ●"),
        ]
        owned_trails = set(self.settings.get("unlocked_trails", ["None"]))
        for trail, cost, subtitle, rgba, symbol in trail_rows:
            row = BoxLayout(orientation="horizontal", size_hint_y=None, height=112, spacing=12,
                            padding=(8, 4))
            preview = CosmeticPreview(kind="trail", name=trail, rgba=rgba,
                                      size_hint=(None, None), size=(112, 92))
            row.add_widget(preview)
            if trail in owned_trails:
                state = "EQUIPPED" if self.settings.get("trail", "None") == trail else "OWNED — EQUIP"
                action = self._menu_button(f"{trail} · {subtitle}\n{state}",
                                           lambda *_, name=trail: self.set_trail(name))
            else:
                action = self._menu_button(f"{trail} · {subtitle}\nBUY · {cost} COINS",
                                           lambda *_, name=trail, price=cost: self.unlock_trail(name, price))
            row.add_widget(action)
            items.add_widget(row)
        items.add_widget(self._menu_button("Back to Menu", self.show_main_menu))
        scroll.add_widget(items)
        page.add_widget(scroll)
        self._replace_screen(page)

    def _purchase_cosmetic(self, item, cost, kind):
        if kind == "skin" and item == "Red":
            if not self._admin_allowed():
                self.status_label.text = "The red player is reserved for the admin account."
                return
            # Admin red is a built-in account perk, not a purchasable skin.
            self.settings["skin"] = "Red"
            self.settings["unlocked_skins"] = sorted(set(self.settings.get("unlocked_skins", ["Green"])) | {"Red"})
            self._save_skin_preferences()
            self.status_label.text = "Admin red player equipped."
            canvas = getattr(self, "editor_canvas", None)
            if canvas is not None:
                canvas.redraw()
            self.open_skins()
            return
        if kind == "skin":
            valid = {"Green": 0, "Blue": 1000, "Red": 2500, "Purple": 5000,
                     "Gold": 10000, "Cyan": 15000, "Orange": 20000,
                     "Pink": 25000, "White": 30000}
            owned_key = "unlocked_skins"
            equipped_key = "skin"
        else:
            valid = {"None": 0, "Spark": 800, "Flame": 1800, "Ice": 3000, "Rainbow": 6000}
            owned_key = "unlocked_trails"
            equipped_key = "trail"
        if item not in valid or valid[item] != int(cost):
            self.status_label.text = "Invalid cosmetic purchase."
            return
        owned = set(self.settings.get(owned_key, ["Green"] if kind == "skin" else ["None"]))
        data = None
        old_settings = dict(self.settings)
        if item not in owned:
            data = self._load_progress_data()
            balance = max(0, int(data.get("currency_balance", 0)))
            if balance < cost:
                self.status_label.text = f"Need {cost - balance} more Coins to unlock {item}."
                return
            owned.add(item)
            self.settings[owned_key] = sorted(owned)
        self.settings[equipped_key] = item
        # Persist ownership/equipment first; only then charge the wallet. If the
        # wallet write fails, restore the previous cosmetic settings.
        if not self._save_skin_preferences():
            self.settings = old_settings
            self.status_label.text = "Cosmetic setting could not be saved. Please try again."
            return
        if data is not None:
            data["currency_balance"] = balance - int(cost)
            if not self._save_progress_data(data):
                self.settings = old_settings
                self._save_skin_preferences()
                self.status_label.text = "Purchase could not be saved. No coins were charged."
                return
        self.status_label.text = f"{item} {kind} equipped!"
        canvas = getattr(self, "editor_canvas", None)
        if canvas is not None:
            canvas.redraw()
        self.open_skins()

    def unlock_skin(self, skin, cost):
        self._purchase_cosmetic(skin, cost, "skin")

    def set_skin(self, skin):
        costs = {"Green": 0, "Blue": 1000, "Red": 2500, "Purple": 5000,
                 "Gold": 10000, "Cyan": 15000, "Orange": 20000,
                 "Pink": 25000, "White": 30000}
        self._purchase_cosmetic(skin, costs.get(skin, -1), "skin")

    def unlock_trail(self, trail, cost):
        self._purchase_cosmetic(trail, cost, "trail")

    def set_trail(self, trail):
        costs = {"None": 0, "Spark": 800, "Flame": 1800, "Ice": 3000, "Rainbow": 6000}
        self._purchase_cosmetic(trail, costs.get(trail, -1), "trail")

    def open_settings(self, *_):
        # Keep the established settings layout for compatibility with the
        # existing Android/Pydroid Kivy UI.
        page = self._simple_page("SETTINGS", back=False)
        page.add_widget(Label(text="Personalize your game and manage your cloud account.", font_size=18,
                              color=self._theme()["text"], size_hint_y=None, height=38))
        scroll = ScrollView(do_scroll_x=False, bar_width=8, scroll_type=["bars", "content"])
        items = BoxLayout(orientation="vertical", spacing=12, padding=(4, 6), size_hint_y=None)
        items.bind(minimum_height=items.setter("height"))
        self.graphics_quality_btn = self._menu_button(
            "Graphics Quality: " + self.settings.get("graphics_quality", "Balanced") + "  •  Change",
            self.cycle_graphics_quality)
        items.add_widget(self.graphics_quality_btn)
        items.add_widget(self._menu_button("Main Menu Theme: " + self.settings.get("theme", "Midnight") + "  •  Change", self.cycle_theme))
        items.add_widget(self._menu_button("Sound: " + ("On" if self.settings.get("sound", True) else "Off"), self.toggle_sound_setting))
        items.add_widget(self._menu_button("REGISTER / LOGIN", self.open_auth_menu))
        items.add_widget(self._menu_button("SAVE ALL LEVELS & PROGRESS TO CLOUD", self.save_all_to_cloud))
        items.add_widget(self._menu_button("LOAD LEVELS & PROGRESS FROM CLOUD", self.load_all_from_cloud))
        if self.access_token:
            items.add_widget(self._menu_button("DELETE ACCOUNT PERMANENTLY", self.open_delete_account_confirmation))
            items.add_widget(self._menu_button("Log Out", self.logout))
        items.add_widget(self._menu_button("Back to Main Menu", self.show_main_menu))
        scroll.add_widget(items)
        page.add_widget(scroll)
        self._replace_screen(page)

    def cycle_graphics_quality(self, *_):
        levels = ("Low", "Balanced", "High")
        current = self.settings.get("graphics_quality", "Balanced")
        if current not in levels:
            current = "Balanced"
        self.settings["graphics_quality"] = levels[(levels.index(current) + 1) % len(levels)]
        self._save_skin_preferences()
        button = getattr(self, "graphics_quality_btn", None)
        if button is not None:
            button.text = "Graphics Quality: " + self.settings["graphics_quality"] + "  •  Change"
        canvas = getattr(self, "editor_canvas", None)
        if canvas is not None:
            Clock.schedule_once(lambda _dt, target=canvas: target.redraw(), 0)

    def toggle_sound_setting(self, *_):
        self.settings["sound"] = not self.settings.get("sound", True)
        self.open_settings()

    def open_delete_account_confirmation(self, *_):
        if not self.access_token or not (self.current_user or {}).get("id"):
            self._cloud_status("Log in to the account you want to delete.")
            return
        content = BoxLayout(orientation="vertical", padding=16, spacing=12)
        message = Label(
            text=("Permanently delete your 2D Platformer account and its online data?\n\n"
                  "This removes your online account, cloud backups, and account-owned online data.\n"
                  "This cannot be undone. Offline levels already saved on this device will remain."),
            font_size=17, halign="center", valign="middle")
        message.bind(size=lambda widget, *_: setattr(widget, "text_size", (widget.width - 20, None)))
        content.add_widget(message)
        buttons = BoxLayout(size_hint_y=None, height=58, spacing=10)
        popup = Popup(title="Delete Account Permanently", content=content, size_hint=(0.92, 0.55), auto_dismiss=False)
        def confirm_delete(*_):
            popup.dismiss()
            self._delete_account_now()
        delete_button = self._menu_button("DELETE ACCOUNT", confirm_delete)
        delete_button.height = 54
        delete_button.font_size = 16
        cancel_button = self._menu_button("Cancel", popup.dismiss)
        cancel_button.height = 54
        cancel_button.font_size = 16
        buttons.add_widget(delete_button)
        buttons.add_widget(cancel_button)
        content.add_widget(buttons)
        popup.open()

    def _delete_account_now(self):
        """Delete the signed-in user through a trusted Supabase Edge Function.

        The service-role key must exist only in the Edge Function's server secrets,
        never in this Python/Android client.
        """
        if not self.access_token:
            self._cloud_status("Log in again before deleting your account.")
            return
        try:
            result = self._api_request(
                "POST", "/functions/v1/delete-account", {}, access_token=self.access_token
            )
            if isinstance(result, dict) and result.get("error"):
                raise RuntimeError(str(result.get("error")))
            self._clear_auth_session()
            self.current_user = None
            self.access_token = None
            self.current_email = ""
            self.current_username = "Guest"
            self._cloud_status("Your account was deleted. Offline levels on this device remain available.")
            self.show_main_menu()
        except Exception as exc:
            self._cloud_status("Account deletion failed. Check internet or deploy the delete-account function: " + str(exc)[:170])

    def logout(self, *_):
        self._clear_auth_session()
        self.current_user = None
        self.access_token = None
        self.current_email = ""
        self.current_username = "Guest"
        self.show_main_menu()

    def _install_eight_builtin_levels(self, folder):
        """Install eight playable starter packs using the game's native stage-pack format."""
        templates = {int(item["id"]): item for item in OBJECTS_DATA}

        def obj(oid, length=None, **extra):
            value = copy.deepcopy(templates[oid])
            if length:
                value["length"] = length
            value.update(extra)
            return value

        # Coordinates deliberately match Tutorial.json: row 0 is the floor and
        # playable geometry stays in rows 0-8 (the visible playfield area).
        designs = [
            {"name":"01 - First Steps", "description":"Learn the route with gentle raised platforms, coins and a checkpoint.",
             "platforms":[(0,31,0),(4,7,2),(10,13,3),(17,20,2),(24,27,3)],
             "coins":[(2,1),(5,3),(7,3),(11,4),(13,4),(18,3),(20,3),(25,4),(27,4)], "gems":[(19,4)], "checkpoints":[(16,1)], "hazards":[], "extras":[]},
            {"name":"02 - Coin Trail", "description":"Follow a trail of coins across a series of safe stepping platforms.",
             "platforms":[(0,5,0),(8,12,0),(15,19,0),(22,26,0),(29,31,0),(3,6,2),(10,13,3),(17,20,2),(24,28,3)],
             "coins":[(1,1),(3,3),(5,3),(9,1),(11,4),(13,4),(16,1),(18,3),(20,3),(23,1),(25,4),(27,4),(30,1)], "gems":[(12,5),(26,5)], "checkpoints":[(21,1)], "hazards":[], "extras":[]},
            {"name":"03 - The Secret Path", "description":"Choose the lower safe route or climb to a hidden treasure path.",
             "platforms":[(0,31,0),(3,8,2),(11,15,2),(18,22,2),(25,29,2),(7,10,5),(13,17,6),(20,24,5)],
             "coins":[(4,3),(6,3),(12,3),(15,7),(17,7),(21,6),(23,6),(27,3)], "gems":[(9,6),(16,8),(22,7)], "checkpoints":[(18,3)], "hazards":[], "extras":[(42,8,7),(42,14,8),(42,21,7)]},
            {"name":"04 - Moving Mayhem", "description":"Ride moving platforms and time your jumps between stable ground.",
             "platforms":[(0,4,0),(9,13,0),(18,22,0),(27,31,0),(5,8,2),(14,17,3),(23,26,2)],
             "coins":[(2,1),(6,3),(11,1),(15,4),(20,1),(24,3),(29,1)], "gems":[(16,5)], "checkpoints":[(18,1)], "hazards":[], "extras":[(4,6,3),(4,15,4),(4,24,3)]},
            {"name":"05 - Don't Touch!", "description":"Avoid spikes and saws while using raised safe platforms.",
             "platforms":[(0,31,0),(4,8,2),(11,15,2),(18,22,2),(25,29,2)],
             "coins":[(2,1),(5,3),(7,3),(12,3),(14,3),(19,3),(21,3),(26,3),(28,3)], "gems":[(20,4)], "checkpoints":[(16,1)], "hazards":[(2,9,1),(2,16,1),(3,23,1)], "extras":[]},
            {"name":"06 - The Checkpoint Run", "description":"A longer route with checkpoints, breakable blocks and moving platforms.",
             "platforms":[(0,6,0),(9,14,0),(17,22,0),(25,31,0),(4,7,2),(11,14,3),(19,22,2),(27,30,3)],
             "coins":[(2,1),(5,3),(10,1),(12,4),(18,1),(20,3),(26,1),(29,4)], "gems":[(13,5),(28,5)], "checkpoints":[(8,1),(24,1)], "hazards":[], "extras":[(20,7,2),(4,15,3)]},
            {"name":"07 - The Forgotten Temple", "description":"Explore the temple, collect the key and unlock the door at the end.",
             "platforms":[(0,31,0),(3,7,2),(10,14,3),(17,21,2),(24,29,3)],
             "coins":[(2,1),(4,3),(6,3),(11,4),(13,4),(18,3),(20,3),(25,4),(28,4)], "gems":[(8,4),(19,4),(27,5)], "checkpoints":[(16,1)], "hazards":[(2,8,1),(3,22,1)], "extras":[(8,12,3),(9,29,1)]},
            {"name":"08 - Final Escape", "description":"The final challenge combines gaps, moving platforms, hazards and treasure.",
             "platforms":[(0,5,0),(9,13,0),(17,21,0),(25,31,0),(3,6,2),(10,14,3),(18,22,2),(26,30,3)],
             "coins":[(1,1),(4,3),(6,3),(10,1),(12,4),(18,1),(20,3),(26,1),(29,4)], "gems":[(13,5),(21,4),(28,5)], "checkpoints":[(8,1),(24,1)], "hazards":[(2,7,1),(2,15,1),(3,23,1)], "extras":[(4,6,3),(4,14,4),(4,22,3)]},
        ]

        for design in designs:
            filename = design["name"] + ".json"
            path = os.path.join(folder, filename)
            # Regenerate only files previously created by this installer. Never
            # overwrite a player's own level, even if it has a matching filename.
            if os.path.isfile(path):
                try:
                    with open(path, "r", encoding="utf-8") as existing_file:
                        existing = json.load(existing_file)
                    if existing.get("format") not in ("adnanzamangames_builtin_level", "neon_arcade_stage_pack"):
                        continue
                except Exception:
                    continue

            records = []
            occupied = set()
            def put(col, row, value):
                col, row = int(col), int(row)
                if not (0 <= col < 32 and 0 <= row < 20):
                    return
                # A tile can hold only one solid/interactive item in these starter levels.
                if (col, row) in occupied:
                    return
                occupied.add((col, row))
                records.append({"col": col, "row": row, "object": copy.deepcopy(value)})

            for left, right, row in design["platforms"]:
                for col in range(left, right + 1):
                    put(col, row, obj(1))
            for col, row in design["coins"]:
                put(col, row, obj(6))
            for col, row in design["gems"]:
                put(col, row, obj(7))
            for col, row in design["checkpoints"]:
                put(col, row, obj(5))
            for oid, col, row in design["hazards"]:
                put(col, row, obj(oid))
            for oid, col, row in design["extras"]:
                put(col, row, obj(oid, "3 Tiles W x 1 Tile L" if oid in (4, 42) else None))

            # _apply_level_data() supports the native multi-stage structure used
            # by Tutorial.json. Keeping that exact shape avoids empty level loads.
            payload = {
                "format": "neon_arcade_stage_pack", "version": 2,
                "cols": 32, "rows": 20,
                "stages": [{"name": design["name"], "level": {"objects": records}}],
            }
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2)

    def _builtin_levels_directory(self):
        """
        Return a writable offline-level folder and install bundled JSON levels.

        Buildozer packages JSON files from the project when ``json`` is included
        in source.include_exts. On first launch, copy Tutorial.json (if it is
        beside main.py) and JSON files inside the bundled offline_levels folder
        into app-private storage. This makes them available in the APK and
        playable offline. Existing player/admin copies are never overwritten.
        """
        folder = os.path.join(self.user_data_dir, "offline_levels")
        os.makedirs(folder, exist_ok=True)

        try:
            source_dir = os.path.dirname(os.path.abspath(__file__))
        except Exception:
            source_dir = os.getcwd()

        bundled_dirs = [
            os.path.join(source_dir, "offline_levels"),
            source_dir,
        ]

        # Also import files from the older shared-storage location when
        # Android allows access. The game no longer depends on that location.
        legacy_external = "/storage/emulated/0/2D_Platformer/offline_levels"
        bundled_dirs.append(legacy_external)

        for source_folder in bundled_dirs:
            if not os.path.isdir(source_folder):
                continue
            try:
                for filename in os.listdir(source_folder):
                    if not filename.lower().endswith(".json"):
                        continue
                    # Only take root-level Tutorial.json from the project root;
                    # other root JSON files may be unrelated configuration data.
                    if os.path.abspath(source_folder) == os.path.abspath(source_dir):
                        if filename.lower() != "tutorial.json":
                            continue
                    source_path = os.path.join(source_folder, filename)
                    destination_path = os.path.join(folder, filename)
                    if not os.path.isfile(destination_path):
                        try:
                            shutil.copy2(source_path, destination_path)
                        except OSError:
                            # Read-only bundled assets can still be opened from
                            # their original folder if copying is unavailable.
                            pass
            except (OSError, PermissionError):
                continue

        # Do not auto-generate starter/campaign levels. The offline player
        # menu is intentionally limited to the creator's Tutorial.json.
        return folder

    def open_builtin_admin_editor(self, *_):
        if not self._admin_allowed():
            self.status_label.text = "Admin access denied. Log in with the owner account."
            return
        self._builtin_editor_mode = True
        page = self._simple_page("Built-in Levels - Admin Editor")
        page.add_widget(Label(text="These levels are stored on this device and can be played offline. Only the owner account can create or edit them.",
                              font_size=15, size_hint_y=None, height=66))
        page.add_widget(self._menu_button("Create New Built-in Level Pack (Stages)", self.create_builtin_level))
        page.add_widget(self._menu_button("Upload JSON", self.upload_builtin_json))
        page.add_widget(self._menu_button("Manage / Edit Built-in Level Packs", self.manage_builtin_levels))
        page.add_widget(self._menu_button("Back to Admin Panel", self.open_admin_menu))
        self._replace_screen(page)

    def create_builtin_level(self, *_):
        if not self._admin_allowed():
            return
        self._builtin_editor_mode = True
        self._builtin_current_filename = ""
        self.stages = [{"name": "Stage 1", "objects": {}, "background": "Default"}]
        self.current_stage_index = 0
        self._community_play_mode = False
        self._builtin_play_mode = False
        self.editor_canvas.grid_data = {}
        self.editor_canvas.selected_key = None
        self.editor_canvas.active_spawn = None
        self.editor_canvas.reset_controls()
        self.editor_canvas.redraw()
        self.open_editor()
        self.status_label.text = "BUILT-IN EDITOR - place objects, then Save"

    def manage_builtin_levels(self, *_):
        if not self._admin_allowed():
            return
        folder = self._builtin_levels_directory()
        files = sorted(f for f in os.listdir(folder) if f.lower().endswith(".json"))
        page = self._simple_page("Manage Built-in Levels")
        if not files:
            page.add_widget(Label(text="No built-in levels yet. Create one in the admin editor.", font_size=16))
        scroll = ScrollView()
        listing = GridLayout(cols=1, spacing=7, size_hint_y=None, padding=4)
        listing.bind(minimum_height=listing.setter("height"))
        for filename in files:
            row = BoxLayout(size_hint_y=None, height=54, spacing=6)
            try:
                pack_data = self._read_builtin_level(filename)
                stage_count = len(pack_data.get("stages", [])) or 1
            except Exception:
                stage_count = 1
            row.add_widget(Label(text=f"{filename[:-5]} ({stage_count} stage{'s' if stage_count != 1 else ''})", font_size=15))
            edit_btn = self._menu_button("EDIT", lambda *_a, f=filename: self.edit_builtin_level(f))
            play_btn = self._menu_button("PLAY OFFLINE", lambda *_a, f=filename: self.play_builtin_level(f))
            delete_btn = self._menu_button("DELETE", lambda *_a, f=filename: self.delete_builtin_level(f))
            row.add_widget(edit_btn); row.add_widget(play_btn); row.add_widget(delete_btn)
            listing.add_widget(row)
        scroll.add_widget(listing)
        page.add_widget(scroll)
        page.add_widget(self._menu_button("UPLOAD JSON", self.upload_builtin_json))
        page.add_widget(self._menu_button("Back to Built-in Editor", self.open_builtin_admin_editor))
        self._replace_screen(page)

    def _validate_builtin_json_data(self, data):
        """Validate a native single-level or multi-stage JSON pack before importing."""
        if not isinstance(data, dict):
            raise ValueError("The JSON root must be an object.")
        raw_stages = data.get("stages")
        if isinstance(raw_stages, list) and raw_stages:
            stage_items = []
            for index, stage in enumerate(raw_stages):
                if not isinstance(stage, dict):
                    raise ValueError(f"Stage {index + 1} is not an object.")
                stage_data = stage.get("level", stage)
                if not isinstance(stage_data, dict) or not isinstance(stage_data.get("objects", []), list):
                    raise ValueError(f"Stage {index + 1} has no valid objects list.")
                stage_items.extend(stage_data.get("objects", []))
        else:
            if not isinstance(data.get("objects"), list):
                raise ValueError("This file has neither a stages list nor an objects list.")
            stage_items = data.get("objects", [])
        for index, item in enumerate(stage_items):
            if not isinstance(item, dict) or not isinstance(item.get("object"), dict):
                raise ValueError(f"Object record {index + 1} is invalid.")
            try:
                col, row = int(item["col"]), int(item["row"])
                oid = int(item["object"]["id"])
            except (KeyError, TypeError, ValueError):
                raise ValueError(f"Object record {index + 1} needs col, row and object.id.")
            if not (0 <= col < 32 and 0 <= row < 20):
                raise ValueError(f"Object record {index + 1} is outside the 32x20 grid.")
            if oid not in {int(obj["id"]) for obj in OBJECTS_DATA}:
                raise ValueError(f"Object record {index + 1} uses unknown object ID {oid}.")
        return True

    def upload_builtin_json(self, *_):
        """Let the owner select a JSON file and import it into offline_levels."""
        if not self._admin_allowed():
            self.status_label.text = "Admin access denied. Log in with the owner account."
            return
        start_path = "/storage/emulated/0/Download"
        if not os.path.isdir(start_path):
            start_path = "/storage/emulated/0" if os.path.isdir("/storage/emulated/0") else os.path.expanduser("~")
        content = BoxLayout(orientation="vertical", padding=8, spacing=6)
        chooser = FileChooserListView(path=start_path, filters=["*.json"], size_hint_y=1)
        content.add_widget(chooser)
        hint = Label(text="Choose a .json level file, then tap Import.", size_hint_y=None, height=30)
        content.add_widget(hint)
        buttons = BoxLayout(size_hint_y=None, height=46, spacing=8)
        popup = Popup(title="Upload JSON to Built-in Levels", content=content, size_hint=(0.94, 0.9))
        def do_import(*_a):
            if not chooser.selection:
                hint.text = "Select a JSON file first."
                return
            source = chooser.selection[0]
            try:
                if not source.lower().endswith(".json") or not os.path.isfile(source):
                    raise ValueError("Please select a .json file.")
                with open(source, "r", encoding="utf-8") as handle:
                    data = json.load(handle)
                self._validate_builtin_json_data(data)
                folder = self._builtin_levels_directory()
                base = re.sub(r"[^A-Za-z0-9 _-]", "_", os.path.splitext(os.path.basename(source))[0]).strip(" ._") or "Imported_Level"
                filename = base + ".json"
                target = os.path.join(folder, filename)
                counter = 2
                while os.path.exists(target):
                    filename = f"{base} ({counter}).json"
                    target = os.path.join(folder, filename)
                    counter += 1
                # Re-serialize validated JSON so the imported file is UTF-8 and readable.
                with open(target, "w", encoding="utf-8") as handle:
                    json.dump(data, handle, ensure_ascii=False, indent=2)
                popup.dismiss()
                self.status_label.text = "Imported built-in level: " + filename
                self.manage_builtin_levels()
            except Exception as exc:
                hint.text = ("Import failed: " + str(exc))[:220]
        import_btn = Button(text="IMPORT JSON")
        cancel_btn = Button(text="CANCEL")
        import_btn.bind(on_press=do_import)
        cancel_btn.bind(on_press=popup.dismiss)
        buttons.add_widget(import_btn); buttons.add_widget(cancel_btn)
        content.add_widget(buttons)
        popup.open()

    def _read_builtin_level(self, filename):
        safe = os.path.basename(filename)
        if not safe.lower().endswith(".json"):
            raise ValueError("Invalid built-in level file")
        with open(os.path.join(self._builtin_levels_directory(), safe), "r", encoding="utf-8") as f:
            return json.load(f)

    def _objects_from_level_data(self, data):
        new_grid = {}
        seen_exact_objects = set()
        for item in data.get("objects", []):
            try:
                col, row = int(item["col"]), int(item["row"])
                obj = item.get("object")
                if 0 <= col < self.editor_canvas.cols and 0 <= row < self.editor_canvas.rows and isinstance(obj, dict):
                    # Older saved packs may repeat the exact same object record
                    # at the same tile. Drawing/colliding with identical duplicates
                    # wastes frame time and can multiply collectible rewards. Keep
                    # genuinely different objects and differently configured props.
                    signature = (col, row, json.dumps(obj, sort_keys=True, ensure_ascii=False))
                    if signature in seen_exact_objects:
                        continue
                    seen_exact_objects.add(signature)
                    key = (col, row)
                    if key in new_grid:
                        serial = 1
                        while (col, row, serial) in new_grid:
                            serial += 1
                        key = (col, row, serial)
                    new_grid[key] = copy.deepcopy(obj)
            except (KeyError, TypeError, ValueError):
                continue
        return new_grid

    def _level_data_from_objects(self, objects):
        return {"objects": [{"col": int(k[0]), "row": int(k[1]), "object": o}
                            for k, o in objects.items()]}

    def _apply_level_data(self, data):
        # Backward compatible: old single-level JSONs still load as one-stage packs.
        raw_stages = data.get("stages") if isinstance(data, dict) else None
        if isinstance(raw_stages, list) and raw_stages:
            stages = []
            for i, stage in enumerate(raw_stages):
                if not isinstance(stage, dict):
                    continue
                stage_data = stage.get("level", stage)
                stages.append({"name": str(stage.get("name") or f"Stage {i + 1}"),
                               "objects": self._objects_from_level_data(stage_data),
                               "background": str(stage.get("background") or "Default")})
            self.stages = stages or [{"name": "Stage 1", "objects": {}}]
        else:
            self.stages = [{"name": str(data.get("name") or "Stage 1"),
                            "objects": self._objects_from_level_data(data),
                            "background": str(data.get("background") or "Default")}]
        self.current_stage_index = 0
        self.editor_canvas.grid_data = self.stages[0]["objects"]
        # grid_data was replaced wholesale; rebuild ID, dimensions and spatial
        # indexes before the editor's first redraw (otherwise a stale empty
        # index can make the editor look blank while Play reloads the stage).
        self.editor_canvas._runtime_index_dirty = True
        self.editor_canvas._render_stage_index = self.current_stage_index
        self.editor_canvas._all_object_items = ()
        self.editor_canvas._spatial_buckets = {}
        self.editor_canvas.selected_key = None
        self.editor_canvas.active_spawn = None
        self.editor_canvas.reset_controls()
        self.editor_canvas.redraw()
        Clock.schedule_once(lambda _dt: self.editor_canvas.redraw(), 0)

    def _serialize_stage_pack(self):
        self._sync_current_stage()
        return {"format": "neon_arcade_stage_pack", "version": 2,
                "cols": self.editor_canvas.cols, "rows": self.editor_canvas.rows,
                "stages": [{"name": stage.get("name", f"Stage {i + 1}"),
                            "background": stage.get("background", "Default"),
                            "level": self._level_data_from_objects(stage.get("objects", {}))}
                           for i, stage in enumerate(self.stages)]}

    def edit_builtin_level(self, filename):
        if not self._admin_allowed():
            return
        try:
            self._apply_level_data(self._read_builtin_level(filename))
            self._builtin_editor_mode = True
            self._builtin_current_filename = os.path.basename(filename)
            self.open_editor()
            self.status_label.text = "EDITING BUILT-IN: " + filename[:-5]
        except Exception as exc:
            self.admin_status.text = ("Could not load built-in level: " + str(exc))[:250]

    def play_builtin_level(self, filename):
        try:
            self._apply_level_data(self._read_builtin_level(filename))
            self._builtin_play_mode = True
            self._community_play_mode = False
            self._builtin_editor_mode = False
            self._builtin_current_filename = os.path.basename(filename)
            self.open_editor()
            self.toggle_play_mode()
            self.status_label.text = "OFFLINE BUILT-IN LEVEL: " + filename[:-5]
        except Exception as exc:
            self.admin_status.text = ("Could not start offline level: " + str(exc))[:250] if hasattr(self, "admin_status") else str(exc)[:250]

    def delete_builtin_level(self, filename):
        if not self._admin_allowed():
            return
        try:
            os.remove(os.path.join(self._builtin_levels_directory(), os.path.basename(filename)))
            self.manage_builtin_levels()
        except Exception as exc:
            self.status_label.text = ("Delete failed: " + str(exc))[:250]

    def open_admin_menu(self, *_):
        """In-editor admin page. Database RLS policies must still enforce admin permissions."""
        if not self.access_token or not self.current_user:
            self.status_label.text = "Admin: log in first from the main menu."
            return
        if (self.current_email or "").strip().lower() != "adnanzamanador@gmail.com":
            self.status_label.text = "Admin access denied for this account."
            return
        page = self._simple_page("Admin Panel")
        page.add_widget(Label(text="Signed in as owner. Manage players, community levels, and reports below.", font_size=16,
                              size_hint_y=None, height=38))
        page.add_widget(self._menu_button("BUILT-IN LEVEL EDITOR (ADMIN ONLY)", self.open_builtin_admin_editor))
        page.add_widget(self._menu_button("Manage Community Levels", self.refresh_admin_levels))
        page.add_widget(self._menu_button("Add Rating / Set Level Difficulty", self.open_admin_difficulty))
        page.add_widget(self._menu_button("Manage Players (ban / balance)", self.open_admin_players))
        page.add_widget(self._menu_button("Level Reports", self.open_admin_reports))
        page.add_widget(self._menu_button("Report a Level", self.report_level_prompt))
        self.admin_levels_list = GridLayout(cols=1, spacing=6, size_hint_y=None)
        self.admin_levels_list.bind(minimum_height=self.admin_levels_list.setter("height"))
        scroll = ScrollView()
        scroll.add_widget(self.admin_levels_list)
        page.add_widget(scroll)
        self.admin_status = Label(text="Tap Refresh / Manage Levels to load community levels.",
                                  font_size=14, size_hint_y=None, height=42)
        page.add_widget(self.admin_status)
        page.add_widget(self._menu_button("Back to Editor", self.open_editor))
        self._replace_screen(page)

    DIFFICULTY_LEVELS = ("Easy", "Medium", "Difficult", "Extreme Difficult")

    def open_admin_difficulty(self, *_):
        if not self._admin_allowed():
            self.status_label.text = "Admin access denied. Log in with the owner account."
            return
        page = self._simple_page("Add Rating / Set Difficulty", back=False)
        page.add_widget(Label(text="Difficulty is admin-only. New community levels default to Easy. Player star ratings are separate.",
                              size_hint_y=None, height=52, font_size=14))
        status = Label(text="Loading levels...", size_hint_y=None, height=40, font_size=13)
        page.add_widget(status)
        listing = GridLayout(cols=1, spacing=8, padding=4, size_hint_y=None)
        listing.bind(minimum_height=listing.setter("height"))
        scroll = ScrollView(do_scroll_x=False); scroll.add_widget(listing); page.add_widget(scroll)
        page.add_widget(self._menu_button("Refresh", lambda *_: self._load_admin_difficulty_rows(status, listing)))
        page.add_widget(self._menu_button("Back to Admin Panel", self.open_admin_menu))
        self._replace_screen(page)
        Clock.schedule_once(lambda _dt: self._load_admin_difficulty_rows(status, listing), 0.05)

    def _load_admin_difficulty_rows(self, status, listing):
        listing.clear_widgets()
        try:
            result = self._leaderboard_request({"action": "admin_list_levels"})
            rows = result.get("rows", [])
            if not rows:
                status.text = "No community or approved built-in leaderboard levels were found."
                return
            for item in rows:
                box = BoxLayout(orientation="vertical", size_hint_y=None, height=112, spacing=5, padding=6)
                label = Label(text=f"{item.get('level_name') or item.get('name') or 'Level'}  [{item.get('type','level')}]\nCurrent: {item.get('difficulty') or 'Easy'}",
                              font_size=14, halign="left", valign="middle", size_hint_y=None, height=42)
                label.bind(size=lambda inst, val: setattr(inst, "text_size", val))
                box.add_widget(label)
                controls = BoxLayout(size_hint_y=None, height=48, spacing=6)
                spinner = Spinner(text=item.get("difficulty") if item.get("difficulty") in self.DIFFICULTY_LEVELS else "Easy",
                                  values=self.DIFFICULTY_LEVELS, size_hint_x=0.62, font_size=14)
                controls.add_widget(spinner)
                def save(*_a, it=item, sp=spinner, lab=label):
                    try:
                        response = self._leaderboard_request({"action": "admin_set_difficulty", "level_type": it.get("type"),
                                                              "level_id": it.get("id"), "level_key": it.get("level_key"),
                                                              "difficulty": sp.text})
                        lab.text = f"{it.get('level_name') or it.get('name') or 'Level'}  [{it.get('type','level')}]\nCurrent: {response.get('difficulty', sp.text)}"
                        status.text = "Difficulty updated. Orbs are awarded only on a player's first approved completion."
                    except Exception as exc:
                        status.text = ("Update failed: " + str(exc))[:220]
                controls.add_widget(self._menu_button("SAVE", save))
                box.add_widget(controls); listing.add_widget(box)
            status.text = f"Loaded {len(rows)} level(s). Only this admin account can change difficulty."
        except Exception as exc:
            status.text = ("Could not load levels: " + str(exc))[:240]

    def _admin_allowed(self):
        return bool(self.access_token and self.current_user and
                    (self.current_email or "").strip().lower() == "adnanzamanador@gmail.com")

    def _admin_simple_list(self, title, table, select_fields, row_text, actions=None):
        if not self._admin_allowed():
            self.status_label.text = "Admin access denied. Log in with the owner account."
            return
        page = self._simple_page(title, back=False)
        page.add_widget(self._menu_button("Refresh", lambda *_: self._admin_simple_list(title, table, select_fields, row_text, actions)))
        listing = GridLayout(cols=1, spacing=6, size_hint_y=None)
        listing.bind(minimum_height=listing.setter("height"))
        scroll = ScrollView()
        scroll.add_widget(listing)
        page.add_widget(scroll)
        status = Label(text="Loading...", size_hint_y=None, height=42, font_size=13)
        page.add_widget(status)
        page.add_widget(self._menu_button("Back to Admin Panel", self.open_admin_menu))
        self._replace_screen(page)
        try:
            rows = self._api_request("GET", "/rest/v1/" + table, params={"select": select_fields, "order": "created_at.desc", "limit": "100"}, access_token=self.access_token)
            for item in rows:
                box = BoxLayout(orientation="vertical", size_hint_y=None, height=92, spacing=3)
                label = Label(text=row_text(item), font_size=13, halign="left", valign="middle")
                label.bind(size=lambda inst, val: setattr(inst, "text_size", val))
                box.add_widget(label)
                if actions:
                    actions(box, item, status)
                listing.add_widget(box)
            status.text = f"Loaded {len(rows)} row(s) from {table}."
        except Exception as exc:
            status.text = (f"Could not load {table}: {exc}. Check table/column names and RLS policies.")[:350]

    def open_admin_players(self, *_):
        if not self._admin_allowed():
            self.status_label.text = "Admin access denied."
            return
        page = self._simple_page("Manage Players", back=False)
        page.add_widget(Label(text="This page expects a public profiles table with id, username, balance, is_banned, created_at. If your schema differs, the error below will explain it.", font_size=13, size_hint_y=None, height=62))
        listing = GridLayout(cols=1, spacing=6, size_hint_y=None)
        listing.bind(minimum_height=listing.setter("height"))
        scroll = ScrollView(); scroll.add_widget(listing); page.add_widget(scroll)
        status = Label(text="Loading players...", font_size=13, size_hint_y=None, height=48)
        page.add_widget(status)
        page.add_widget(self._menu_button("Back to Admin Panel", self.open_admin_menu))
        self._replace_screen(page)
        try:
            rows = self._api_request("GET", "/rest/v1/profiles", params={"select":"id,username,balance,is_banned,created_at", "order":"created_at.desc", "limit":"100"}, access_token=self.access_token)
            for player in rows:
                row = BoxLayout(orientation="vertical", size_hint_y=None, height=118, spacing=3)
                row.add_widget(Label(text=f"{player.get('username','Player')} | balance: {player.get('balance','?')} | banned: {player.get('is_banned','?')}\nUID: {player.get('id','')}", font_size=12))
                controls = BoxLayout(size_hint_y=None, height=42, spacing=5)
                controls.add_widget(self._menu_button("Edit balance", lambda *_a, pl=player: self.admin_edit_balance(pl)))
                controls.add_widget(self._menu_button("Ban / Unban", lambda *_a, pl=player: self.admin_toggle_ban(pl)))
                row.add_widget(controls); listing.add_widget(row)
            status.text = f"Loaded {len(rows)} players."
        except Exception as exc:
            status.text = (f"Players unavailable: {exc}. Configure the profiles table and admin-only RLS/RPC.")[:350]

    def admin_edit_balance(self, player):
        if not self._admin_allowed(): return
        content = BoxLayout(orientation="vertical", padding=10, spacing=8)
        amount = TextInput(text=str(player.get("balance", 0)), hint_text="New balance", multiline=False, input_filter="float", size_hint_y=None, height=64, padding=(14, 16), font_size=20)
        content.add_widget(Label(text="Set the player's new balance", size_hint_y=None, height=35)); content.add_widget(amount)
        buttons = BoxLayout(size_hint_y=None, height=48, spacing=8)
        popup = Popup(title="Edit Balance", content=content, size_hint=(0.9, 0.38))
        def save(*_):
            try:
                value = float(amount.text)
                if value < 0: raise ValueError("Balance cannot be negative")
                self._api_request("PATCH", "/rest/v1/profiles", {"balance": value}, params={"id":"eq."+str(player.get("id"))}, access_token=self.access_token, prefer="return=minimal")
                popup.dismiss(); self.open_admin_players()
            except Exception as exc:
                amount.hint_text = str(exc)[:100]
        buttons.add_widget(self._menu_button("Save", save)); buttons.add_widget(self._menu_button("Cancel", popup.dismiss)); content.add_widget(buttons); popup.open()

    def admin_toggle_ban(self, player):
        if not self._admin_allowed(): return
        new_value = not bool(player.get("is_banned", False))
        try:
            self._api_request("PATCH", "/rest/v1/profiles", {"is_banned": new_value}, params={"id":"eq."+str(player.get("id"))}, access_token=self.access_token, prefer="return=minimal")
            self.open_admin_players()
        except Exception as exc:
            self.admin_status.text = (f"Ban update failed: {exc}")[:250] if hasattr(self, "admin_status") else str(exc)[:250]

    def open_admin_reports(self, *_):
        self._admin_simple_list("Level Reports", "level_reports", "id,level_id,reporter_id,reason,status,created_at", lambda x: f"Report: {x.get('reason','(no reason)')} | status: {x.get('status','?')}\nLevel: {x.get('level_id','?')} | Report ID: {x.get('id','')}")

    def refresh_admin_levels(self, *_):
        if (self.current_email or "").strip().lower() != "adnanzamanador@gmail.com" or not self.access_token:
            self.admin_status.text = "Admin access denied. Log in with the owner account."
            return
        try:
            rows = self._api_request("GET", "/rest/v1/levels", params={
                "select": "id,display_id,name,creator_username,created_at", "order": "created_at.desc", "limit": "100"
            }, access_token=self.access_token)
            self.admin_levels_list.clear_widgets()
            for item in rows:
                rowbox = BoxLayout(orientation="horizontal", size_hint_y=None, height=56, spacing=6)
                title = Label(text=f"#{item.get('display_id', '?')}  {item.get('name','Untitled')} - {item.get('creator_username','Guest')}\nDatabase UUID: {item.get('id','')}",
                              font_size=12, halign="left", valign="middle")
                title.bind(size=lambda inst, val: setattr(inst, "text_size", val))
                rowbox.add_widget(title)
                delete_btn = Button(text="Delete", size_hint_x=None, width=90, background_color=(0.75, 0.2, 0.2, 1))
                delete_btn.bind(on_press=lambda *_args, level=item: self.admin_delete_level(level))
                rowbox.add_widget(delete_btn)
                self.admin_levels_list.add_widget(rowbox)
            self.admin_status.text = f"Loaded {len(rows)} level(s). Delete only levels that violate your rules."
        except Exception as exc:
            self.admin_status.text = ("Could not load levels: " + str(exc))[:250]

    def admin_delete_level(self, level):
        if (self.current_email or "").strip().lower() != "adnanzamanador@gmail.com" or not self.access_token:
            self.admin_status.text = "Admin access denied."
            return
        content = BoxLayout(orientation="vertical", padding=10, spacing=8)
        content.add_widget(Label(text=f"Delete '{level.get('name','Untitled')}' from the community?", font_size=16))
        buttons = BoxLayout(size_hint_y=None, height=48, spacing=8)
        popup = Popup(title="Confirm Delete", content=content, size_hint=(0.9, 0.32))
        def confirm(*_):
            try:
                deleted = self._api_request("DELETE", "/rest/v1/levels", params={"id": "eq." + str(level.get("id"))},
                                  access_token=self.access_token, prefer="return=representation")
                if not deleted:
                    raise RuntimeError("Supabase deleted 0 rows. Run the admin-only DELETE policy SQL supplied with this update; RLS is blocking deletion.")
                popup.dismiss()
                self.refresh_admin_levels()
                self.admin_status.text = "Level deleted successfully."
            except Exception as exc:
                self.admin_status.text = ("Delete failed: " + str(exc))[:250]
        buttons.add_widget(self._menu_button("Delete", confirm))
        buttons.add_widget(self._menu_button("Cancel", popup.dismiss))
        content.add_widget(buttons)
        popup.open()

    def report_level_prompt(self, *_args, level=None):
        content = BoxLayout(orientation="vertical", padding=16, spacing=12)
        level_id = TextInput(text=str((level or {}).get("id", "")), hint_text="Community level UUID", multiline=False, size_hint_y=None, height=64, padding=(14, 16), font_size=20)
        reason = TextInput(hint_text="Explain why this level should be reviewed", multiline=True, size_hint_y=None, height=110, padding=(14, 14), font_size=20)
        content.add_widget(Label(text="Anyone can report a community level. You do not need to log in.", font_size=17, size_hint_y=None, height=50))
        content.add_widget(level_id)
        content.add_widget(reason)
        buttons = BoxLayout(size_hint_y=None, height=48, spacing=8)
        popup = Popup(title="Report Level", content=content, size_hint=(0.94, 0.68))
        def send_report(*_):
            if not level_id.text.strip() or not reason.text.strip():
                return
            try:
                if not reason.text.strip():
                    raise ValueError("Please enter a reason for the report.")
                payload = {"level_id": level_id.text.strip(), "reason": reason.text.strip(), "status": "open"}
                if self.current_user and self.current_user.get("id"):
                    payload["reporter_id"] = self.current_user.get("id")
                self._api_request("POST", "/rest/v1/level_reports", payload, access_token=self.access_token, prefer="return=representation")
                popup.dismiss()
                self.community_status.text = "Report submitted for review." if hasattr(self, "community_status") else "Report submitted for review."
            except Exception as exc:
                self.status_label.text = str(exc)[:220]
        buttons.add_widget(self._menu_button("Submit Report", send_report))
        buttons.add_widget(self._menu_button("Cancel", popup.dismiss))
        content.add_widget(buttons)
        popup.open()

    def _position_show_ui_button(self, *_):
        # Keep the only visible control tucked into the upper-right corner while UI is hidden.
        if hasattr(self, "show_ui_btn"):
            self.show_ui_btn.pos = (self.editor_canvas.right - self.show_ui_btn.width - 12,
                                    self.editor_canvas.top - self.show_ui_btn.height - 12)

    def hide_ui(self, *_):
        if self.is_playing or self.ui_hidden:
            return
        root = self.top_bar_layout.parent
        if root is not None:
            root.remove_widget(self.top_bar_layout)
        if self.bottom_bar_layout.parent is not None:
            self.bottom_bar_layout.parent.remove_widget(self.bottom_bar_layout)
        if self.show_ui_btn.parent is None:
            self.editor_canvas.add_widget(self.show_ui_btn)
        self._position_show_ui_button()
        self.ui_hidden = True

    def show_ui(self, *_):
        if not self.ui_hidden:
            return
        if self.show_ui_btn.parent is not None:
            self.show_ui_btn.parent.remove_widget(self.show_ui_btn)
        root = getattr(self, "root_layout", None) or self.editor_canvas.parent
        if root is not None:
            # Rebuild the usual edit layout so the canvas fills the space between the bars.
            root.remove_widget(self.editor_canvas)
            if self.top_bar_layout.parent is None:
                root.add_widget(self.top_bar_layout)
            if self.bottom_bar_layout.parent is None:
                root.add_widget(self.bottom_bar_layout)
            root.add_widget(self.editor_canvas)
        self.ui_hidden = False
        self.editor_canvas.redraw()

    def _build_edit_toolbar(self):
        self.bottom_bar_layout.clear_widgets()
        row1 = BoxLayout(spacing=8)
        row2 = BoxLayout(spacing=8)
        self.objects_btn = Button(text="Object Catalog", font_size=22,
                                  background_normal="", background_down="",
                                  background_color=self._theme()["accent"],
                                  color=self._theme()["text"])
        self.objects_btn.bind(on_press=lambda w: (
            Animation.cancel_all(w, "opacity"),
            (Animation(opacity=0.72, duration=0.055) +
             Animation(opacity=1, duration=0.15, t="out_back")).start(w)
        ))
        self.objects_btn.bind(on_press=self.open_objects_popup)
        row1.add_widget(self.objects_btn)
        for label, tool in (("Place", "place"), ("Select", "select"), ("Move", "move"), ("Copy", "copy"), ("Erase", "delete")):
            btn = Button(text=label, font_size=24, background_normal="", background_down="", background_color=self._theme()["panel"], color=self._theme()["text"])
            btn.bind(on_press=lambda instance, t=tool: self.set_edit_tool(t))
            row1.add_widget(btn)
        self.properties_btn = Button(text="Props", font_size=22, background_color=(0.3, 0.5, 0.7, 1))
        self.properties_btn.bind(on_press=self.open_properties_popup)
        self.save_btn = Button(text="Save", font_size=22, background_color=(0.2, 0.6, 0.3, 1))
        self.save_btn.bind(on_press=self.open_save_popup)
        self.load_btn = Button(text="Load", font_size=22, background_color=(0.5, 0.4, 0.8, 1))
        self.load_btn.bind(on_press=self.open_load_popup)
        # Recreate the Upload button whenever the edit toolbar is rebuilt after Play mode.
        # Keep the same callback and respect built-in editor mode restrictions.
        self.upload_btn = Button(text="Upload", font_size=22, background_color=(0.1, 0.62, 0.78, 1))
        self.upload_btn.bind(on_press=self.upload_from_editor)
        resize_btn = Button(text="Resize", font_size=22)
        resize_btn.bind(on_press=lambda instance: self.set_edit_tool("resize"))
        row2.add_widget(resize_btn)
        self.stages_btn = Button(text="Stages", font_size=22, background_color=(0.15, 0.58, 0.62, 1))
        self.stages_btn.bind(on_press=self.open_stages_popup)
        row2.add_widget(self.stages_btn)
        self.background_btn = Button(text="BG", font_size=20, background_color=self._theme()["panel"])
        self.background_btn.bind(on_press=self.open_background_popup)
        row2.add_widget(self.background_btn)
        self.rotate_btn = Button(text="Rotate", font_size=20, background_color=(0.55, 0.38, 0.75, 1))
        self.rotate_btn.bind(on_press=self.rotate_selected_object)
        row2.add_widget(self.rotate_btn)
        row2.add_widget(self.properties_btn)
        row2.add_widget(self.save_btn)
        row2.add_widget(self.load_btn)
        row2.add_widget(self.upload_btn)
        self.bottom_bar_layout.add_widget(row1)
        self.bottom_bar_layout.add_widget(row2)
        # Unified neon editor toolbar styling; keep distinct actions easy to spot.
        palette = self._theme()
        for toolbar in (row1, row2):
            for control in toolbar.children:
                if isinstance(control, Button):
                    control.background_normal = ""
                    control.background_down = ""
                    control.color = palette["text"]
                    control.bold = True
                    if control not in (self.objects_btn, self.properties_btn, self.save_btn,
                                       self.load_btn, self.upload_btn, self.stages_btn,
                                       self.rotate_btn):
                        control.background_color = palette["panel"]
        self.objects_btn.background_color = palette["accent"]
        self.properties_btn.background_normal = ""
        self.properties_btn.background_color = palette["secondary"]
        self.save_btn.background_normal = ""
        self.save_btn.background_color = palette["good"]
        self.load_btn.background_normal = ""
        self.load_btn.background_color = palette["panel"]
        self.upload_btn.background_normal = ""
        self.upload_btn.background_color = palette["accent"]
        self.stages_btn.background_normal = ""
        self.stages_btn.background_color = palette["panel"]
        if hasattr(self, "background_btn"):
            self.background_btn.background_normal = ""
            self.background_btn.background_color = palette["secondary"]
            self.background_btn.color = palette["text"]
        self.rotate_btn.background_normal = ""
        self.rotate_btn.background_color = palette["secondary"]
        self.bottom_bar_layout.height = 210
        # Re-apply mode rules after rebuilding: normal editor can upload; built-in editor cannot.
        builtin_mode = bool(getattr(self, "_builtin_editor_mode", False))
        self.upload_btn.disabled = builtin_mode
        self.upload_btn.opacity = 0.35 if builtin_mode else 1
        self.upload_btn.text = "Admin: Local Only" if builtin_mode else "Upload"

    def open_background_popup(self, *_):
        """Choose a per-stage editor/gameplay background. Default follows the current theme."""
        if self.is_playing:
            self.status_label.text = "Stop Play mode to change the stage background"
            return
        self._sync_current_stage()
        palette = self._theme()
        options = {
            "Default": None,
            "Midnight": (0.025, 0.04, 0.085, 1),
            "Deep Space": (0.012, 0.018, 0.055, 1),
            "Ocean": (0.015, 0.075, 0.12, 1),
            "Forest": (0.018, 0.075, 0.055, 1),
            "Sunset": (0.16, 0.045, 0.09, 1),
            "Violet": (0.075, 0.035, 0.14, 1),
            "Light Grid": (0.72, 0.80, 0.9, 1),
        }
        current = self.stages[self.current_stage_index].get("background", "Default")
        content = BoxLayout(orientation="vertical", padding=12, spacing=9)
        content.add_widget(Label(text="SELECT THIS STAGE'S BACKGROUND", size_hint_y=None,
                                 height=36, bold=True, color=palette["accent"]))
        popup = Popup(title="STAGE BACKGROUND", content=content, size_hint=(0.82, 0.82),
                      background="", background_color=(0.018, 0.028, 0.065, 0.99),
                      separator_color=palette["accent"], title_color=palette["text"])
        scroll = ScrollView(do_scroll_x=False, bar_width=5)
        choices = GridLayout(cols=2, spacing=8, padding=4, size_hint_y=None)
        choices.bind(minimum_height=choices.setter("height"))
        for name, color in options.items():
            button = Button(text=("✓  " if name == current else "") + name,
                            size_hint_y=None, height=64, bold=True, font_size=15,
                            background_normal="", background_down="",
                            background_color=color or palette["bg"], color=palette["text"])
            def choose(_button, selected=name):
                self.stages[self.current_stage_index]["background"] = selected
                self.editor_canvas.redraw()
                self.status_label.text = f"Background: {selected}"
                popup.dismiss()
            button.bind(on_release=choose)
            choices.add_widget(button)
        scroll.add_widget(choices)
        content.add_widget(scroll)
        close = Button(text="CLOSE", size_hint_y=None, height=48, bold=True,
                       background_normal="", background_color=palette["secondary"], color=palette["text"])
        close.bind(on_release=popup.dismiss)
        content.add_widget(close)
        popup.open()

    def _sync_current_stage(self):
        if hasattr(self, "editor_canvas") and self.stages and 0 <= self.current_stage_index < len(self.stages):
            self.stages[self.current_stage_index]["objects"] = self.editor_canvas.grid_data

    def select_stage(self, index):
        if not (0 <= index < len(self.stages)):
            return
        self._sync_current_stage()
        self.current_stage_index = index
        self.editor_canvas.grid_data = self.stages[index]["objects"]
        self.editor_canvas._runtime_index_dirty = True
        self.editor_canvas._render_stage_index = index
        self.editor_canvas.selected_key = None
        self.editor_canvas.active_spawn = None
        self.editor_canvas.reset_controls()
        self.editor_canvas.redraw()
        self.status_label.text = f"Editing {self.stages[index]['name']} ({index + 1}/{len(self.stages)})"

    def transition_stage(self, direction):
        """Switch stages without resetting run-wide time/score or losing collectibles."""
        if not self.is_playing:
            return False
        target = self.current_stage_index + (1 if direction > 0 else -1)
        if not (0 <= target < len(self.stages)):
            return False

        canvas = self.editor_canvas
        current = self.current_stage_index
        # Preserve the live stage grid (doors, broken blocks, etc.) and the
        # collected object keys before changing the active stage.
        self.stages[current]["objects"] = canvas.grid_data
        self._play_stage_collected[current] = set(canvas.collected_ids)
        run_time = float(canvas.elapsed_time)
        run_score = int(canvas.score)

        self.current_stage_index = target
        canvas.grid_data = self.stages[target]["objects"]
        canvas._runtime_index_dirty = True
        canvas._render_stage_index = target
        canvas.reset_controls()
        # reset_controls is also used for a new run, so explicitly restore the
        # run-wide counters and this stage's collected-item set after transition.
        canvas.elapsed_time = run_time
        canvas.score = run_score
        canvas.collected_ids = set(self._play_stage_collected.get(target, set()))

        cell = canvas.cell()
        canvas.player_x = canvas.x + 2 if direction > 0 else canvas.x + canvas.width - cell
        canvas.player_y = canvas.y + canvas.height - cell * 1.25
        canvas.active_spawn = None
        for key, obj in canvas.grid_data.items():
            if obj.get("id") == 51:
                bx, by, bw, bh = canvas.object_rect(key, obj, cell)
                canvas.player_x, canvas.player_y = bx, by + bh + 2
                break
        canvas.redraw()
        return True

    def open_stages_popup(self, *_):
        """Stage browser with a clear level preview and a complete object inventory."""
        if self.is_playing:
            self.status_label.text = "Return to Edit mode to manage stages"
            return
        self._sync_current_stage()
        palette = self._theme()
        content = BoxLayout(orientation="vertical", padding=12, spacing=9)
        popup = Popup(title="STAGES", content=content, size_hint=(0.96, 0.94),
                      background="", background_color=(0.018, 0.028, 0.065, 0.99),
                      separator_color=palette["accent"], title_color=palette["text"])
        heading = Label(text="SELECT A STAGE  •  PREVIEW & OBJECTS", size_hint_y=None,
                        height=34, font_size=17, bold=True, color=palette["accent"])
        content.add_widget(heading)
        listing = GridLayout(cols=1, spacing=10, padding=(3, 5), size_hint_y=None)
        listing.bind(minimum_height=listing.setter("height"))
        scroll = ScrollView(do_scroll_x=False, bar_width=6, scroll_type=["bars", "content"])
        scroll.add_widget(listing)
        content.add_widget(scroll)

        for i, stage in enumerate(self.stages):
            stage = stage if isinstance(stage, dict) else {}
            objects = stage.get("objects", {})
            if not isinstance(objects, dict):
                objects = {}
            selected = (i == self.current_stage_index)
            # Miniature preview uses the same object data as the editor stage.
            preview_data = {"cols": 32, "rows": 20,
                "objects": [{"col": int(k[0]), "row": int(k[1]), "object": v}
                            for k, v in objects.items()
                            if isinstance(k, tuple) and len(k) >= 2 and isinstance(v, dict)]}
            inventory_counts = {}
            for obj in objects.values():
                if not isinstance(obj, dict):
                    continue
                oid = obj.get("id")
                meta = next((entry for entry in OBJECTS_DATA if entry.get("id") == oid), None)
                name = str(obj.get("name") or (meta.get("name") if meta else "Unknown Object"))
                inventory_counts[name] = inventory_counts.get(name, 0) + 1
            inventory_lines = [f"• {name}  ×{count}" for name, count in sorted(inventory_counts.items())]
            inventory_text = "\n".join(inventory_lines) if inventory_lines else "No objects placed yet"
            inventory_text += f"\n\nTOTAL OBJECTS: {len(objects)}"
            inventory_height = max(68, 22 * (len(inventory_lines) + 2))
            card_height = max(174, inventory_height + 98)

            card = BoxLayout(orientation="horizontal", size_hint_y=None,
                             height=card_height, padding=9, spacing=10)
            with card.canvas.before:
                Color(*(palette["panel"][:3] + (1,)))
                card._card_bg = Rectangle(pos=card.pos, size=card.size)
                Color(*((palette["good"] if selected else palette["accent"])[:3]), 0.9)
                card._card_edge = Line(rounded_rectangle=(card.x, card.y, card.width, card.height, 10), width=1.35)
            def sync_card(widget, _value):
                widget._card_bg.pos = widget.pos
                widget._card_bg.size = widget.size
                widget._card_edge.rounded_rectangle = (widget.x, widget.y, widget.width, widget.height, 10)
            card.bind(pos=sync_card, size=sync_card)

            preview_column = BoxLayout(orientation="vertical", size_hint_x=None, width=190, spacing=5)
            preview = CommunityLevelThumbnail(preview_data, size_hint=(1, 1))
            preview_column.add_widget(preview)
            bg_name = str(stage.get("background", "Default"))
            bg_label = Label(text=f"BG: {bg_name}", size_hint_y=None, height=22,
                             font_size=11, color=palette["accent"], halign="center")
            bg_label.bind(size=lambda w, _v: setattr(w, "text_size", w.size))
            preview_column.add_widget(bg_label)
            card.add_widget(preview_column)

            details = BoxLayout(orientation="vertical", spacing=5)
            title = Label(text=("▶  " if selected else "") +
                          f"STAGE {i + 1}: {stage.get('name') or f'Stage {i + 1}'}",
                          size_hint_y=None, height=29, font_size=15, bold=True,
                          color=palette["good"] if selected else palette["text"],
                          halign="left", valign="middle")
            title.bind(size=lambda w, _v: setattr(w, "text_size", w.size))
            details.add_widget(title)
            inventory = Label(text=inventory_text, font_size=12,
                              color=(0.76, 0.85, 0.96, 1), halign="left", valign="top",
                              size_hint_y=None, height=inventory_height)
            inventory.bind(size=lambda w, _v: setattr(w, "text_size", w.size))
            details.add_widget(inventory)
            edit_btn = Button(text="EDIT THIS STAGE" if not selected else "CURRENT STAGE",
                              size_hint_y=None, height=39, bold=True, font_size=13,
                              halign="center", valign="middle", background_normal="",
                              background_down="", background_color=palette["accent"] if not selected else palette["good"],
                              color=palette["text"])
            edit_btn.bind(size=lambda w, _v: setattr(w, "text_size", (w.width - 16, w.height - 8)))
            edit_btn.bind(on_release=lambda _btn, idx=i: (self.select_stage(idx), popup.dismiss()))
            details.add_widget(edit_btn)
            card.add_widget(details)
            listing.add_widget(card)

        actions = BoxLayout(size_hint_y=None, height=54, spacing=9)
        add_btn = Button(text="+  ADD STAGE", bold=True, font_size=14,
                         halign="center", valign="middle", background_normal="",
                         background_down="", background_color=palette["accent"], color=palette["text"])
        add_btn.bind(size=lambda w, _v: setattr(w, "text_size", (w.width - 16, w.height - 8)))
        def add_stage(*_):
            self._sync_current_stage()
            idx = len(self.stages) + 1
            self.stages.append({"name": f"Stage {idx}", "objects": {}, "background": "Default"})
            self.select_stage(len(self.stages) - 1)
            popup.dismiss()
        add_btn.bind(on_release=add_stage)
        close_btn = Button(text="CLOSE", size_hint_x=None, width=142,
                           size_hint_y=1, bold=True, font_size=14,
                           halign="center", valign="middle", padding=(4, 0),
                           background_normal="", background_down="",
                           background_color=palette["secondary"], color=palette["text"])
        def fit_close_text(widget, *_):
            widget.text_size = (max(1, widget.width - 18), max(1, widget.height - 10))
            widget.texture_update()
        close_btn.bind(size=fit_close_text, pos=fit_close_text)
        close_btn.bind(on_release=popup.dismiss)
        actions.add_widget(add_btn)
        actions.add_widget(close_btn)
        content.add_widget(actions)
        popup.open()

    def toggle_play_mode(self, *_):
        canvas = self.editor_canvas
        root = getattr(self, "root_layout", None)
        if root is None:
            root = self.top_bar_layout.parent or self.bottom_bar_layout.parent or canvas.parent
        if root is None:
            return
        # Keep a clean copy of the level design. Gameplay changes (collected coins,
        # opened doors, toggled groups, broken blocks, etc.) must not erase the editor map.
        if not self.is_playing:
            self._reward_flow_active = False
            self._reward_bonus_claimed = False
            self._sync_current_stage()
            canvas.elapsed_time = 0.0
            canvas.score = 0
            canvas.collected_ids.clear()
            self._play_stage_collected = {i: set() for i in range(len(self.stages))}
            self._play_start_stage_index = self.current_stage_index
            self._play_stages_snapshot = copy.deepcopy(self.stages)
            self._play_level_snapshot = copy.deepcopy(canvas.grid_data)
        elif getattr(self, "_play_stages_snapshot", None) is not None:
            self.stages = copy.deepcopy(self._play_stages_snapshot)
            self.current_stage_index = max(0, min(self._play_start_stage_index, len(self.stages) - 1))
            canvas.grid_data = copy.deepcopy(self.stages[self.current_stage_index]["objects"])
            self._play_stages_snapshot = None
            self._play_level_snapshot = None
            canvas.selected_key = None
        # Remove all root children first, then rebuild a stable order. This avoids
        # reparenting/layout crashes when switching Play <-> Edit.
        self.is_playing = not self.is_playing
        canvas.reset_controls()
        if self.is_playing:
            if self.show_ui_btn.parent is canvas:
                canvas.remove_widget(self.show_ui_btn)
            self.ui_hidden = False
            locked_level = bool(getattr(self, "_community_play_mode", False) or
                                getattr(self, "_builtin_play_mode", False))
            self.play_btn.text = "Playing" if locked_level else "Edit"
            self.play_btn.disabled = locked_level
            self.play_btn.opacity = 0.55 if locked_level else 1.0
            self.play_btn.background_color = (0.9, 0.6, 0.1, 1)
            if self.clear_btn.parent is not None:
                self.clear_btn.parent.remove_widget(self.clear_btn)
            canvas.spawn_player()
            self.bottom_bar_layout.clear_widgets()
            controls = BoxLayout(spacing=10, padding=(8, 6))
            left = MultiTouchButton(lambda active: setattr(canvas, "move_left", active), text="◀  LEFT", font_size=42, bold=True, size_hint=(1, 1), size_hint_min_y=104, background_normal="", background_down="", background_color=self._theme()["secondary"])
            jump = MultiTouchButton(lambda active: self.jump_player(active), text="JUMP  ▲", font_size=42, bold=True, size_hint=(1, 1), size_hint_min_y=104, background_normal="", background_down="", background_color=self._theme()["good"])
            self.jump_button = jump
            right = MultiTouchButton(lambda active: setattr(canvas, "move_right", active), text="RIGHT  ▶", font_size=42, bold=True, size_hint=(1, 1), size_hint_min_y=104, background_normal="", background_down="", background_color=self._theme()["secondary"])
            for btn in (left, jump, right):
                controls.add_widget(btn)
            self.bottom_bar_layout.add_widget(controls)
            self.bottom_bar_layout.height = 210
        else:
            self.play_btn.text = "Play"
            self.play_btn.disabled = False
            self.play_btn.opacity = 1.0
            self.play_btn.background_color = (0.2, 0.8, 0.3, 1)
            if self.clear_btn.parent is None:
                self.top_bar_layout.add_widget(self.clear_btn)
            self._build_edit_toolbar()
            self.edit_tool = "place"
            canvas.redraw()
        root.clear_widgets()
        root.add_widget(self.top_bar_layout)
        root.add_widget(canvas)
        root.add_widget(self.bottom_bar_layout)
        # Root order is always top bar, flexible canvas, bottom controls.
        if self.is_playing:
            self.top_bar_layout.height = 72
        else:
            self.top_bar_layout.height = 72

    def set_edit_tool(self, tool):
        self.edit_tool = tool
        names = {"place": "Place objects", "select": "Tap an object to select it", "move": "Drag an object to move it", "copy": "Tap an object to copy it", "delete": "Tap an object to erase it", "resize": "Drag over an object to resize it", "rotate": "Drag the outer rotation wheel to rotate the selected object"}
        self.status_label.text = f"Tool: {names.get(tool, tool)}"
        canvas = getattr(self, "editor_canvas", None)
        if canvas is not None and not self.is_playing:
            canvas.redraw()

    def rotate_selected_object(self, *_):
        """Enter rotation mode; the external circular wheel appears around selection."""
        if self.is_playing:
            self.status_label.text = "Stop Play mode before rotating objects"
            return
        if self.editor_canvas.selected_key is None:
            self.status_label.text = "Select an object first, then tap Rotate"
            self.set_edit_tool("select")
            return
        self.set_edit_tool("rotate")
        self.editor_canvas.redraw()

    def open_properties_popup(self, *_):
        canvas = self.editor_canvas
        key = canvas.selected_key
        if key is None or key not in canvas.grid_data:
            self.status_label.text = "Select an object first, then tap Props"
            self.set_edit_tool("select")
            return
        obj = canvas.grid_data[key]
        oid = obj.get("id")
        width, height = parse_tile_dimensions(obj.get("length", "1 Tile W x 1 Tile L"))
        content = BoxLayout(orientation="vertical", padding=10, spacing=9)
        scroll = ScrollView(do_scroll_x=False, bar_width=12)
        fields = BoxLayout(orientation="vertical", padding=8, spacing=9, size_hint_y=None)
        fields.bind(minimum_height=fields.setter("height"))
        fields.add_widget(Label(text=f"Edit properties: {obj.get('name', 'Object')}", size_hint_y=None, height=38, font_size=18, bold=True))
        def add_field(label, value, hint=""):
            label_widget = Label(text=label, size_hint_y=None, height=40, font_size=15,
                                 halign="left", valign="middle", text_size=(Window.width * 0.80, None))
            fields.add_widget(label_widget)
            widget = TextInput(text=str(value), hint_text=hint or label, multiline=False,
                               size_hint_y=None, height=48, font_size=18, padding=(12, 12))
            fields.add_widget(widget)
            return widget
        name_input = add_field("Name", obj.get("name", "Object"))
        text_input = None
        if oid == 45:
            text_input = add_field("Displayed Text", obj.get("display_text", "Enter Your Text"), "Enter Your Text")
        width_input = add_field("Width (tiles)", f"{width:g}")
        height_input = add_field("Height (tiles)", f"{height:g}")
        chosen_color = {"value": obj.get("color", "WHITE")}
        color_row = BoxLayout(size_hint_y=None, height=52, spacing=8)
        color_btn = Button(text="Choose Color Wheel", font_size=16)
        color_preview = Widget(size_hint_x=None, width=52)
        def paint_preview(*_):
            color_preview.canvas.clear()
            with color_preview.canvas:
                Color(*get_color_rgba(chosen_color["value"]))
                Rectangle(pos=color_preview.pos, size=color_preview.size)
        color_preview.bind(pos=paint_preview, size=paint_preview)
        def open_color_wheel(*_):
            picker_content = BoxLayout(orientation="vertical", padding=10, spacing=8)
            wheel = ColorWheel(chosen_color["value"], on_color=lambda value: (chosen_color.__setitem__("value", value), paint_preview()), size_hint=(1, 1))
            picker_content.add_widget(wheel)
            done = Button(text="Use Color", size_hint_y=None, height=54, font_size=18)
            picker = Popup(title="Color Wheel", content=picker_content, size_hint=(0.8, 0.9))
            done.bind(on_press=picker.dismiss)
            picker_content.add_widget(done)
            picker.open()
        color_btn.bind(on_press=open_color_wheel)
        color_row.add_widget(color_btn)
        color_row.add_widget(color_preview)
        fields.add_widget(Label(text="Color", size_hint_y=None, height=34, font_size=15, halign="left"))
        fields.add_widget(color_row)
        paint_preview()
        group_input = add_field("Group ID (optional)", obj.get("group_id", ""), "e.g. door_group")
        trigger_widgets = {}
        if oid in self.editor_canvas.TRIGGER_IDS:
            fields.add_widget(Label(text=f"{obj.get('name', 'Trigger')} Settings", size_hint_y=None, height=44, font_size=16, bold=True, halign="left", valign="middle", text_size=(Window.width * 0.80, None)))
            def add_choice(field_name, label, options, current):
                fields.add_widget(Label(text=label, size_hint_y=None, height=36, font_size=15, halign="left", valign="middle"))
                choice = Spinner(text=str(current), values=tuple(options), size_hint_y=None, height=48, font_size=17)
                fields.add_widget(choice); trigger_widgets[field_name] = choice
                return choice
            def add_group_field(field_name="effect_group_id", label="Effect Group ID", current=None):
                trigger_widgets[field_name] = add_field(label, obj.get(field_name, obj.get("target_group_id", "") if current is None else current), "Match this ID with target objects' Group ID")
            add_choice("activation_mode", "Activation", ["Normal", "Touch", "Auto activate on spawn"], obj.get("activation_mode", "Normal"))
            trigger_widgets["group_id"] = add_field("This Trigger's Group ID (optional)", obj.get("group_id", ""), "Other triggers can activate this trigger by targeting this Group ID")
            if oid == 50:
                trigger_widgets["target_group_id"] = add_field("Target Group ID", obj.get("target_group_id", ""), "Match target objects' Group ID")
                alpha_value = float(obj.get("alpha_value", 0))
                alpha_row = BoxLayout(orientation="vertical", size_hint_y=None, height=72, spacing=2)
                alpha_label = Label(text=f"Target transparency: {alpha_value:.0f}%", size_hint_y=None, height=28, font_size=15)
                alpha_slider = Slider(min=0, max=100, value=max(0, min(100, alpha_value)), step=1, size_hint_y=None, height=40)
                alpha_slider.bind(value=lambda _w, v: setattr(alpha_label, "text", f"Target transparency: {v:.0f}%"))
                alpha_row.add_widget(alpha_label); alpha_row.add_widget(alpha_slider); fields.add_widget(alpha_row)
                trigger_widgets["alpha_value"] = alpha_slider
                trigger_widgets["alpha_speed"] = add_field("Fade Time (seconds)", obj.get("alpha_speed", 1.0))
            elif oid == 54:
                add_group_field()
                trigger_widgets["timer_duration"] = add_field("Delay Time (seconds)", obj.get("timer_duration", 3))
                trigger_widgets["next_trigger_group_id"] = add_field("Next Trigger Group ID (optional)", obj.get("next_trigger_group_id", ""), "After this timer finishes, activate trigger(s) whose Group ID matches")
                add_choice("trigger_action", "Action", ["Toggle", "ON", "OFF"], obj.get("trigger_action", "Toggle"))
                add_choice("timer_loop", "Loop", ["Once", "Loop"], obj.get("timer_loop", "Once"))
            elif oid == 55:
                add_group_field()
                direction_spinner = add_choice("move_direction", "Select Direction", ["Up", "Down", "Up and down", "Right", "Left", "Right and left"], obj.get("move_direction", "Right"))
                trigger_widgets["move_time"] = add_field("Movement Time (seconds)", obj.get("move_time", 2.0))
                axis_fields = BoxLayout(orientation="vertical", size_hint_y=None, spacing=9)
                axis_fields.bind(minimum_height=axis_fields.setter("height"))
                fields.add_widget(axis_fields)
                def rebuild_move_axis(*_):
                    old_x = trigger_widgets.get("move_x_tiles")
                    old_y = trigger_widgets.get("move_y_tiles")
                    x_value = old_x.text if old_x is not None else str(obj.get("move_x_tiles", obj.get("move_distance", 1)))
                    y_value = old_y.text if old_y is not None else str(obj.get("move_y_tiles", obj.get("move_distance", 1)))
                    axis_fields.clear_widgets()
                    trigger_widgets.pop("move_x_tiles", None); trigger_widgets.pop("move_y_tiles", None)
                    if direction_spinner.text in ("Right", "Left", "Right and left"):
                        label = Label(text="Movement (X) – tiles", size_hint_y=None, height=36, font_size=15, halign="left")
                        widget = TextInput(text=x_value, hint_text="Horizontal distance in tiles", multiline=False, size_hint_y=None, height=48, font_size=18, padding=(12, 12))
                        axis_fields.add_widget(label); axis_fields.add_widget(widget); trigger_widgets["move_x_tiles"] = widget
                    if direction_spinner.text in ("Up", "Down", "Up and down"):
                        label = Label(text="Movement (Y) – tiles", size_hint_y=None, height=36, font_size=15, halign="left")
                        widget = TextInput(text=y_value, hint_text="Vertical distance in tiles", multiline=False, size_hint_y=None, height=48, font_size=18, padding=(12, 12))
                        axis_fields.add_widget(label); axis_fields.add_widget(widget); trigger_widgets["move_y_tiles"] = widget
                direction_spinner.bind(text=rebuild_move_axis)
                rebuild_move_axis()
                add_choice("move_loop", "Loop", ["Once", "Loop"], obj.get("move_loop", "Once"))
            elif oid == 56:
                sound_action_spinner = add_choice("sound_action", "Sound", ["Play", "Stop"], obj.get("sound_action", "Play"))
                sound_fields = BoxLayout(orientation="vertical", size_hint_y=None, spacing=9)
                sound_fields.bind(minimum_height=sound_fields.setter("height"))
                fields.add_widget(sound_fields)
                sound_values = {
                    "effect_group_id": str(obj.get("effect_group_id", obj.get("target_group_id", ""))),
                    "stop_effect_group_id": str(obj.get("stop_effect_group_id", "")),
                    "sound_path": str(obj.get("sound_path", "")),
                    "sound_volume": str(obj.get("sound_volume", 100)),
                    "sound_playback": str(obj.get("sound_playback", "Once")),
                    "sound_delay": str(obj.get("sound_delay", 0)),
                }
                def rebuild_sound_fields(*_):
                    for field_name in ("effect_group_id", "stop_effect_group_id", "sound_path", "sound_volume", "sound_playback", "sound_delay"):
                        widget = trigger_widgets.pop(field_name, None)
                        if widget is not None and isinstance(widget, TextInput): sound_values[field_name] = widget.text
                        elif widget is not None and isinstance(widget, Spinner): sound_values[field_name] = widget.text
                    sound_fields.clear_widgets()
                    def sound_text(field_name, label, hint=""):
                        label_widget = Label(text=label, size_hint_y=None, height=36, font_size=15, halign="left", valign="middle")
                        sound_fields.add_widget(label_widget)
                        widget = TextInput(text=sound_values[field_name], hint_text=hint or label, multiline=False, size_hint_y=None, height=48, font_size=18, padding=(12, 12))
                        sound_fields.add_widget(widget); trigger_widgets[field_name] = widget
                        return widget
                    if sound_action_spinner.text == "Stop":
                        sound_text("stop_effect_group_id", "Effect Group ID to Stop", "Enter the Effect Group ID of the playing sound")
                    else:
                        sound_text("effect_group_id", "Effect Group ID", "Match with target objects' Group ID")
                        path_widget = sound_text("sound_path", "Selected Sound File", "Choose a sound from Android storage")
                        choose_btn = Button(text="Browse Android Storage", size_hint_y=None, height=52, font_size=16)
                        choose_btn.bind(on_press=lambda *_: self.open_audio_chooser(path_widget))
                        sound_fields.add_widget(choose_btn)
                        sound_text("sound_volume", "Volume (0–100%)")
                        playback_label = Label(text="Playback", size_hint_y=None, height=36, font_size=15, halign="left")
                        playback_spinner = Spinner(text=sound_values["sound_playback"], values=("Once", "Loop"), size_hint_y=None, height=48, font_size=17)
                        sound_fields.add_widget(playback_label); sound_fields.add_widget(playback_spinner)
                        trigger_widgets["sound_playback"] = playback_spinner
                        sound_text("sound_delay", "Delay (seconds)")
                sound_action_spinner.bind(text=rebuild_sound_fields)
                rebuild_sound_fields()
            elif oid == 57:
                add_group_field()
                add_choice("trigger_action", "Toggle Mode", ["Toggle", "ON", "OFF"], obj.get("trigger_action", "Toggle"))
        scroll.add_widget(fields)
        content.add_widget(scroll)
        buttons = BoxLayout(size_hint_y=None, height=56, spacing=10)
        palette = self._theme()
        popup = Popup(title="OBJECT PROPERTIES", content=content, size_hint=(0.94, 0.96),
                      background="", background_color=(0.018, 0.028, 0.065, 0.99),
                      separator_color=palette["accent"], title_color=palette["text"])
        with content.canvas.before:
            Color(0.025, 0.04, 0.085, 1)
            content._props_bg = Rectangle(pos=content.pos, size=content.size)
        content.bind(pos=lambda w, _v: setattr(w._props_bg, "pos", w.pos),
                     size=lambda w, _v: setattr(w._props_bg, "size", w.size))
        def style_property_tree(widget):
            if isinstance(widget, Label):
                widget.color = palette["text"]
            elif isinstance(widget, TextInput):
                widget.background_normal = ""
                widget.background_active = ""
                widget.background_color = (0.055, 0.085, 0.15, 1)
                widget.foreground_color = palette["text"]
                widget.cursor_color = palette["accent"]
                widget.hint_text_color = (0.55, 0.66, 0.8, 1)
            elif isinstance(widget, Spinner):
                widget.background_normal = ""
                widget.background_color = palette["panel"]
                widget.color = palette["text"]
            elif isinstance(widget, Button):
                widget.background_normal = ""
                widget.background_color = palette["panel"]
                widget.color = palette["text"]
            for child in getattr(widget, "children", []):
                style_property_tree(child)
        style_property_tree(content)
        apply_btn = Button(text="APPLY CHANGES", font_size=17, bold=True,
                           background_normal="", background_color=palette["accent"],
                           color=palette["text"])
        cancel_btn = Button(text="CANCEL", font_size=17, bold=True,
                            background_normal="", background_color=palette["secondary"],
                            color=palette["text"])
        def apply_properties(*_):
            try:
                w = max(0.2, min(float(canvas.cols - key[0]), float(width_input.text or "1")))
                h = max(0.2, min(float(canvas.rows - key[1]), float(height_input.text or "1")))
                new_obj = dict(obj)
                new_obj["name"] = name_input.text.strip() or obj.get("name", "Object")
                if oid == 45:
                    new_obj["display_text"] = (text_input.text if text_input is not None else obj.get("display_text", "Enter Your Text")).strip() or "Enter Your Text"
                new_obj["length"] = f"{w:g} Tiles W x {h:g} Tiles L"
                new_obj["color"] = chosen_color["value"] or obj.get("color", "WHITE")
                if group_input is not None:
                    new_obj["group_id"] = group_input.text.strip()
                for field_name, widget in trigger_widgets.items():
                    value = bool(widget.active) if isinstance(widget, Switch) else (float(widget.value) if isinstance(widget, Slider) else widget.text.strip())
                    if field_name in ("timer_duration", "timer_extra_delay", "move_distance", "move_x_tiles", "move_y_tiles", "move_time", "sound_volume", "sound_delay", "alpha_value", "alpha_speed", "in_zone_alpha_value", "in_zone_speed", "out_zone_alpha_value", "out_zone_speed"):

                        value = float(value or "0")
                        if field_name in ("timer_duration", "move_time", "alpha_speed", "in_zone_speed", "out_zone_speed"): value = max(0.05, value)
                        if field_name in ("timer_extra_delay", "move_distance", "move_x_tiles", "move_y_tiles", "sound_delay"): value = max(0.0, value)
                        if field_name in ("alpha_value", "in_zone_alpha_value", "out_zone_alpha_value"): value = max(0.0, min(100.0, value))
                        if field_name == "sound_volume": value = max(0.0, min(100.0, value))
                    elif field_name == "sound_loop":
                        value = bool(value)
                    elif field_name == "activation_mode" and value not in ("Touch", "In Touch", "Normal", "Auto activate on spawn"):
                        raise ValueError("Activation must be Normal, Touch, or Auto activate on spawn")
                    elif field_name == "normal_direction" and value not in ("Both", "Left to Right", "Right to Left"):
                        raise ValueError("Normal Direction must be Both, Left to Right, or Right to Left")
                    elif field_name == "move_direction" and value not in ("Right", "Left", "Up", "Down", "Up and down", "Right and left"):
                        raise ValueError("Choose a valid movement direction")
                    elif field_name == "easing" and value not in ("Linear", "Ease In", "Ease Out", "Ease In-Out", "Bounce", "Elastic"):
                        raise ValueError("Choose a listed easing option")
                    elif field_name == "timer_mode" and value not in ("Countdown", "Interval", "Stopwatch"):
                        raise ValueError("Timer Mode must be Countdown, Interval, or Stopwatch")
                    elif field_name == "timer_start" and value not in ("Level Start", "On Activation"):
                        raise ValueError("Timer Start must be Level Start or On Activation")
                    elif field_name == "timer_repeat" and value not in ("Once", "Repeat automatically", "Restartable"):
                        raise ValueError("Repeat must be Once, Repeat automatically, or Restartable")
                    elif field_name == "trigger_action" and value not in ("Toggle", "Enable", "Disable", "ON", "OFF"):
                        raise ValueError("Action must be Toggle, ON, or OFF")
                    elif field_name == "sound_action" and value not in ("Play", "Stop"):
                        raise ValueError("Sound Action must be Play or Stop")
                    new_obj[field_name] = value
                canvas.grid_data[key] = new_obj
                canvas._mark_grid_changed()
                self.status_label.text = f"Updated: {new_obj['name']}"
                canvas.redraw()
                popup.dismiss()
            except ValueError as exc:
                self.status_label.text = str(exc) or "Please check numeric properties"
        apply_btn.bind(on_press=apply_properties)
        cancel_btn.bind(on_press=popup.dismiss)
        buttons.add_widget(apply_btn)
        buttons.add_widget(cancel_btn)
        content.add_widget(buttons)
        popup.open()

    def open_audio_chooser(self, target_input):
        content = BoxLayout(orientation="vertical", padding=8, spacing=6)
        start_path = "/storage/emulated/0" if os.path.isdir("/storage/emulated/0") else os.path.expanduser("~")
        chooser = FileChooserListView(path=start_path, filters=["*.mp3", "*.wav", "*.ogg", "*.m4a", "*.aac", "*.mp4", "*.flac"], size_hint_y=1)
        content.add_widget(chooser)
        buttons = BoxLayout(size_hint_y=None, height=42, spacing=8)
        popup = Popup(title="Choose Sound File", content=content, size_hint=(0.9, 0.9))
        choose = Button(text="Use Selected File")
        cancel = Button(text="Cancel")
        def use_file(*_):
            if not chooser.selection:
                self.status_label.text = "Select an audio/video file first"
                return
            path = chooser.selection[0]
            if path.lower().endswith(".mp4"):
                ffmpeg = shutil.which("ffmpeg")
                if not ffmpeg:
                    self.status_label.text = "MP4 selected, but FFmpeg is not installed; choose audio or install FFmpeg"
                    return
                output = os.path.splitext(path)[0] + "_audio.mp3"
                try:
                    result = subprocess.run([ffmpeg, "-y", "-i", path, "-vn", "-codec:a", "libmp3lame", output], capture_output=True, text=True, timeout=120)
                    if result.returncode != 0 or not os.path.isfile(output):
                        self.status_label.text = "MP4 audio extraction failed; check that the video contains audio"
                        return
                    path = output
                except Exception as exc:
                    self.status_label.text = f"Audio conversion failed: {exc}"
                    return
            try:
                audio_dir = os.path.join(self.user_data_dir, "trigger_audio")
                os.makedirs(audio_dir, exist_ok=True)
                safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", os.path.basename(path)) or "sound_audio"
                destination = os.path.join(audio_dir, safe_name)
                if os.path.abspath(path) != os.path.abspath(destination):
                    if os.path.exists(destination):
                        stem, ext = os.path.splitext(safe_name)
                        destination = os.path.join(audio_dir, f"{stem}_{int(time.time())}{ext}")
                    shutil.copy2(path, destination)
                path = destination
            except Exception as exc:
                self.status_label.text = f"Could not import sound into game storage: {exc}"
                return
            target_input.text = path
            popup.dismiss()
        choose.bind(on_press=use_file)
        cancel.bind(on_press=popup.dismiss)
        buttons.add_widget(choose)
        buttons.add_widget(cancel)
        content.add_widget(buttons)
        popup.open()

    def levels_directory(self):
        folder = os.path.join(self.user_data_dir, "levels")
        os.makedirs(folder, exist_ok=True)
        return folder

    def open_save_popup(self, *_):
        content = BoxLayout(orientation="vertical", padding=10, spacing=8)
        name_input = TextInput(text="my_level", hint_text="Level name", multiline=False, size_hint_y=None, height=42)
        content.add_widget(Label(text="Save current level", size_hint_y=None, height=28))
        content.add_widget(name_input)
        buttons = BoxLayout(size_hint_y=None, height=42, spacing=8)
        popup = Popup(title="Save Level", content=content, size_hint=(0.75, 0.45))
        save = Button(text="Save")
        cancel = Button(text="Cancel")
        def do_save(*_):
            name = re.sub(r"[^A-Za-z0-9_-]+", "_", name_input.text.strip()).strip("_") or "my_level"
            try:
                self._sync_current_stage()
                if getattr(self, "_builtin_editor_mode", False):
                    if not self._admin_allowed():
                        raise PermissionError("Only the admin can save built-in levels")
                    existing = getattr(self, "_builtin_current_filename", "")
                    if existing and os.path.basename(existing) == existing:
                        name = os.path.splitext(existing)[0]
                    path = os.path.join(self._builtin_levels_directory(), name + ".json")
                else:
                    path = os.path.join(self.levels_directory(), name + ".json")
                if getattr(self, "_builtin_editor_mode", False):
                    data = self._serialize_stage_pack()
                else:
                    # Use the same backward-compatible stage-pack format for normal
                    # and admin levels so stage layouts and per-stage backgrounds persist.
                    data = self._serialize_stage_pack()
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                if not getattr(self, "_builtin_editor_mode", False) and self.access_token:
                    try:
                        self._cloud_upsert_json("levels", name + ".json", data)
                        cloud_note = " (cloud saved)"
                    except Exception as cloud_exc:
                        cloud_note = " (local saved; cloud sync failed: " + str(cloud_exc)[:80] + ")"
                else:
                    cloud_note = " (log in and use Save All to Cloud to back up)" if not self.access_token else ""
                self.status_label.text = ("Saved built-in level: " if getattr(self, "_builtin_editor_mode", False) else "Saved: ") + name + cloud_note
                popup.dismiss()
                if getattr(self, "_builtin_editor_mode", False):
                    self._builtin_current_filename = name + ".json"
            except Exception as exc:
                self.status_label.text = f"Save failed: {exc}"
        save.bind(on_press=do_save)
        cancel.bind(on_press=popup.dismiss)
        buttons.add_widget(save)
        buttons.add_widget(cancel)
        content.add_widget(buttons)
        popup.open()

    def open_load_popup(self, *_):
        folder = self.levels_directory()
        files = sorted(f for f in os.listdir(folder) if f.lower().endswith(".json"))
        content = BoxLayout(orientation="vertical", padding=8, spacing=6)
        popup = Popup(title="Load Level", content=content, size_hint=(0.8, 0.8))
        scroll = ScrollView()
        listing = GridLayout(cols=1, spacing=5, size_hint_y=None, padding=4)
        listing.bind(minimum_height=listing.setter("height"))
        if not files:
            listing.add_widget(Label(text="No saved levels yet. Use Save first.", size_hint_y=None, height=52))
        for filename in files:
            btn = Button(text=filename[:-5], size_hint_y=None, height=42)
            def load_one(instance, fname=filename):
                path = os.path.join(folder, fname)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    new_grid = {}
                    for item in data.get("objects", []):
                        col, row = int(item["col"]), int(item["row"])
                        if 0 <= col < self.editor_canvas.cols and 0 <= row < self.editor_canvas.rows and isinstance(item.get("object"), dict):
                            base = (col, row)
                            if base not in new_grid:
                                new_grid[base] = item["object"]
                            else:
                                serial = 1
                                while (col, row, serial) in new_grid:
                                    serial += 1
                                new_grid[(col, row, serial)] = item["object"]
                    self.editor_canvas.grid_data = new_grid
                    self._sync_current_stage()
                    self.stages[self.current_stage_index]["objects"] = new_grid
                    self.editor_canvas.selected_key = None
                    self.editor_canvas.active_spawn = None
                    self.editor_canvas.reset_controls()
                    self.editor_canvas.redraw()
                    self.status_label.text = f"Loaded: {fname[:-5]}"
                    popup.dismiss()
                except Exception as exc:
                    self.status_label.text = f"Load failed: {exc}"
            btn.bind(on_press=load_one)
            listing.add_widget(btn)
        scroll.add_widget(listing)
        content.add_widget(scroll)
        close = Button(text="Close", size_hint_y=None, height=40)
        close.bind(on_press=popup.dismiss)
        content.add_widget(close)
        popup.open()

    def jump_player(self, active):
        canvas = self.editor_canvas
        if not active:
            # Tap and hold have the same predictable normal jump height.
            return

        canvas.jump_buffer_remaining = 0.14
        no_jump = any(self._player_overlaps_key(k, o)
                      for k, o in canvas._objects_by_id.get(41, ())) or canvas.zone_modes.get("no_jump", False)
        if no_jump:
            canvas.jump_buffer_remaining = 0.0
            return

        now = time.monotonic()
        if now <= getattr(canvas, "landing_input_until", 0.0):
            canvas.player_vy = -15.5 if canvas.gravity_sign > 0 else 15.5
            canvas.is_grounded = False
            canvas.used_double_jump = True
            canvas.jump_buffer_remaining = 0.0
            canvas.landing_input_until = 0.0
            canvas.redraw()
            return

        if getattr(self, "in_ladder", False):
            canvas.player_vy = -7.0 if canvas.gravity_sign > 0 else 7.0
            canvas.jump_buffer_remaining = 0.0
            return

        can_ground_jump = canvas.is_grounded or canvas.coyote_remaining > 0.0
        if can_ground_jump:
            progress = self._load_progress_data()
            progress["jumps_count"] = int(progress.get("jumps_count", 0)) + 1
            if progress["jumps_count"] >= 100:
                progress.setdefault("achievements", {}).setdefault("jump_master", {"title": "Jump Master", "description": "Jump 100 times", "unlocked": True, "unlocked_at": int(time.time())})
            self._save_progress_data(progress)
            canvas.player_vy = -5.9 if canvas.gravity_sign > 0 else 5.9
            canvas.is_grounded = False
            canvas.coyote_remaining = 0.0
            canvas.jump_buffer_remaining = 0.0
            canvas.used_double_jump = False
        else:
            in_double = any(self._player_overlaps_key(k, o)
                            for k, o in canvas._objects_by_id.get(38, ())) or canvas.zone_modes.get("double_jump", False)
            if in_double and not canvas.used_double_jump:
                canvas.player_vy = -6.2 if canvas.gravity_sign > 0 else 6.2
                canvas.used_double_jump = True
                canvas.jump_buffer_remaining = 0.0

    def _player_overlaps_key(self, key, obj):
        canvas = self.editor_canvas
        cell = canvas.cell()
        bx, by, bw, bh = canvas.object_rect(key, obj, cell)
        p = (canvas.player_x, canvas.player_y, cell-4, cell-4)
        return canvas.overlaps(p, (bx, by, bw, bh))

    def _show_notice(self, title, message):
        content = BoxLayout(orientation="vertical", spacing=10, padding=12)
        label = Label(text=str(message), font_size=17, halign="center", valign="middle")
        label.bind(size=lambda widget, _value: setattr(widget, "text_size", (widget.width, None)))
        content.add_widget(label)
        close = Button(text="OK", size_hint_y=None, height=48, font_size=18)
        content.add_widget(close)
        popup = Popup(title=str(title), content=content, size_hint=(0.82, 0.42))
        close.bind(on_release=popup.dismiss)
        popup.open()

    def _after_level_reward_navigation(self, was_community_level=False, was_builtin_level=False):
        """Return published/offline play to the main menu; editor tests return to editing."""
        self._reward_flow_active = False
        if was_community_level or was_builtin_level:
            self._community_play_mode = False
            self._community_play_row = None
            self._builtin_play_mode = False
            self.show_main_menu()
            return
        # show_win_popup() already switched gameplay off, restoring the editor UI.
        # Keep the current editor, stage, and selected design available for editing.
        self._community_play_mode = False
        self._community_play_row = None
        self._builtin_play_mode = False
        self.status_label.text = "LEVEL TEST COMPLETE - back to editing"

    def _grant_rewarded_bonus(self, bonus, popup=None, level_key=None):
        """Grant a rewarded-ad bonus once per level, persisted with the wallet."""
        if self._reward_bonus_claimed or not level_key:
            return False
        data = self._load_progress_data()
        claimed_levels = set(str(v) for v in data.get("claimed_level_ad_bonuses", []))
        normalized_key = str(level_key)
        if normalized_key in claimed_levels:
            self._reward_bonus_claimed = True
            if popup is not None:
                try: popup.dismiss()
                except Exception: pass
            self._show_notice("Bonus already collected", "The rewarded-ad bonus for this level has already been collected.")
            self._after_level_reward_navigation(self._reward_was_community, self._reward_was_builtin)
            return False
        amount = max(0, int(bonus))
        claimed_levels.add(normalized_key)
        data["claimed_level_ad_bonuses"] = sorted(claimed_levels)
        data["currency_balance"] = max(0, int(data.get("currency_balance", 0))) + amount
        saved = self._save_progress_data(data)
        if saved:
            self._reward_bonus_claimed = True
        if popup is not None:
            try: popup.dismiss()
            except Exception: pass
        if not saved:
            self._show_notice("Reward could not be saved", "Your ad was completed, but the bonus could not be saved. Please contact support.")
        else:
            self._show_notice("Bonus coins received!", f"You earned +{amount} bonus coins. This level's ad bonus cannot be claimed again.")
        self._after_level_reward_navigation(self._reward_was_community, self._reward_was_builtin)
        return saved

    def _show_rewarded_ad_for_bonus(self, bonus, popup, level_key=None):
        """Show a Unity rewarded ad; coins are granted only by event 1."""
        bridge = getattr(self, "_unity_bridge", None)
        if bridge is None:
            self._show_notice("Ads unavailable", "Unity Ads is not initialized on this device. You can still skip to the main menu.")
            return
        if self._unity_pending_reward_popup is not None:
            return
        if not level_key:
            self._show_notice("Bonus unavailable", "This level's reward could not be verified. No bonus was granted.")
            return
        data = self._load_progress_data()
        claimed_levels = set(str(v) for v in data.get("claimed_level_ad_bonuses", []))
        if str(level_key) in claimed_levels:
            self._show_notice("Bonus already collected", "The rewarded-ad bonus for this level has already been collected.")
            return
        try:
            self._unity_pending_reward_popup = popup
            self._unity_pending_bonus = int(bonus)
            self._unity_pending_level_key = str(level_key)
            bridge.showRewarded()
        except Exception as exc:
            self._unity_pending_reward_popup = None
            self._unity_pending_bonus = 0
            self._unity_pending_level_key = None
            self._show_notice("Ad unavailable", str(exc)[:180])

    def _finish_after_skip(self, popup):
        try:
            popup.dismiss()
        except Exception:
            pass
        self._after_level_reward_navigation(self._reward_was_community, self._reward_was_builtin)

    def _skip_reward_and_maybe_interstitial(self, popup):
        """The 20% interstitial roll applies only when leaving community/offline play."""
        if not (self._reward_was_community or self._reward_was_builtin):
            self._finish_after_skip(popup)
            return
        show_ad = random.random() < 0.20
        if not show_ad:
            self._finish_after_skip(popup)
            return
        bridge = getattr(self, "_unity_bridge", None)
        if bridge is None:
            self._finish_after_skip(popup)
            return
        try:
            popup.dismiss()
        except Exception:
            pass
        try:
            self._unity_pending_interstitial = True
            bridge.showInterstitial()
        except Exception:
            self._unity_pending_interstitial = False
            self._after_level_reward_navigation(self._reward_was_community, self._reward_was_builtin)

    def show_win_popup(self):
        if getattr(self, "_reward_flow_active", False):
            return
        self._reward_flow_active = True
        was_community_level = bool(getattr(self, "_community_play_mode", False))
        was_builtin_level = bool(getattr(self, "_builtin_play_mode", False))
        self._reward_was_community = was_community_level
        self._reward_was_builtin = was_builtin_level
        level_key = ""
        ad_bonus_available = False
        try:
            result = self._record_level_completion()
            base_reward = max(0, int(result.get("currency_reward", 0)))
            level_key = str(result.get("level_key") or "")
            progress_for_bonus = self._load_progress_data()
            claimed_ad_levels = set(str(v) for v in progress_for_bonus.get("claimed_level_ad_bonuses", []))
            ad_bonus_available = bool(level_key) and level_key not in claimed_ad_levels
            bonus_reward = (150 if base_reward == 0 else base_reward * 2) if ad_bonus_available else 0
            detail = (f"Level: {result['name']}\n"
                      f"Time: {result['time']:.2f} seconds\n"
                      f"Collectibles: {result['coins']} / {result['total_coins']} coins, "
                      f"{result['gems']} / {result['total_gems']} gems\n"
                      f"Coins already saved: +{base_reward}\n"
                      f"Wallet balance: {result.get('currency_balance', 0)} Coins\n"
                      f"Score: {self.editor_canvas.score}")
            if not result["saved"]:
                detail += "\nProgress could not be saved to device storage."
            newly_unlocked = [v.get("title", k) for k, v in result["unlocked"].items()]
            if newly_unlocked:
                detail += "\nAchievements unlocked: " + ", ".join(newly_unlocked)
            if was_builtin_level or was_community_level:
                leaderboard_message = self._submit_leaderboard_result(result)
                detail += "\nLeaderboard: " + leaderboard_message
            elif not self.access_token:
                detail += "\nLeaderboard: Log in to submit scores from approved levels."
        except Exception as exc:
            base_reward = 0
            bonus_reward = 0
            ad_bonus_available = False
            level_key = ""
            detail = f"You reached the end! Score: {self.editor_canvas.score}\nProgress save failed: {str(exc)[:100]}"

        # Stop gameplay before showing the choice; the original reward was saved above.
        if self.is_playing:
            self.toggle_play_mode()

        content = BoxLayout(orientation="vertical", spacing=10, padding=14)
        content.add_widget(Label(text="LEVEL COMPLETED!", font_size=27, bold=True,
                                 color=self._theme()["good"], size_hint_y=None, height=44))
        content.add_widget(Label(text=detail, font_size=15, halign="center", valign="middle"))
        if ad_bonus_available:
            content.add_widget(Label(text=f"ONE-TIME LEVEL BONUS  •  +{bonus_reward} COINS",
                                     font_size=20, bold=True, color=self._theme()["accent"],
                                     size_hint_y=None, height=42))
            watch_btn = Button(text=f"WATCH REWARDED AD  —  GET +{bonus_reward} COINS",
                               size_hint_y=None, height=58, font_size=18, bold=True,
                               background_normal="", background_color=self._theme()["good"])
        else:
            content.add_widget(Label(text="REPLAY COMPLETE  •  NO REPEAT BONUS",
                                     font_size=18, bold=True, color=self._theme()["accent"],
                                     size_hint_y=None, height=42))
            watch_btn = None
        return_to_menu = was_community_level or was_builtin_level
        skip_btn = Button(
            text="GO TO MAIN MENU" if return_to_menu else "GO BACK TO EDIT",
            size_hint_y=None, height=52, font_size=18, bold=True,
            background_normal="", background_color=self._theme()["panel"])
        popup = Popup(title="Level Complete", content=content, size_hint=(0.88, 0.78),
                      auto_dismiss=False)
        if watch_btn is not None:
            watch_btn.bind(on_release=lambda *_: self._show_rewarded_ad_for_bonus(bonus_reward, popup, level_key))
            content.add_widget(watch_btn)
        skip_btn.bind(on_release=lambda *_: self._skip_reward_and_maybe_interstitial(popup))
        content.add_widget(skip_btn)
        popup.open()

    def select_object(self, obj):
        self.selected_object = obj
        if obj.get("id") == -1:
            self.edit_tool = "delete"
            self.status_label.text = "Eraser selected: tap objects to remove them"
        else:
            self.edit_tool = "place"
            self.status_label.text = f"Brush: {obj['name']}"

    def open_objects_popup(self, *_):
        ObjectCatalogPopup(self).open()

    def clear_map(self, *_):
        self.editor_canvas.grid_data.clear()
        self.editor_canvas.active_spawn = None
        self.editor_canvas.redraw()

if __name__ == "__main__":
    LevelEditorApp().run()
