#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pyxlar - Pixel Art Editor
"""
import pathlib

from kivy.app import App
from kivy.lang.builder import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.properties import ListProperty, BoundedNumericProperty, ObjectProperty
from kivy.graphics import Color, Line, SmoothLine, Ellipse
from kivy.uix.relativelayout import RelativeLayout


basepath = pathlib.Path(__file__).resolve().parent
ui_path = basepath.joinpath('ui')
palettes_path = basepath.joinpath('palettes')


for kv in ui_path.rglob("*.kv"):
    Builder.load_file(str(kv))


def rgb_to_rgb01(rgb):
    return [int(c)/255 for c in rgb]


def rgb_to_hex(rgb):
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def rgb01_to_rgb(rgb):
    return [round(clamp(float(c), 0, 1)*255) for c in rgb]


def rgb01_to_hex(rgb01):
    return rgb_to_hex(rgb01_to_rgb(rgb01))


def clamp(n, minvalue, maxvalue):
    return max(minvalue, min(n, maxvalue))


def read_gimp_palettes():
    palettes = []

    for path in pathlib.Path(palettes_path).rglob("*.gpl"):
        colors = []
        name = path.stem
        columns = 0
        with path.open('r') as f:
            header_magic = next(f)
            assert header_magic.strip() == 'GIMP Palette', '{0}: Incorrect ' \
                'header at the first line'.format(filename)
            for line in f:
                line = line.strip()
                if line.startswith('#') or not line:
                    continue
                key_value = line.split(":", 1)
                if len(key_value) == 1:
                    color = line.split(maxsplit=3)
                    color_name = ""
                    if len(color) == 4:
                        color_name = color[3]
                    colors.append([rgb_to_rgb01(color[:3]), color_name])
                else:
                    key, value = key_value
                    key = key.lower()
                    if key == 'name:':
                        name = value
                    elif key == 'columns:':
                        columns = int(value)
                    else:
                        continue
        if len(colors) == 0:
            colors.append([0, 0, 0, ""])
            colors.append([1, 1, 1, ""])

        palette = {
            'name': name,
            'columns': columns,
            'colors': colors
        }

        palettes.append(palette)

    return palettes


class ColorSwatch(ToggleButtonBehavior, Widget):
    border_size = BoundedNumericProperty(1, min=0.1)
    border_color = ListProperty([])
    background_color = ListProperty([])


class ColorLabel(Label):
    background_color = ListProperty([0, 0, 0])


class Paint_brush(Widget):
    brush_color = ListProperty([0, 0, 0])
    brush_size = BoundedNumericProperty(1, min=1)


class CanvasPaint(Widget):
    background_color = ListProperty([1, 1, 1])
    brush_color = ListProperty([0, 0, 0])
    brush_size = BoundedNumericProperty(1, min=1)

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return
        pb = Paint_brush()
        pb.brush_color = self.brush_color
        pb.brush_size = self.brush_size
        pb.center = touch.pos
        self.add_widget(pb)

    # On mouse movement how Paint_brush behave
    def on_touch_move(self, touch):
        if not self.collide_point(*touch.pos):
            return
        pb = Paint_brush()
        pb.brush_color = self.brush_color
        pb.brush_size = self.brush_size
        pb.center = touch.pos
        self.add_widget(pb)


class MainUI(BoxLayout):
    grid = ObjectProperty(None)
    brush_color = ListProperty([0, 0, 0])
    brush_size = BoundedNumericProperty(1, min=1)


class PyxlarApp(App):

    def build_config(self, config):
        config.setdefaults('Colors', {
            'palette': 'toxic-raven',
        })

    def build(self):

        palette_name = self.config.get('Colors', 'palette')
        self.ui = MainUI()

        for p in read_gimp_palettes():
            if p['name'] == palette_name:
                for color, _ in p["colors"]:
                    btnColorSwatch = ColorSwatch(
                        group='color',
                        background_color=color)
                    btnColorSwatch.bind(on_press=self.brush_color)
                    self.ui.gridPalette.add_widget(btnColorSwatch)
                break

        self.ui.clearButton.bind(on_press=self.clear_canvas)
        self.ui.brushSizeSlider.bind(value=self.brush_size)
        # self.ui.undoButton.bind(on_press=self.undo_canvas)

        return self.ui

    # def undo_canvas(self, instance):
    #     if self.ui.canvasPaint.undo_list:
    #         self.ui.canvasPaint.canvas.remove(self.ui.canvasPaint.undo_list.pop())

    def clear_canvas(self, instance):
        self.ui.canvasPaint.canvas.clear()

    def brush_size(self, instance, value):
        self.ui.brush_size = value

    def brush_color(self, instance):
        self.ui.brush_color = instance.background_color
        rgb = rgb01_to_rgb(instance.background_color)
        rgb_str = "rgb({:d}, {:d}, {:d})".format(*rgb)
        self.ui.colorLabel.text = "{:s}\n{:s}".format(rgb_to_hex(rgb), rgb_str)
