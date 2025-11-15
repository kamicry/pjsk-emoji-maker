"""
AstrBot PJSk Emoji Maker Plugin

A plugin for creating Project SEKAI character emoji cards with customizable text and styling.
"""

__version__ = "2.0.0"
__author__ = "PJSk Community"
__all__ = ["PjskEmojiMaker"]

try:
    from .main import PjskEmojiMaker
    __all__ = ["PjskEmojiMaker"]
except ImportError:
    pass
