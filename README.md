# PJSk Card Adjustment Suite

A comprehensive plugin for [AstrBot](https://astrbot.app) providing PJSk card rendering and adjustment commands with extensive customization options.

## Features

- PJSk card rendering with state persistence
- Advanced Koishi-style draw command with flag parsing (-n, -x, -y, -r, -s, -l, -c, --daf)
- Text content adjustment with validation and sanitization
- Adaptive font sizing based on text length
- Font size adjustment (absolute and relative)
- Line spacing adjustment (absolute and relative)
- Curve effect toggle with intensity control
- Position adjustment (up/down/left/right with custom steps)
- Role/character selection with random option
- Helper functions for text calculations (offsets, font size, dimensions)
- Comprehensive configuration system with YAML persistence
- Mock renderer with image generation
- Comprehensive error handling and user guidance
- Support for Chinese and English command aliases
- Range validation and clamping for all parameters
- State persistence with TTL support
- Concurrent-safe state management

## Installation

### Prerequisites

- AstrBot v4.5.0 or higher
- Python 3.8 or higher

### Installation Steps

1. Place this plugin directory in your AstrBot plugins folder:
   ```bash
   cd <astrbot-installation>/plugins/
   git clone <repository-url> helloworld
   ```

2. Install dependencies (if any):
   ```bash
   # No external dependencies required for this basic plugin
   # AstrBot core dependencies are automatically available
   ```

3. Restart AstrBot or reload plugins through the AstrBot interface

4. The plugin should now be active and ready to use

## Usage

### Commands

| Command | Description | Usage Example |
|---------|-------------|---------------|
| `/pjsk.draw` | Initialize or refresh PJSk card state | `/pjsk.draw 卡面文本` |
| `/pjsk.绘制` | Advanced rendering with Koishi-style options | `/pjsk.绘制 -n "文本" -s 48 -c` |
| `/pjsk.调整` | Adjust card parameters and re-render | `/pjsk.调整 字号.大` |
| `/helloworld` | Legacy greeting command | `/helloworld Hello!` |

### Command Details

#### `/pjsk.draw`

Initialize a new PJSk card state or refresh the current configuration. Optionally provide text content.

**Usage:**
```
/pjsk.draw                    # Initialize with default text
/pjsk.draw 自定义文本内容       # Initialize with custom text
```

**Response:** Displays current state summary with all parameters.

#### `/pjsk.绘制` (Advanced Draw Command)

Advanced rendering command supporting Koishi-style flags for precise control.

**Usage:**
```
/pjsk.绘制                                   # Render with defaults
/pjsk.绘制 -n "自定义文本内容"               # Set text content
/pjsk.绘制 -n "文本" -s 48 -c               # Text + font size + curve
/pjsk.绘制 -x 50 -y -20                     # Set position offsets
/pjsk.绘制 -r 初音未来                      # Set character
/pjsk.绘制 -r -r                            # Random character
/pjsk.绘制 -l 1.8                          # Set line spacing
/pjsk.绘制 --daf                            # Use default font
```

**Available Flags:**
- `-n "text"`: Set text content (supports quotes for spaces)
- `-x pixels`: Set horizontal offset (-240 to 240)
- `-y pixels`: Set vertical offset (-240 to 240)  
- `-r name`: Set character (use `-r -r` for random)
- `-s size`: Set font size (18-84px)
- `-l spacing`: Set line spacing (0.6-3.0)
- `-c`: Enable curve effect
- `--daf`: Use default font settings

**Examples:**
```
/pjsk.绘制 -n "Hello World" -s 36 -c
/pjsk.绘制 -n "多行文本\n第二行" -l 1.5 -x 20 -y -10
/pjsk.绘制 -r miku -s 48 -c -x 30
/pjsk.绘制 --daf -n "Default font rendering"
```

**Features:**
- Adaptive text sizing (configurable)
- Automatic offset calculation
- Persistent state storage
- Image generation with mock renderer
- Configurable messaging options

#### `/pjsk.调整` (Adjustment Commands)

Modify card parameters. Without arguments, displays command guidance.

**Text Adjustment:**
```
/pjsk.调整 文本 新的文本内容
/pjsk.调整 text New text content
```

**Font Size Adjustment:**
```
/pjsk.调整 字号 48            # Set absolute size (18-84px)
/pjsk.调整 字号.大            # Increase by 4px
/pjsk.调整 字号.小            # Decrease by 4px
/pjsk.调整 font-size 60       # English alias
```

**Line Spacing Adjustment:**
```
/pjsk.调整 行距 1.8           # Set absolute spacing (0.6-3.0)
/pjsk.调整 行距.大            # Increase by 0.1
/pjsk.调整 行距.小            # Decrease by 0.1
```

**Curve Toggle:**
```
/pjsk.调整 曲线 开            # Turn on
/pjsk.调整 曲线 关            # Turn off
/pjsk.调整 曲线 切换          # Toggle
/pjsk.调整 curve toggle       # English alias
```

**Position Adjustment:**
```
/pjsk.调整 位置.上            # Move up by 12px
/pjsk.调整 位置.下 24         # Move down by 24px
/pjsk.调整 位置.左            # Move left by 12px
/pjsk.调整 位置.右 30         # Move right by 30px
/pjsk.调整 pos.up 15          # English alias
```

**Role/Character Change:**
```
/pjsk.调整 人物 初音未来      # Change to specific character
/pjsk.调整 人物 miku          # Using alias
/pjsk.调整 人物 -r            # Random character
/pjsk.调整 role ichika        # English alias
```

**Available Characters:**
- 初音未来 (miku, hatsune)
- 星乃一歌 (ichika)
- 天马咲希 (saki)
- 望月穗波 (honami)
- 日野森志步 (shiho)
- 东云彰人 (akito)
- 青柳冬弥 (toya)
- 小豆泽心羽 (kohane)

#### `/helloworld`

Legacy greeting command for backward compatibility.

**Example:**
```
User: /helloworld test message
Bot: Hello, JohnDoe, 你发了 test message!
```

## Configuration

The plugin supports extensive configuration through `config/pjsk_config.yaml`. The configuration file is automatically created with default values on first run.

### Current Configuration Options

```yaml
# Text processing options
adaptive_text_sizing: true      # Automatically adjust font size to fit text
enable_markdown_flow: false     # Enable markdown text processing

# Messaging options  
show_success_messages: true      # Include success messages in responses
mention_user_on_render: false   # Mention user when rendering

# Rendering options
default_curve_intensity: 0.5    # Default curve effect intensity (0.0-1.0)
enable_text_shadow: true        # Add shadow to rendered text
default_emoji_set: "apple"      # Default emoji set for rendering

# Persistence options
persistence_enabled: true       # Enable state persistence
state_ttl_hours: 24            # State expiration time in hours

# Validation ranges
font_size_min: 18               # Minimum font size
font_size_max: 84               # Maximum font size
font_size_step: 4               # Font size adjustment step

line_spacing_min: 0.6           # Minimum line spacing
line_spacing_max: 3.0           # Maximum line spacing
line_spacing_step: 0.1          # Line spacing adjustment step

offset_min: -240                # Minimum position offset
offset_max: 240                 # Maximum position offset
offset_step: 12                 # Position adjustment step

max_text_length: 120             # Maximum allowed text length
```

### Configuration Management

Configuration is managed automatically:
- File created at: `config/pjsk_config.yaml`
- Default values applied on first run
- Hot reloading supported (restart required for changes)
- Validation ensures all values stay within acceptable ranges

### Future Configuration Options

Additional configuration options can be added as needed. The system supports:
- Boolean toggles for features
- Numeric ranges with validation
- String preferences
- Nested configuration structures

## Development

### Plugin Structure

- `main.py` - Main plugin implementation with command handlers
- `pjsk_emoji/domain.py` - Character database and validation helpers
- `pjsk_emoji/messaging.py` - Message adapter utilities (NEW)
- `config.py` - Configuration management
- `metadata.yaml` - Plugin metadata and configuration
- `tests/` - Unit and integration tests
- `docs/` - Additional documentation

### Plugin Architecture

The plugin follows the standard AstrBot plugin pattern:

1. **Registration**: Uses `@register()` decorator to register the plugin
2. **Initialization**: Implements `initialize()` lifecycle hook for async setup
3. **Command Handling**: Uses `@filter.command()` decorator for command routing
4. **Termination**: Implements `terminate()` lifecycle hook for cleanup

### Key Components

- **PjskEmojiMaker Class**: Main plugin class extending `Star` base class
- **MessageAdapter**: Unified interface for building and sending responses
- **ButtonMatrix**: Koishi-style button grids for quick-reply actions
- **StateManager**: In-memory state storage with persistence
- **Context**: Provides access to AstrBot core functionality
- **Event Handling**: Processes `AstrMessageEvent` for incoming messages
- **Response Generation**: Uses adapter and `event.plain_result()` for responses

### Messaging System (NEW)

The plugin now includes a comprehensive messaging adapter system for building flexible responses:

- **MessageAdapter**: Configuration-aware response building
- **ButtonMatrix & ButtonMapping**: Koishi-style button grids
- **MessageComponentBuilder**: Fluent builder for composite messages
- **Pre-built Button Sets**: Adjustment buttons, list navigation buttons
- **Koishi Encoding**: Text encoding for Koishi-compatible responses

See [docs/MESSAGING_README.md](docs/MESSAGING_README.md) for details.

## Testing

Run the test suite:

```bash
pytest tests/
```

For detailed testing information and manual test scenarios, see [docs/testing.md](docs/testing.md).

## API Reference

### Plugin Methods

- `initialize()`: Async initialization method called after instantiation
- `helloworld(event)`: Command handler for `/helloworld` command
- `terminate()`: Async cleanup method called during plugin shutdown

### Event Methods Used

- `event.get_sender_name()`: Retrieves the name of the message sender
- `event.message_str`: Accesses the plain text message content
- `event.get_messages()`: Retrieves the full message chain
- `event.plain_result()`: Returns a plain text response

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Support

- [AstrBot Documentation](https://astrbot.app)
- [AstrBot GitHub](https://github.com/Soulter/AstrBot)
- [Plugin Development Guide](https://astrbot.app/plugin-dev)

## License

See [LICENSE](LICENSE) file for details.

## Changelog

### v1.0.0
- Initial release
- Basic `/helloworld` command implementation
- User greeting and message echo functionality
