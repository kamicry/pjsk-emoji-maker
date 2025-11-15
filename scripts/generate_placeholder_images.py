#!/usr/bin/env python3
"""
Generate placeholder character images for development purposes.
"""

import os
from PIL import Image, ImageDraw, ImageFont
import json

def load_character_data():
    """Load character data from JSON file."""
    with open('pjsk_emoji/assets/characters.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['characters']

def generate_placeholder_image(character_name, color, output_path):
    """Generate a placeholder image for a character."""
    # Create 400x400 image with transparent background
    image = Image.new('RGBA', (400, 400), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    
    # Parse color from hex
    if color.startswith('#'):
        color = color[1:]
    rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
    
    # Draw a colored circle as placeholder
    center = 200
    radius = 150
    draw.ellipse([center-radius, center-radius, center+radius, center+radius], 
                fill=rgb + (200,), outline=rgb + (255,), width=3)
    
    # Add character name
    try:
        # Try to use a default font
        font = ImageFont.load_default()
    except:
        font = None
    
    if font:
        # Draw text
        text_bbox = draw.textbbox((0, 0), character_name, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        text_x = (400 - text_width) // 2
        text_y = (400 - text_height) // 2
        
        # Add text shadow
        draw.text((text_x + 2, text_y + 2), character_name, 
                fill=(0, 0, 0, 128), font=font, anchor="mm")
        # Add main text
        draw.text((text_x, text_y), character_name, 
                fill=(255, 255, 255, 255), font=font, anchor="mm")
    
    # Save image
    image.save(output_path, 'PNG')
    print(f"Generated: {output_path}")

def main():
    """Generate all placeholder character images."""
    characters = load_character_data()
    output_dir = 'pjsk_emoji/assets/emoji_images'
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    for character_id, data in characters.items():
        output_path = os.path.join(output_dir, f"{data['id']}.png")
        generate_placeholder_image(data['name'], data['color'], output_path)
    
    print(f"Generated {len(characters)} placeholder character images.")

if __name__ == '__main__':
    main()