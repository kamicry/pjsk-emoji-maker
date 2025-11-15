# Messaging Adapter Guide

This document describes how to use the messaging adapter utilities provided in `pjsk_emoji/messaging.py` to build consistent, flexible responses in the PJSk Emoji Maker plugin.

## Overview

The messaging adapter provides a unified interface for:
- Plain text responses
- Image responses  
- Composite messages (text + image + buttons)
- Koishi-style button matrices
- Configuration-aware formatting (mentions, timing, etc.)

## Core Classes

### ButtonMapping

Represents a single button/quick-reply option:

```python
from pjsk_emoji.messaging import ButtonMapping

btn = ButtonMapping(
    label="增大字号",
    command="/pjsk.调整 字号.大",
    emoji="🔠"
)

# Convert to dict for serialization
btn_dict = btn.to_dict()
```

### ButtonMatrix

Organizes buttons in a grid structure:

```python
from pjsk_emoji.messaging import ButtonMatrix, ButtonMapping

buttons = ButtonMatrix(
    rows=[
        [
            ButtonMapping("A", "/cmd/a", "📝"),
            ButtonMapping("B", "/cmd/b", "🎨"),
        ],
        [
            ButtonMapping("C", "/cmd/c", "📍"),
        ],
    ],
    title="快捷操作"
)

# Flatten all buttons
all_buttons = buttons.flatten()  # [A, B, C]

# Convert to dict
matrix_dict = buttons.to_dict()
```

### MessageComponentBuilder

Fluent builder for constructing composite messages:

```python
from pjsk_emoji.messaging import MessageComponentBuilder, ButtonMatrix

builder = MessageComponentBuilder(event)

builder.add_text("Header text") \
       .add_text("More text") \
       .add_image(image_bytes, "image/png") \
       .add_buttons(button_matrix)

# Get the result
result = builder.get_composite_result()
yield result
```

### MessageAdapter

High-level adapter that respects configuration settings:

```python
from pjsk_emoji.messaging import MessageAdapter
from config import ConfigManager

config_manager = ConfigManager()
config = config_manager.get()

adapter = MessageAdapter(event, config)

# Emit text (respects mention_user_on_render config)
yield adapter.emit_text("Hello World")

# Emit image
yield adapter.emit_image(image_bytes, caption="Card preview")

# Emit composite
yield adapter.emit_composite(
    text="Card rendered successfully",
    image_bytes=image_bytes,
    buttons=button_matrix
)
```

### Async Generators

All emit methods have async generator versions for use in async command handlers:

```python
async def some_command(self, event: AstrMessageEvent):
    adapter = MessageAdapter(event, config)
    
    async for result in adapter.send_text_async("Text message"):
        yield result
    
    async for result in adapter.send_image_async(image_bytes, "Caption"):
        yield result
    
    async for result in adapter.send_composite_async(
        text="Full response",
        image_bytes=image_bytes,
        buttons=button_matrix
    ):
        yield result
```

## Pre-built Button Matrices

### Adjustment Buttons

Quick-access buttons for common card adjustments:

```python
from pjsk_emoji.messaging import create_adjustment_buttons

buttons = create_adjustment_buttons()
# Returns matrix with buttons for:
# - Font size increase/decrease
# - Line spacing increase/decrease
# - Position adjustments (up/down/left/right)
# - Curve toggle
```

### List Navigation Buttons

Buttons for browsing character lists:

```python
from pjsk_emoji.messaging import create_list_buttons

buttons = create_list_buttons()
# Returns matrix with buttons for:
# - View all characters
# - View by category
```

## Koishi Text Encoding

Convert button matrices to Koishi-style markdown format:

```python
from pjsk_emoji.messaging import encode_koishi_button_text

matrix = create_adjustment_buttons()
text = encode_koishi_button_text(matrix)

print(text)
# Output:
# 【快捷调整】
# 
# 🔠 字号 ↑ ｜ 🔠 字号 ↓
# 📏 行距 ↑ ｜ 📏 行距 ↓
# 📍 位置 ↑ ｜ 📍 位置 ↓ ｜ 📍 位置 ← ｜ 📍 位置 →
# 〰️ 曲线
```

## Configuration Options

The adapter respects these configuration settings:

### mention_user_on_render

When enabled, prepends the user's name to messages:

```yaml
mention_user_on_render: true
```

```python
adapter.emit_text("Message")
# Emits: "@Username Message"
```

### show_success_messages

Controls whether success messages include state details:

```yaml
show_success_messages: true
```

### should_wait_for_user_input_before_sending_commands

Koishi equivalent: `shouldWaitForUserInputBeforeSendingCommands`

Controls whether button clicks should wait for acknowledgment:

```python
should_wait = should_wait_for_input(config)
```

### should_mention_user_in_message

Koishi equivalent: `shouldMentionUserInMessage`

```python
should_mention = should_mention_user(config)
```

