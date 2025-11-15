"""
AstrBot Hello World Plugin

A simple example plugin demonstrating basic AstrBot functionality.
"""

__version__ = "1.0.0"
__author__ = "AstrBot Community"
__all__ = ["MyPlugin"]

try:
    from main import MyPlugin
except ImportError:
    pass
