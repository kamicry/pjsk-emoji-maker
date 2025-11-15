# PJSK Renderer Setup Guide

## Overview

The PJSK Emoji Renderer is a Python-based rendering system that uses Playwright to generate high-quality emoji cards and character lists. This document explains how to set up and use the renderer.

## Architecture

### Components

1. **Renderer Core** (`pjsk_emoji/renderer.py`): Main rendering engine using Playwright
2. **Assets** (`pjsk_emoji/assets/`): Static resources including templates, images, and fonts
3. **Domain Logic** (`pjsk_emoji/domain.py`): Character data and helper functions
4. **Templates** (`pjsk_emoji/assets/templates/`): Jinja2 HTML templates for rendering

### Rendering Pipeline

1. **Template Preparation**: Jinja2 templates are loaded and cached
2. **HTML Generation**: Template variables are populated with character data and user parameters
3. **Browser Rendering**: Playwright renders the HTML to PNG using a headless browser
4. **Output**: PNG bytes are returned for further processing

## Installation

### Dependencies

Add these to your `requirements.txt`:

```txt
playwright>=1.40.0
jinja2>=3.0.0
importlib-resources>=6.0.0
Pillow>=9.0.0
```

### System Dependencies

Install Playwright browser dependencies:

```bash
# For Ubuntu/Debian
sudo apt-get install -y libnspr4 libnss3 libatk1.0-0t64 libatk-bridge2.0-0t64 \
    libcups2t64 libxkbcommon0 libatspi2.0-0t64 libxcomposite1 libxdamage1 \
    libxfixes3 libxrandr2 libgbm1 libcairo2 libpango-1.0-0 libasound2t64

# Install Playwright browsers
pip install playwright
playwright install
```

### Virtual Environment Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
playwright install
```

## Asset Structure

### Directory Layout

```
pjsk_emoji/assets/
├── characters.json          # Character database
├── fonts/                   # Font files
│   ├── NotoSansCJK-Regular.ttc
│   ├── NotoSansCJK-Bold.ttc
│   └── README.md
├── emoji_images/           # Character images
│   ├── miku.png
│   ├── ichika.png
│   ├── saki.png
│   ├── honami.png
│   ├── shiho.png
│   ├── akito.png
│   ├── toya.png
│   ├── kohane.png
│   └── README.md
├── list_images/           # Additional list images
└── templates/             # HTML templates
    ├── card_template.html
    ├── list_template.html
    └── emptyHtml.html     # Fallback template
```

### Character Data Format

`characters.json` contains structured character data:

```json
{
  "characters": {
    "初音未来": {
      "id": "miku",
      "name": "初音未来",
      "aliases": ["初音未来", "初音", "miku", "hatsune", "hatsune miku"],
      "group": "MORE MORE JUMP!",
      "image_path": "emoji_images/miku.png",
      "color": "#39C5BB"
    }
  },
  "groups": {
    "Leo/need": {
      "id": "leo_need",
      "name": "Leo/need",
      "members": ["星乃一歌", "天马咲希", "望月穗波", "日野森志步"],
      "color": "#FF6B9D"
    }
  }
}
```

## Usage

### Basic Rendering

```python
from pjsk_emoji.renderer import get_renderer

# Get renderer instance (automatically initialized)
renderer = await get_renderer()

# Render an emoji card
image_bytes = await renderer.render_emoji_card(
    text="Hello World!\n这是一个测试",
    character_name="初音未来",
    font_size=42,
    line_spacing=1.2,
    curve_enabled=True,
    offset_x=10,
    offset_y=5,
    enable_shadow=True,
    emoji_set="apple"
)

# Render character list
list_bytes = await renderer.render_character_list(
    list_type="all"  # "all", "groups", "group_detail"
)
```

### Lifecycle Management

```python
from pjsk_emoji.renderer import renderer_manager

# Initialize renderer
renderer = await renderer_manager.get_renderer()

# Use renderer...
image_bytes = await renderer.render_emoji_card(...)

# Cleanup when done
await renderer_manager.close()
```

### Integration with Plugin

In your plugin's `initialize()` method:

```python
async def initialize(self):
    self._renderer = await renderer_manager.get_renderer()

async def terminate(self):
    await renderer_manager.close()
```

## Rendering Options

### Emoji Card Parameters

- `text`: Text content to render (supports newlines)
- `character_name`: Canonical character name
- `font_size`: Font size in pixels (18-84)
- `line_spacing`: Line spacing multiplier (0.6-3.0)
- `curve_enabled`: Whether to apply curve effect
- `offset_x/offset_y`: Text position offsets (-240 to 240)
- `curve_intensity`: Curve effect intensity (0.0-1.0)
- `enable_shadow`: Whether to add text shadow
- `emoji_set`: Emoji set identifier

### Character List Types

- `"all"`: Grid of all characters
- `"groups"`: Characters organized by groups
- `"group_detail"`: Detailed view of specific group (requires `group_filter`)

## Templates

### Card Template

The card template (`card_template.html`) uses Jinja2 syntax:

```html
<div class="text-content" style="transform: translate({{offset_x}}px, {{offset_y}}px) {{curve_transform}}">
    {{text_content}}
</div>
```

Available variables:
- `text_content`: Processed text content (with `<br>` for newlines)
- `character_name`: Character display name
- `character_group`: Character group name
- `character_image_path`: Path to character image
- `font_size`, `line_spacing`, `offset_x`, `offset_y`: Numeric parameters
- `curve_transform`: CSS transform for curve effect
- `text_shadow`: CSS text-shadow value
- `emoji_set`: Emoji set identifier
- `timestamp`: Current timestamp

### List Template

The list template (`list_template.html`) supports:
- `page_title`: Page title
- `page_subtitle`: Page subtitle
- `content_html`: Generated HTML content
- `timestamp`: Current timestamp

## Testing

### Quick Test

```bash
python3 scripts/quick_renderer_test.py
```

### Smoke Test

```bash
python3 tests/test_renderer_smoke.py
```

Both tests generate sample PNG files for manual verification.

## Performance Considerations

### Browser Initialization

- Browser context is created once and reused
- Viewport is set to 1200x800 with device_scale_factor=2.0 for high DPI
- Headless mode is enabled by default for production

### Template Caching

- Jinja2 templates are loaded once during initialization
- Template compilation is cached for performance

### Asset Loading

- Assets are loaded using `importlib.resources` for package distribution
- File:// URLs are used for reliable local file access

## Troubleshooting

### Common Issues

1. **Missing Playwright browsers**: Run `playwright install`
2. **Missing system dependencies**: Install libnspr4, libnss3, etc.
3. **Template not found**: Check asset directory structure
4. **Font not loading**: Verify font files in assets/fonts/
5. **Character images missing**: Check emoji_images/ directory

### Debug Mode

Enable debug logging:

```python
import logging
logging.getLogger('pjsk_emoji.renderer').setLevel(logging.DEBUG)
```

### Headless vs Headed

For debugging, you can run with headed browser:

```python
renderer = PJSKRenderer(headless=False)
```

## License

- Code: MIT License
- Fonts: SIL Open Font License (OFL)
- Character Images: Subject to original game terms of service
- Playwright: Apache License 2.0

## Contributing

When adding new characters or features:

1. Update `characters.json` with new character data
2. Add character images to `emoji_images/`
3. Update templates if needed
4. Add tests for new functionality
5. Update documentation