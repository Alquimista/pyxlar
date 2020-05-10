#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pyxlar - Pixel Art Editor
"""
from pyxlar.app import PyxlarApp
from kivy.config import Config
from kivy.core.window import Window


def main():
    Window.clearcolor = (0.22, 0.22, 0.22, 1)
    Config.set('input', 'mouse', 'mouse,disable_multitouch')

    PyxlarApp().run()


if __name__ == "__main__":
    main()
