"""Data models for PJSk plugin."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RenderState:
    """Runtime configuration for a user's PJSk card rendering."""

    text: str
    font_size: int
    line_spacing: float
    curve_enabled: bool
    offset_x: int
    offset_y: int
    role: str