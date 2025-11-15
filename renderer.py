"""Mock renderer for PJSk card generation."""

from __future__ import annotations

import io
import time
from typing import Optional

import numpy as np
from PIL import Image, ImageDraw, ImageFont


class MockRenderer:
    """Mock renderer that simulates card generation."""
    
    def __init__(self):
        self.render_count = 0
    
    def render_card(
        self,
        text: str,
        font_size: int = 42,
        line_spacing: float = 1.2,
        curve_enabled: bool = False,
        offset_x: int = 0,
        offset_y: int = 0,
        role: str = "初音未来",
        curve_intensity: float = 0.5,
        enable_shadow: bool = True,
        emoji_set: str = "apple"
    ) -> bytes:
        """Render a PJSk card with the given parameters.
        
        Args:
            text: Text content to render
            font_size: Font size in pixels
            line_spacing: Line spacing multiplier
            curve_enabled: Whether to apply curve effect
            offset_x: X offset in pixels
            offset_y: Y offset in pixels
            role: Character role
            curve_intensity: Intensity of curve effect (0.0-1.0)
            enable_shadow: Whether to add text shadow
            emoji_set: Emoji set to use
            
        Returns:
            Image bytes in PNG format
        """
        self.render_count += 1
        
        # Create a mock image (800x600 typical card size)
        width, height = 800, 600
        image = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # Draw background gradient (mock)
        for y in range(height):
            color_value = int(240 + (15 * y / height))
            draw.line([(0, y), (width, y)], fill=(color_value, color_value, 255))
        
        # Draw character placeholder (mock)
        char_x, char_y = 100, 150
        char_size = 200
        draw.ellipse([char_x, char_y, char_x + char_size, char_y + char_size], 
                    fill=(200, 200, 200), outline=(150, 150, 150), width=2)
        
        # Add character name
        try:
            # Try to use a default font
            font = ImageFont.load_default()
        except:
            font = None
        
        if font:
            draw.text((char_x + 50, char_y + char_size + 20), role, 
                     fill=(50, 50, 50), font=font)
        
        # Process and draw text
        if text:
            lines = text.split('\n')
            line_height = int(font_size * line_spacing)
            
            # Starting position with offsets
            text_x = 400 + offset_x
            text_y = 100 + offset_y
            
            for i, line in enumerate(lines):
                y_pos = text_y + (i * line_height)
                
                # Apply curve effect if enabled
                if curve_enabled:
                    # Simple curve: adjust x position based on line index
                    curve_offset = int(curve_intensity * 20 * np.sin(i * 0.5))
                    x_pos = text_x + curve_offset
                else:
                    x_pos = text_x
                
                # Draw shadow if enabled
                if enable_shadow:
                    shadow_color = (200, 200, 200)
                    draw.text((x_pos + 2, y_pos + 2), line, fill=shadow_color, font=font)
                
                # Draw main text
                draw.text((x_pos, y_pos), line, fill=(0, 0, 0), font=font)
        
        # Add metadata (mock)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        metadata_text = f"Render #{self.render_count} | {timestamp} | {emoji_set}"
        if font:
            draw.text((10, height - 25), metadata_text, fill=(100, 100, 100), font=font)
        
        # Convert to bytes
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return img_bytes.getvalue()
    
    def get_render_info(self) -> dict:
        """Get information about the renderer."""
        return {
            'renders_completed': self.render_count,
            'renderer_type': 'mock',
            'supported_formats': ['PNG'],
            'max_size': (1920, 1080),
            'supported_emoji_sets': ['apple', 'google', 'twitter', 'facebook']
        }