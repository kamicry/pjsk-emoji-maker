# PJSk Card Adjustment Suite

A comprehensive plugin for [AstrBot](https://astrbot.app) providing PJSk card rendering and adjustment commands with extensive customization options.

## Features

- PJSk card rendering with state persistence
- Text content adjustment with validation
- Font size adjustment (absolute and relative)
- Line spacing adjustment (absolute and relative)
- Curve effect toggle
- Position adjustment (up/down/left/right with custom steps)
- Role/character selection with random option
- Comprehensive error handling and user guidance
- Support for Chinese and English command aliases
- Range validation and clamping for all parameters

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

This plugin currently does not require any configuration. All functionality works out of the box.

### Future Configuration Options

Configuration can be added to `metadata.yaml` if needed:

```yaml
# Example configuration schema (not currently used)
config:
  greeting_prefix:
    type: string
    default: "Hello"
    description: "Prefix for greeting messages"
  
  echo_enabled:
    type: boolean
    default: true
    description: "Whether to echo back the user's message"
```

## Development

### Plugin Structure

- `main.py` - Main plugin implementation with command handlers
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

- **MyPlugin Class**: Main plugin class extending `Star` base class
- **Context**: Provides access to AstrBot core functionality
- **Event Handling**: Processes `AstrMessageEvent` for incoming messages
- **Response Generation**: Uses `event.plain_result()` to send text responses

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
