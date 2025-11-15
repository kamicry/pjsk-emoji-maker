"""Shared utilities for PJSk card rendering and calculations."""

from __future__ import annotations

import re
from typing import List, Tuple


def calculateOffsets(text: str, font_size: int, line_spacing: float) -> Tuple[int, int]:
    """Calculate optimal X/Y offsets for text positioning.
    
    Args:
        text: The text content to render
        font_size: Font size in pixels  
        line_spacing: Line spacing multiplier
        
    Returns:
        Tuple of (offset_x, offset_y) in pixels
    """
    lines = text.split('\n')
    line_count = len(lines)
    
    # Base offsets proportional to font size
    base_offset_x = font_size // 4
    base_offset_y = font_size // 2
    
    # Adjust Y offset based on line count and spacing
    line_height = int(font_size * line_spacing)
    total_height = line_height * line_count
    
    # Center vertically in typical card space (600px height)
    card_height = 600
    offset_y = (card_height - total_height) // 2
    
    # Clamp to reasonable bounds
    offset_y = max(-240, min(240, offset_y))
    
    return base_offset_x, offset_y


def calculateFontSize(text: str, target_width: int = 400, min_size: int = 18, max_size: int = 84) -> int:
    """Calculate optimal font size to fit text within target width.
    
    Args:
        text: Text to measure
        target_width: Target width in pixels
        min_size: Minimum font size
        max_size: Maximum font size
        
    Returns:
        Calculated font size
    """
    if not text:
        return max_size
    
    # Simple heuristic: estimate character width as 60% of font size
    longest_line = findLongestLine(text)
    estimated_width = len(longest_line) * 0.6 * max_size
    
    if estimated_width <= target_width:
        return max_size
    
    # Scale down to fit
    scale_factor = target_width / estimated_width
    calculated_size = int(max_size * scale_factor)
    
    return max(min_size, min(max_size, calculated_size))


def findLongestLine(text: str) -> str:
    """Find the longest line in multiline text.
    
    Args:
        text: Multiline text
        
    Returns:
        The longest line
    """
    if not text:
        return ""
    
    lines = text.split('\n')
    # Filter out empty lines when finding the longest
    non_empty_lines = [line for line in lines if line.strip()]
    if not non_empty_lines:
        return ""
    
    return max(non_empty_lines, key=len)


def calculateTextDimensions(text: str, font_size: int, line_spacing: float) -> Tuple[int, int]:
    """Calculate the dimensions of rendered text.
    
    Args:
        text: Text to measure
        font_size: Font size in pixels
        line_spacing: Line spacing multiplier
        
    Returns:
        Tuple of (width, height) in pixels
    """
    if not text:
        return 0, 0
    
    lines = text.split('\n')
    longest_line = findLongestLine(text)
    
    # Estimate width: character count * font size * 0.6 (approximate character width ratio)
    width = int(len(longest_line) * font_size * 0.6)
    
    # Calculate height: line count * font size * line spacing
    height = int(len(lines) * font_size * line_spacing)
    
    return width, height


def sanitizeText(text: str, max_length: int = 120) -> str:
    """Sanitize and truncate text for rendering.
    
    Args:
        text: Input text
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length-3] + "..."
    
    return text


def validateCurveIntensity(intensity: float) -> float:
    """Validate and clamp curve intensity.
    
    Args:
        intensity: Curve intensity value
        
    Returns:
        Clamped intensity value (0.0 to 1.0)
    """
    return max(0.0, min(1.0, intensity))


def parseKoishiFlags(command_args: str) -> dict:
    """Parse Koishi-style command flags.
    
    Args:
        command_args: Command arguments string
        
    Returns:
        Dictionary of parsed options
    """
    if not command_args:
        return {}
    
    # Simple flag parser for -n, -x, -y, -r, -s, -l, -c, --daf
    flags = {
        'text': None,
        'offset_x': None,
        'offset_y': None, 
        'role': None,
        'font_size': None,
        'line_spacing': None,
        'curve': None,
        'default_font': False
    }
    
    # Split by spaces but keep quoted text together
    parts = re.findall(r'(?:[^\s"]+|"[^"]*")+', command_args)
    
    i = 0
    while i < len(parts):
        part = parts[i].strip('"')
        
        if part == '-n' and i + 1 < len(parts):
            flags['text'] = parts[i + 1].strip('"')
            i += 2
        elif part == '-x' and i + 1 < len(parts):
            try:
                flags['offset_x'] = int(parts[i + 1])
            except ValueError:
                pass
            i += 2
        elif part == '-y' and i + 1 < len(parts):
            try:
                flags['offset_y'] = int(parts[i + 1])
            except ValueError:
                pass
            i += 2
        elif part == '-r' and i + 1 < len(parts):
            flags['role'] = parts[i + 1].strip('"')
            i += 2
        elif part == '-s' and i + 1 < len(parts):
            try:
                flags['font_size'] = int(parts[i + 1])
            except ValueError:
                pass
            i += 2
        elif part == '-l' and i + 1 < len(parts):
            try:
                flags['line_spacing'] = float(parts[i + 1])
            except ValueError:
                pass
            i += 2
        elif part == '-c':
            flags['curve'] = True
            i += 1
        elif part == '--daf':
            flags['default_font'] = True
            i += 1
        else:
            # Unrecognized flag, skip
            i += 1
    
    return flags


def applyDefaults(options: dict, defaults: dict) -> dict:
    """Apply default values to options.
    
    Args:
        options: Parsed options
        defaults: Default values
        
    Returns:
        Options with defaults applied
    """
    result = {}
    
    # Start with defaults
    for key, value in defaults.items():
        result[key] = value
    
    # Override with options (including None values)
    for key, value in options.items():
        result[key] = value
    
    return result