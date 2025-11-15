"""
PJSK Emoji Renderer using Playwright

This module provides async rendering functionality for PJSK emoji cards,
character lists, and role category listings using Playwright for headless
browser rendering.
"""

from __future__ import annotations

import asyncio
import io
import json
import logging
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

try:
    import importlib_resources
except ImportError:
    import importlib.resources as importlib_resources

from jinja2 import Environment, FileSystemLoader, Template
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

try:
    from .domain import CHARACTERS, CHARACTER_GROUPS
except ImportError:
    # Fallback for standalone testing
    CHARACTERS = {
        "初音未来": {"初音未来", "初音", "miku", "hatsune", "hatsune miku"},
        "星乃一歌": {"星乃一歌", "一歌", "ichika"},
        "天马咲希": {"天马咲希", "咲希", "saki"},
        "望月穗波": {"望月穗波", "穗波", "honami"},
        "日野森志步": {"日野森志步", "志步", "shiho"},
        "东云彰人": {"东云彰人", "彰人", "akito"},
        "青柳冬弥": {"青柳冬弥", "冬弥", "toya"},
        "小豆泽心羽": {"小豆泽心羽", "心羽", "kohane"},
    }
    
    CHARACTER_GROUPS = {
        "Leo/need": ["星乃一歌", "天马咲希", "望月穗波", "日野森志步"],
        "MORE MORE JUMP!": ["初音未来"],
        "Vivid BAD SQUAD": ["东云彰人", "青柳冬弥"],
        "Nightcord at 25:00": ["小豆泽心羽"],
    }

# Setup logger
logger = logging.getLogger(__name__)


