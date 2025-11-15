"""Shared domain logic and validation helpers for PjskEmojiMaker."""

from __future__ import annotations

import io
from typing import Dict, Iterable, List, Optional, Tuple

from astrbot.api import logger
from renderer import MockRenderer


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


def get_character_image_buffer(
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
    renderer = MockRenderer()
    
    try:
        image_bytes = renderer.render_card(
            text=text,
            font_size=font_size,
            line_spacing=line_spacing,
            curve_enabled=curve_enabled,
            offset_x=offset_x,
            offset_y=offset_y,
            role=character_name,
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
