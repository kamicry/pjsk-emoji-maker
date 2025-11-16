"""Shared domain logic and validation helpers for PjskEmojiMaker."""

from __future__ import annotations

import io
import json
import logging
import os
from typing import Dict, Iterable, List, Optional, Tuple

try:
    from astrbot.api import logger
except ImportError:
    logger = logging.getLogger(__name__)


# Character database
CHARACTERS: Dict[str, Iterable[str]] = {
    "初音未来": {"初音未来", "初音", "miku", "hatsune", "hatsune miku"},
    "星乃一歌": {"星乃一歌", "一歌", "ichika"},
    "天马咲希": {"天马咲希", "咲希", "saki"},
    "望月穗波": {"望月穗波", "穗波", "honami"},
    "日野森志步": {"日野森志步", "志步", "shiho"},
    "东云彰人": {"东云彰人", "彰人", "akito"},
    "青柳冬弥": {"青柳冬弥", "冬弥", "toya"},
    "小豆泽心羽": {"小豆泽心羽", "心羽", "kohane"},
}

# Character groups by category
CHARACTER_GROUPS: Dict[str, List[str]] = {
    "Leo/need": ["星乃一歌", "天马咲希", "望月穗波", "日野森志步"],
    "MORE MORE JUMP!": ["初音未来"],
    "Vivid BAD SQUAD": ["东云彰人", "青柳冬弥"],
    "Nightcord at 25:00": ["小豆泽心羽"],
}

CHARACTER_NAMES = list(CHARACTERS.keys())