class PJSKRenderer:
    """Async renderer for PJSK emoji cards and lists using Playwright."""
    
    def __init__(self, headless: bool = True):
        """Initialize the renderer.
        
        Args:
            headless: Whether to run browser in headless mode
        """
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self._playwright = None
        self._template_env: Optional[Environment] = None
        self._assets_path: Optional[Path] = None
        
    async def initialize(self) -> None:
        """Initialize the browser and template environment."""
        if self.browser is not None:
            return
            
        self._playwright = await async_playwright().start()
        self.browser = await self._playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context(
            viewport={'width': 1200, 'height': 800},
            device_scale_factor=2.0
        )
        
        # Setup template environment
        self._setup_template_environment()
        
    async def close(self) -> None:
        """Close the browser and cleanup resources."""
        if self.context:
            await self.context.close()
            self.context = None
        if self.browser:
            await self.browser.close()
            self.browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
            
    def _setup_template_environment(self) -> None:
        """Setup Jinja2 template environment with asset paths."""
        # Get assets path using importlib.resources
        try:
            assets_path = importlib_resources.files('pjsk_emoji') / 'assets'
        except Exception:
            # Fallback for development
            self._assets_path = Path(__file__).parent / 'assets'
        else:
            self._assets_path = Path(str(assets_path))
            
        template_path = self._assets_path / 'templates'
        self._template_env = Environment(
            loader=FileSystemLoader(str(template_path)),
            autoescape=True
        )
        
    def _get_asset_path(self, relative_path: str) -> str:
        """Get absolute path to an asset file.
        
        Args:
            relative_path: Relative path from assets directory
            
        Returns:
            Absolute file:// URL or path
        """
        asset_file = self._assets_path / relative_path
        if asset_file.exists():
            return f"file://{asset_file.absolute()}"
        else:
            # Return fallback path
            return f"file://{self._assets_path / relative_path}"
            
    async def render_emoji_card(
        self,
        text: str,
        character_name: str,
        font_size: int = 42,
        line_spacing: float = 1.2,
        curve_enabled: bool = False,
        offset_x: int = 0,
        offset_y: int = 0,
        curve_intensity: float = 0.5,
        enable_shadow: bool = True,
        emoji_set: str = "apple"
    ) -> bytes:
        """Render a PJSK emoji card.
        
        Args:
            text: Text content to render
            character_name: Character name
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
        await self._ensure_initialized()
        
        # Get character data
        character_data = self._get_character_data(character_name)
        
        # Setup curve transform
        curve_transform = ""
        if curve_enabled:
            curve_transform = f"rotate({curve_intensity * 5}deg)"
        
        # Setup text shadow
        text_shadow = "2px 2px 4px rgba(0, 0, 0, 0.5)" if enable_shadow else "none"
        
        # Prepare template variables
        template_vars = {
            'text_content': text.replace('\n', '<br>'),
            'character_name': character_data['name'],
            'character_group': character_data['group'],
            'character_image_path': self._get_asset_path(character_data['image_path']),
            'font_size': font_size,
            'line_spacing': line_spacing,
            'offset_x': offset_x,
            'offset_y': offset_y,
            'curve_transform': curve_transform,
            'text_shadow': text_shadow,
            'emoji_set': emoji_set,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Render template
        template = self._template_env.get_template('card_template.html')
        html_content = template.render(**template_vars)
        
        # Render to image
        return await self._render_html_to_image(html_content, width=800, height=600)
        
    async def render_character_list(
        self,
        list_type: str = "all",
        group_filter: Optional[str] = None
    ) -> bytes:
        """Render a character list.
        
        Args:
            list_type: Type of list ("all", "groups", "group_detail")
            group_filter: Filter by specific group name
            
        Returns:
            PNG image bytes
        """
        await self._ensure_initialized()
        
        # Generate content based on list type
        if list_type == "all":
            title = "所有角色"
            subtitle = f"共 {len(CHARACTERS)} 位角色"
            content_html = self._generate_all_characters_html()
        elif list_type == "groups":
            title = "角色分类"
            subtitle = f"共 {len(CHARACTER_GROUPS)} 个组合"
            content_html = self._generate_group_list_html()
        elif list_type == "group_detail" and group_filter:
            group_data = CHARACTER_GROUPS.get(group_filter)
            if not group_data:
                raise ValueError(f"Unknown group: {group_filter}")
            title = f"组合详情 - {group_filter}"
            subtitle = f"共 {len(group_data)} 位成员"
            content_html = self._generate_group_detail_html(group_filter, group_data)
        else:
            raise ValueError(f"Invalid list_type: {list_type}")
            
        # Prepare template variables
        template_vars = {
            'page_title': title,
            'page_subtitle': subtitle,
            'content_html': content_html,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Render template
        template = self._template_env.get_template('list_template.html')
        html_content = template.render(**template_vars)
        
        # Render to image
        return await self._render_html_to_image(html_content, width=1200, height=800)
        
    async def _render_html_to_image(
        self,
        html_content: str,
        width: int,
        height: int
    ) -> bytes:
        """Render HTML content to PNG image.
        
        Args:
            html_content: HTML content to render
            width: Image width in pixels
            height: Image height in pixels
            
        Returns:
            PNG image bytes
        """
        if not self.context:
            raise RuntimeError("Renderer not initialized")
            
        # Create a new page
        page = await self.context.new_page()
        
        try:
            # Set viewport size
            await page.set_viewport_size({'width': width, 'height': height})
            
            # Set content
            await page.set_content(html_content)
            
            # Wait for content to load
            await page.wait_for_load_state('networkidle')
            
            # Take screenshot
            screenshot = await page.screenshot(
                type='png',
                full_page=False,
                clip={'x': 0, 'y': 0, 'width': width, 'height': height}
            )
            
            return screenshot
            
        finally:
            await page.close()
            
    async def _ensure_initialized(self) -> None:
        """Ensure the renderer is initialized."""
        if self.browser is None:
            await self.initialize()
            
    def _get_character_data(self, character_name: str) -> Dict:
        """Get character data by name.
        
        Args:
            character_name: Character name
            
        Returns:
            Character data dictionary
        """
        # Load character data from JSON
        characters_file = self._assets_path / 'characters.json'
        if characters_file.exists():
            with open(characters_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                characters = data['characters']
        else:
            # Fallback to in-memory data
            characters = {}
            for name, aliases in CHARACTERS.items():
                characters[name] = {
                    'name': name,
                    'aliases': list(aliases),
                    'image_path': f'emoji_images/{name.lower().replace(" ", "_")}.png',
                    'group': 'Unknown'
                }
                
        return characters.get(character_name, {
            'name': character_name,
            'group': 'Unknown',
            'image_path': 'emoji_images/default.png'
        })
        
    def _generate_all_characters_html(self) -> str:
        """Generate HTML for all characters list."""
        html_parts = ['<div class="character-grid">']
        
        for character_name in CHARACTERS.keys():
            character_data = self._get_character_data(character_name)
            aliases = ', '.join(character_data.get('aliases', [])[:3])  # Show first 3 aliases
            
            html_parts.append(f'''
                <div class="character-card">
                    <div class="character-name">{character_name}</div>
                    <div class="character-group">{character_data.get('group', 'Unknown')}</div>
                    <div class="character-aliases">别名: {aliases}</div>
                </div>
            ''')
            
        html_parts.append('</div>')
        return ''.join(html_parts)
        
    def _generate_group_list_html(self) -> str:
        """Generate HTML for groups list."""
        html_parts = []
        
        for group_name, members in CHARACTER_GROUPS.items():
            html_parts.append(f'''
                <div class="group-section">
                    <div class="group-title" style="border-color: #{self._get_group_color(group_name)}">
                        {group_name} ({len(members)}人)
                    </div>
                    <div class="character-grid">
            ''')
            
            for member in members:
                html_parts.append(f'''
                    <div class="character-card">
                        <div class="character-name">{member}</div>
                        <div class="character-group">{group_name}</div>
                    </div>
                ''')
                
            html_parts.append('</div></div>')
            
        return ''.join(html_parts)
        
    def _generate_group_detail_html(self, group_name: str, members: List[str]) -> str:
        """Generate HTML for group detail view."""
        html_parts = ['<div class="character-grid">']
        
        for member in members:
            character_data = self._get_character_data(member)
            aliases = ', '.join(character_data.get('aliases', [])[:3])
            
            html_parts.append(f'''
                <div class="character-card">
                    <div class="character-name">{member}</div>
                    <div class="character-group">{group_name}</div>
                    <div class="character-aliases">别名: {aliases}</div>
                </div>
            ''')
            
        html_parts.append('</div>')
        return ''.join(html_parts)
        
    def _get_group_color(self, group_name: str) -> str:
        """Get color code for a group."""
        colors = {
            "Leo/need": "FF6B9D",
            "MORE MORE JUMP!": "39C5BB", 
            "Vivid BAD SQUAD": "FF6B35",
            "Nightcord at 25:00": "E74C3C"
        }
        return colors.get(group_name, "666666")


class RendererManager:
    """Manager class for renderer lifecycle."""
    
    def __init__(self):
        self._renderer: Optional[PJSKRenderer] = None
        
    async def get_renderer(self) -> PJSKRenderer:
        """Get or create renderer instance."""
        if self._renderer is None:
            self._renderer = PJSKRenderer()
            await self._renderer.initialize()
        return self._renderer
        
    async def close(self) -> None:
        """Close the renderer."""
        if self._renderer:
            await self._renderer.close()
            self._renderer = None


# Global renderer manager instance
renderer_manager = RendererManager()


async def get_renderer() -> PJSKRenderer:
    """Get the global renderer instance."""
    return await renderer_manager.get_renderer()


async def render_emoji_card(**kwargs) -> bytes:
    """Convenience function to render an emoji card."""
    renderer = await get_renderer()
    return await renderer.render_emoji_card(**kwargs)


async def render_character_list(**kwargs) -> bytes:
    """Convenience function to render a character list."""
    renderer = await get_renderer()
    return await renderer.render_character_list(**kwargs)