### retract_delay_ms

Configurable message deletion delay in milliseconds:

```python
delay = get_retract_delay_ms(config)  # Returns None or int
```

## Usage Examples

### Example 1: Render with State Summary

```python
from pjsk_emoji.messaging import MessageAdapter, create_adjustment_buttons

async def draw_with_buttons(self, event: AstrMessageEvent):
    config = self._config_manager.get()
    adapter = MessageAdapter(event, config)
    
    # Render card
    image_bytes = self._renderer.render_card(...)
    
    # Build text summary
    summary_text = "\n".join([
        "✨ 已完成渲染",
        "",
        f"文本：{state.text}",
        f"字号：{state.font_size}px",
    ])
    
    # Send composite response
    yield adapter.emit_composite(
        text=summary_text,
        image_bytes=image_bytes,
        buttons=create_adjustment_buttons()
    )
```

### Example 2: Builder Pattern for Complex Messages

```python
from pjsk_emoji.messaging import MessageComponentBuilder

builder = MessageComponentBuilder(event)

builder.add_text("=== 渲染结果 ===")
builder.add_text("")

if config.show_success_messages:
    builder.add_text(f"✨ {headline}")
    for line in state_summary:
        builder.add_text(line)
    builder.add_text("")

builder.add_image(image_bytes)

if buttons_enabled:
    builder.add_buttons(create_adjustment_buttons())

yield builder.get_composite_result()
```

### Example 3: Configuration-Aware Error Handling

```python
from pjsk_emoji.messaging import MessageAdapter, should_mention_user

async def error_handler(self, event: AstrMessageEvent, error_msg: str):
    config = self._config_manager.get()
    adapter = MessageAdapter(event, config)
    
    # Build error response
    error_text = f"❌ {error_msg}"
    
    if should_mention_user(config):
        # Adapter.emit_text handles this
        yield adapter.emit_text(error_text)
    else:
        yield adapter.emit_text(error_text)
```

## AstrBot API Notes

### event.plain_result()

Returns a plain text result. Currently, the adapter uses this for all responses including composite messages. The image bytes are referenced as metadata.

```python
result = event.plain_result("Response text")
yield result
```

### event.image_result()

If AstrBot's event object has this method, the adapter could be extended to use it:

```python
# Future implementation
if hasattr(event, 'image_result'):
    result = event.image_result(image_bytes, caption=caption)
else:
    # Fallback to plain_result with metadata
    result = event.plain_result(f"[Image: {len(image_bytes)} bytes]")
```

## Extending the Adapter

### Adding New Button Types

Create factory functions following the pattern:

```python
def create_custom_buttons() -> ButtonMatrix:
    """Create custom button matrix."""
    return ButtonMatrix(
        rows=[
            [ButtonMapping("Label", "/command", "emoji")],
        ],
        title="Custom Buttons"
    )
```

### Custom Configuration Helpers

Add configuration accessor functions:

```python
def get_custom_setting(config: Any) -> bool:
    """Get custom configuration setting."""
    if hasattr(config, 'my_custom_setting'):
        return config.my_custom_setting
    return False  # Default
```

### Extending MessageAdapter

Subclass for domain-specific behavior:

```python
class PjskMessageAdapter(MessageAdapter):
    """Adapter with PJSk-specific helpers."""
    
    def emit_state_summary(self, state: RenderState) -> MessageEventResult:
        """Emit formatted state summary."""
        lines = [
            f"文本：{state.text}",
            f"字号：{state.font_size}px",
            f"行距：{state.line_spacing:.2f}",
            f"曲线：{'开启' if state.curve_enabled else '关闭'}",
            f"位置：X {state.offset_x} / Y {state.offset_y}",
            f"人物：{state.role}",
        ]
        return self.emit_text("\n".join(lines))
```

## Testing

The messaging module includes comprehensive tests covering:

- Button mapping and matrix operations
- Text building and composition
- Configuration-aware formatting
- Edge cases (large images, Unicode text, etc.)
- Async generator behavior

Run tests with:

```bash
pytest tests/test_messaging.py -v
```

## Limitations and Future Enhancements

### Current Limitations

1. **Image Handling**: Images are referenced as metadata in text responses since AstrBot's event object may not have a native `image_result()` method
2. **Button Interactivity**: Button matrices are encoded as text since AstrBot may not support interactive quick-reply buttons
3. **Message Retraction**: No automatic message deletion yet (depends on AstrBot API)

### Future Enhancements

1. Support for `event.image_result()` if added to AstrBot
2. Native button/quick-reply support if AstrBot adds this
3. Automatic message retraction based on configured delay
4. Rich text formatting (bold, italic, links)
5. Media attachments (audio, video)
6. Message threading/conversations

## See Also

- [AstrBot Documentation](https://astrbot.app)
- [Main Plugin Implementation](../main.py)
- [Configuration Guide](../README.md#configuration)
