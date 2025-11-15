# Messaging Adapter System

The messaging adapter system provides a unified interface for building and sending AstrBot responses, with support for text, images, buttons, and configuration-aware formatting.

## Quick Start

### Basic Text Response

```python
from pjsk_emoji.messaging import MessageAdapter

async def my_command(self, event: AstrMessageEvent):
    config = self._config_manager.get()
    adapter = MessageAdapter(event, config)
    
    yield adapter.emit_text("Hello World")
```

### Composite Response

```python
from pjsk_emoji.messaging import MessageAdapter, create_adjustment_buttons

async def render_command(self, event: AstrMessageEvent):
    config = self._config_manager.get()
    adapter = MessageAdapter(event, config)
    
    image_bytes = self._renderer.render_card(...)
    
    yield adapter.emit_composite(
        text="✨ 卡面已完成渲染",
        image_bytes=image_bytes,
        buttons=create_adjustment_buttons()
    )
```

## Core Concepts

### Buttons and Quick Replies

The system maps Koishi-style button matrices to AstrBot components:

```python
from pjsk_emoji.messaging import ButtonMapping, ButtonMatrix

# Single button
btn = ButtonMapping("增大字号", "/pjsk.调整 字号.大", "🔠")

# Button grid
matrix = ButtonMatrix(
    rows=[
        [btn1, btn2],
        [btn3],
    ],
    title="快捷操作"
)
```

### Message Components

Build complex messages using the builder pattern:

```python
from pjsk_emoji.messaging import MessageComponentBuilder

builder = MessageComponentBuilder(event)
builder.add_text("Title") \
       .add_text("Content") \
       .add_image(image_bytes) \
       .add_buttons(button_matrix)

yield builder.get_composite_result()
```

## Configuration

The messaging system honors these config settings:

### mention_user_on_render
- Type: `bool` (default: `false`)
- Effect: Prepends user's name to responses
- Example: `@Username Your message`

### should_wait_for_user_input_before_sending_commands
- Type: `bool` (default: `false`)
- Effect: Changes behavior of button responses
- Koishi equivalent: `shouldWaitForUserInputBeforeSendingCommands`

### should_mention_user_in_message
- Type: `bool` (default: `false`)
- Effect: Controls user mention in messages
- Koishi equivalent: `shouldMentionUserInMessage`

### retract_delay_ms
- Type: `int | null` (default: `null`)
- Effect: Auto-delete message after delay (if supported)
- Example: `5000` (5 seconds)

## Response Types

### Plain Text
```python
adapter.emit_text("Simple message")
```

### Image
```python
adapter.emit_image(image_bytes, caption="Card preview")
```

### Composite
```python
adapter.emit_composite(
    text="Message text",
    image_bytes=image_bytes,
    buttons=button_matrix
)
```

### Async Generators
```python
async for result in adapter.send_text_async("Message"):
    yield result
```

## Pre-built Button Sets

### Adjustment Buttons
Quick-access buttons for card parameters:

```python
from pjsk_emoji.messaging import create_adjustment_buttons

buttons = create_adjustment_buttons()
# Includes: font size, line spacing, position, curve toggle
```

### List Buttons
Navigation buttons for character lists:

```python
from pjsk_emoji.messaging import create_list_buttons

buttons = create_list_buttons()
# Includes: view all characters, view by group
```

## Koishi Compatibility

The system provides helpers for Koishi-style button encoding:

```python
from pjsk_emoji.messaging import encode_koishi_button_text

matrix = create_adjustment_buttons()
text = encode_koishi_button_text(matrix)

# Output:
# 【快捷调整】
# 🔠 字号 ↑ ｜ 🔠 字号 ↓
# 📏 行距 ↑ ｜ 📏 行距 ↓
# ...
```

## Configuration Helpers

Helper functions to check configuration:

```python
from pjsk_emoji.messaging import (
    should_wait_for_input,
    should_mention_user,
    get_retract_delay_ms,
)

# Check if button clicks should wait for confirmation
if should_wait_for_input(config):
    # Adjust behavior accordingly
    pass

# Check if user should be mentioned
if should_mention_user(config):
    # Build mention
    pass

# Get message retraction delay
delay = get_retract_delay_ms(config)  # Returns int or None
```

## Advanced Usage

### Custom Adapter

Extend the adapter for domain-specific behavior:

```python
from pjsk_emoji.messaging import MessageAdapter

class PjskAdapter(MessageAdapter):
    def emit_state_summary(self, state: RenderState):
        """Emit formatted state."""
        lines = [
            f"文本：{state.text}",
            f"字号：{state.font_size}px",
            # ...
        ]
        return self.emit_text("\n".join(lines))
```

### Multi-step Responses

Send multiple messages sequentially:

```python
async def multi_step(self, event, state, image_bytes):
    config = self._config_manager.get()
    adapter = MessageAdapter(event, config)
    
    # Send state
    async for result in adapter.send_text_async("Current state..."):
        yield result
    
    # Send image
    async for result in adapter.send_image_async(image_bytes):
        yield result
    
    # Send buttons
    async for result in adapter.send_text_async(
        encode_koishi_button_text(buttons)
    ):
        yield result
```

## Testing

The messaging module includes comprehensive tests:

```bash
pytest tests/test_messaging.py -v
```

Test coverage includes:
- Button mapping and matrix operations
- Text building and composition
- Configuration-aware formatting
- Image handling
- Async generator behavior
- Edge cases (Unicode, large files, etc.)

## Limitations

### Current
- Images referenced as metadata in text (no native AstrBot image API)
- Buttons encoded as text (no interactive quick-reply support)
- No automatic message deletion (depends on AstrBot API)

### Future
- Support for `event.image_result()` when available
- Native button/quick-reply support
- Message retraction/deletion
- Rich text formatting (bold, italic, links)
- Media attachments

## AstrBot API Notes

The adapter uses these AstrBot event methods:

- `event.plain_result(text)`: Return plain text result
- `event.get_sender_name()`: Get user name (for mentions)
- `event.message_str`: Access message content

If AstrBot adds these in future:
- `event.image_result(bytes)`: Return image result
- `event.component_result(buttons)`: Return interactive buttons
- `event.delete_message(delay_ms)`: Delete message after delay

## Examples

See `docs/messaging_adapter.md` for detailed documentation and `docs/messaging_integration_example.py` for code examples.

## Contributing

To add new features:

1. Add button factories: `create_*_buttons()` functions
2. Add config helpers: `get_*_setting()` functions
3. Add adapter methods for domain-specific responses
4. Add tests in `tests/test_messaging.py`
5. Update documentation

## See Also

- [Messaging Adapter Guide](messaging_adapter.md)
- [Integration Examples](messaging_integration_example.py)
- [Main Plugin](../main.py)
- [Configuration](../README.md#configuration)