def load_characters_data() -> Dict:
    """Load characters data from JSON file."""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(current_dir, 'assets')
        characters_file = os.path.join(assets_dir, 'characters.json')
        
        with open(characters_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data
    except Exception as e:
        logger.error(f"Failed to load characters data: {e}")
        return {}


def get_character_thumbnail_path(character_name: str) -> Optional[str]:
    """Get thumbnail path for a character."""
    try:
        data = load_characters_data()
        characters = data.get('characters', {})
        
        for name, info in characters.items():
            if name == character_name:
                thumbnail_path = info.get('list_thumbnail_path')
                if thumbnail_path:
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    assets_dir = os.path.join(current_dir, 'assets')
                    return os.path.join(assets_dir, thumbnail_path)
        
        return None
    except Exception as e:
        logger.error(f"Failed to get thumbnail path for {character_name}: {e}")
        return None


def get_all_character_thumbnails() -> List[Tuple[str, str]]:
    """Get all character thumbnails as (name, path) tuples."""
    try:
        data = load_characters_data()
        characters = data.get('characters', {})
        thumbnails = []
        
        for name, info in characters.items():
            thumbnail_path = info.get('list_thumbnail_path')
            if thumbnail_path:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                assets_dir = os.path.join(current_dir, 'assets')
                full_path = os.path.join(assets_dir, thumbnail_path)
                
                if os.path.exists(full_path):
                    thumbnails.append((name, full_path))
        
        return thumbnails
    except Exception as e:
        logger.error(f"Failed to get character thumbnails: {e}")
        return []


def build_character_lookup(characters: Dict[str, Iterable[str]]) -> Dict[str, str]:
    """Build a lookup table mapping aliases to canonical character names.
    
    Args:
        characters: Dictionary mapping canonical names to aliases
        
    Returns:
        Lookup dictionary for fast character resolution
    """
    lookup: Dict[str, str] = {}
    for canonical, aliases in characters.items():
        for alias in aliases:
            lookup[alias] = canonical
            lookup[alias.lower()] = canonical
    return lookup


def get_character_name(raw_input: str) -> Optional[str]:
    """Resolve a user input string to a canonical character name.
    
    Args:
        raw_input: User input (can be name, alias, etc.)
        
    Returns:
        Canonical character name, or None if not found
    """
    if not raw_input:
        return None
    
    lookup = build_character_lookup(CHARACTERS)
    stripped = raw_input.strip()
    lowered = stripped.lower()
    
    if stripped in lookup:
        return lookup[stripped]
    if lowered in lookup:
        return lookup[lowered]
    
    return None


async def get_character_image_buffer(
    character_name: str,
    text: str = "",
    font_size: int = 42,
    line_spacing: float = 1.2,
    curve_enabled: bool = False,
    offset_x: int = 0,
    offset_y: int = 0,
    curve_intensity: float = 0.5,
    enable_shadow: bool = True,
    emoji_set: str = "apple",
) -> bytes:
    """Generate image buffer for a character with the given parameters.
    
    Args:
        character_name: Canonical character name
        text: Text to render on the card
        font_size: Font size in pixels
        line_spacing: Line spacing multiplier
        curve_enabled: Whether to apply curve effect
        offset_x: X offset in pixels
        offset_y: Y offset in pixels
        curve_intensity: Intensity of curve effect (0.0-1.0)
        enable_shadow: Whether to add text shadow
        emoji_set: Emoji set to use
        
    Returns:
        PNG image bytes
    """
    from .renderer import get_renderer
    
    try:
        renderer = await get_renderer()
        image_bytes = await renderer.render_emoji_card(
            text=text,
            character_name=character_name,
            font_size=font_size,
            line_spacing=line_spacing,
            curve_enabled=curve_enabled,
            offset_x=offset_x,
            offset_y=offset_y,
            curve_intensity=curve_intensity,
            enable_shadow=enable_shadow,
            emoji_set=emoji_set,
        )
        return image_bytes
    except Exception as e:
        logger.error("Failed to generate image buffer: %s", str(e))
        raise


def format_character_list() -> str:
    """Format all characters as a displayable list.
    
    Returns:
        Formatted string with character list
    """
    lines = ["📋 所有角色（共 {} 人）：".format(len(CHARACTER_NAMES)), ""]
    for idx, char in enumerate(CHARACTER_NAMES, 1):
        lines.append(f"{idx}. {char}")
    return "\n".join(lines)


def format_character_groups() -> str:
    """Format characters organized by group/category.
    
    Returns:
        Formatted string with grouped characters
    """
    lines = ["🎭 角色分类：", ""]
    for group_name, members in CHARACTER_GROUPS.items():
        lines.append(f"【{group_name}】")
        for member in members:
            lines.append(f"  • {member}")
        lines.append("")
    return "\n".join(lines)


async def get_character_list_image(
    list_type: str = "all",
    group_filter: Optional[str] = None
) -> bytes:
    """Generate image buffer for character list.
    
    Args:
        list_type: Type of list ("all", "groups", "group_detail")
        group_filter: Filter by specific group name
        
    Returns:
        PNG image bytes
    """
    from .renderer import get_renderer
    
    try:
        renderer = await get_renderer()
        image_bytes = await renderer.render_character_list(
            list_type=list_type,
            group_filter=group_filter
        )
        return image_bytes
    except Exception as e:
        logger.error("Failed to generate list image: %s", str(e))
        raise


def create_character_selection_grid() -> bytes:
    """Create a grid image with character thumbnails for selection.
    
    Returns:
        PNG image bytes with character thumbnails arranged in a grid
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Get all character thumbnails
        thumbnails = get_all_character_thumbnails()
        
        if not thumbnails:
            # Fallback: create a simple text image
            return _create_text_fallback_image()
        
        # Grid layout: 3 columns, 3 rows (8 characters + 1 empty)
        cols = 3
        rows = 3
        thumbnail_size = 100
        padding = 10
        label_height = 30
        
        grid_width = cols * (thumbnail_size + padding) + padding
        grid_height = rows * (thumbnail_size + padding + label_height) + padding
        
        # Create white background
        grid_image = Image.new('RGB', (grid_width, grid_height), 'white')
        draw = ImageDraw.Draw(grid_image)
        
        # Try to load a font
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        # Place thumbnails in grid
        for idx, (name, path) in enumerate(thumbnails):
            if idx >= 8:  # Only show first 8 characters
                break
            
            row = idx // cols
            col = idx % cols
            
            x = padding + col * (thumbnail_size + padding)
            y = padding + row * (thumbnail_size + padding + label_height)
            
            # Load and resize thumbnail
            try:
                thumbnail = Image.open(path)
                thumbnail = thumbnail.resize((thumbnail_size, thumbnail_size), Image.Resampling.LANCZOS)
                grid_image.paste(thumbnail, (x, y))
            except Exception as e:
                logger.error(f"Failed to load thumbnail {path}: {e}")
                # Draw placeholder
                draw.rectangle([x, y, x + thumbnail_size, y + thumbnail_size], fill='lightgray')
                draw.text((x + thumbnail_size//2, y + thumbnail_size//2), f"{idx+1}", 
                         fill='black', font=font, anchor='mm')
            
            # Add number label
            label_text = f"{idx + 1}. {name}"
            label_y = y + thumbnail_size + 5
            draw.text((x + thumbnail_size//2, label_y), label_text, 
                     fill='black', font=font, anchor='mm')
        
        # Convert to bytes
        img_bytes = io.BytesIO()
        grid_image.save(img_bytes, format='PNG', optimize=True)
        img_bytes.seek(0)
        
        return img_bytes.getvalue()
        
    except Exception as e:
        logger.error(f"Failed to create character selection grid: {e}")
        return _create_text_fallback_image()


def _create_text_fallback_image() -> bytes:
    """Create a text fallback image when thumbnails are not available."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a simple text image
        width, height = 400, 300
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        text_lines = [
            "角色选择列表",
            "",
            "1. 初音未来",
            "2. 星乃一歌", 
            "3. 天马咲希",
            "4. 望月穗波",
            "5. 日野森志步",
            "6. 东云彰人",
            "7. 青柳冬弥",
            "8. 小豆泽心羽"
        ]
        
        y_offset = 20
        for line in text_lines:
            draw.text((20, y_offset), line, fill='black', font=font)
            y_offset += 25
        
        # Convert to bytes
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='PNG', optimize=True)
        img_bytes.seek(0)
        
        return img_bytes.getvalue()
        
    except Exception as e:
        logger.error(f"Failed to create fallback image: {e}")
        # Return empty PNG as last resort
        return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'


def format_character_detail(character_name: str) -> str:
    """Format detailed information about a character.
    
    Args:
        character_name: Canonical character name
        
    Returns:
        Formatted string with character details
    """
    aliases = ", ".join(list(CHARACTERS.get(character_name, [])))
    
    group = ""
    for group_name, members in CHARACTER_GROUPS.items():
        if character_name in members:
            group = group_name
            break
    
    lines = [f"👤 角色信息 - {character_name}", ""]
    lines.append(f"别名：{aliases}")
    if group:
        lines.append(f"所属组合：{group}")
    lines.append("")
    lines.append("发送 /pjsk 开始创建表情包吧！")
    
    return "\n".join(lines)
