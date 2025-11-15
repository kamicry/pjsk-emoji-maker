# Hello World Plugin

A simple example plugin for [AstrBot](https://astrbot.app) demonstrating basic command handling, message processing, and event responses.

## Features

- Simple command handler responding to `/helloworld`
- User greeting with message echo functionality
- Message chain logging and processing
- Demonstrates AstrBot plugin architecture and lifecycle hooks

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
| `/helloworld` | Greets the user and echoes their message | `/helloworld Hello there!` |

### Command Details

#### `/helloworld`

Sends a greeting to the user and echoes back the message content.

**Response Format:**
```
Hello, {user_name}, 你发了 {message_content}!
```

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
