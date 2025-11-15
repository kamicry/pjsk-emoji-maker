"""Example integration of messaging adapter with PJSk plugin.

This file demonstrates how to use the messaging adapter system to build
enhanced responses in command handlers.

Note: This is example code only and not meant to be run directly.
For the actual plugin implementation, see main.py.
"""

from __future__ import annotations

from astrbot.api.event import AstrMessageEvent
from main import ConfigWrapper
from models import RenderState
from pjsk_emoji.messaging import (
    MessageAdapter,
    create_adjustment_buttons,
    encode_koishi_button_text,
)


class ExamplePjskPlugin:
    """Example showing messaging adapter integration."""
    
    def __init__(self, config):
        self.config = ConfigWrapper(config)
    
    # Example 1: Simple text response with mention
    async def example_text_response(self, event: AstrMessageEvent):
        """Send a simple text response respecting mention config."""
        config = self.config
        adapter = MessageAdapter(event, config)
        
        # The adapter automatically applies mention_user_on_render if configured
        yield adapter.emit_text("✨ 卡面已完成初始渲染")
    
    # Example 2: Composite response with image and buttons
    async def example_composite_response(
        self,
        event: AstrMessageEvent,
        state: RenderState,
        image_bytes: bytes,
    ):
        """Send composite response with text, image, and buttons."""
        config = self.config
        adapter = MessageAdapter(event, config)
        
        # Build summary text
        summary = "\n".join([
            "✨ 已完成初始渲染",
            "",
            f"文本：{state.text}",
            f"字号：{state.font_size}px",
            f"行距：{state.line_spacing:.2f}",
            f"曲线：{'开启' if state.curve_enabled else '关闭'}",
            f"位置：X {state.offset_x} / Y {state.offset_y}",
            f"人物：{state.role}",
        ])
        
        # Emit composite response
        yield adapter.emit_composite(
            text=summary,
            image_bytes=image_bytes,
            buttons=create_adjustment_buttons(),
        )
    
    # Example 3: Using MessageComponentBuilder for complex layouts
    async def example_builder_pattern(
        self,
        event: AstrMessageEvent,
        state: RenderState,
        image_bytes: bytes,
    ):
        """Example using the builder pattern for complex messages."""
        from pjsk_emoji.messaging import MessageComponentBuilder
        
        config = self.config
        
        builder = MessageComponentBuilder(event)
        
        # Add header
        builder.add_text("=" * 20)
        builder.add_text("🎨 卡面渲染结果")
        builder.add_text("=" * 20)
        builder.add_text("")
        
        # Add state summary if configured
        if config.show_success_messages:
            builder.add_text("【状态信息】")
            builder.add_text(f"文本：{state.text}")
            builder.add_text(f"字号：{state.font_size}px")
            builder.add_text(f"行距：{state.line_spacing:.2f}")
            builder.add_text(f"曲线：{'开启' if state.curve_enabled else '关闭'}")
            builder.add_text(f"位置：X {state.offset_x} / Y {state.offset_y}")
            builder.add_text(f"人物：{state.role}")
            builder.add_text("")
        
        # Add image
        builder.add_image(image_bytes)
        
        # Add quick actions
        builder.add_text("")
        builder.add_text("【快捷操作】")
        buttons = create_adjustment_buttons()
        builder.add_text(encode_koishi_button_text(buttons))
        
        # Send composite result
        yield builder.get_composite_result()
    
    # Example 4: Configuration-aware error handling
    async def example_error_handling(
        self,
        event: AstrMessageEvent,
        error_message: str,
    ):
        """Handle errors with configuration awareness."""
        from pjsk_emoji.messaging import should_mention_user
        
        config = self.config
        adapter = MessageAdapter(event, config)
        
        # Build error message
        lines = [
            f"❌ {error_message}",
            "",
            "可能的解决方案：",
            "1. 发送 /pjsk.draw 创建新的卡面",
            "2. 使用 /pjsk.调整 查看调整指令帮助",
            "3. 发送 /pjsk.列表 查看可用角色",
        ]
        
        error_text = "\n".join(lines)
        
        # Emit error response
        yield adapter.emit_text(error_text)
    
    # Example 5: Async generator for multiple messages
    async def example_multi_step_response(
        self,
        event: AstrMessageEvent,
        state: RenderState,
    ):
        """Send multiple messages in sequence."""
        config = self.config
        adapter = MessageAdapter(event, config)
        
        # Send state summary
        state_text = "\n".join([
            "【当前状态】",
            f"文本：{state.text}",
            f"字号：{state.font_size}px",
            f"行距：{state.line_spacing:.2f}",
        ])
        
        async for result in adapter.send_text_async(state_text):
            yield result
        
        # Send quick actions separately
        buttons = create_adjustment_buttons()
        quick_actions = encode_koishi_button_text(buttons)
        
        async for result in adapter.send_text_async(quick_actions):
            yield result
    
    # Example 6: Custom adapter subclass for domain-specific behavior
    class PjskMessageAdapter(MessageAdapter):
        """Extended adapter with PJSk-specific helpers."""
        
        def emit_state_summary(self, state: RenderState) -> dict:
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
        
        def emit_available_commands(self) -> dict:
            """Emit help for available commands."""
            lines = [
                "📚 可用命令：",
                "• /pjsk.draw [文本] - 创建或刷新卡面",
                "• /pjsk.绘制 -n '文本' -s 48 -c - 高级渲染",
                "• /pjsk.调整 <子命令> - 调整卡面参数",
                "• /pjsk.列表 - 查看角色列表",
            ]
            return self.emit_text("\n".join(lines))
    
    # Example 7: Using configuration flags for behavior control
    async def example_config_driven_behavior(
        self,
        event: AstrMessageEvent,
        state: RenderState,
        image_bytes: bytes,
    ):
        """Example showing how config flags drive behavior."""
        from pjsk_emoji.messaging import (
            should_wait_for_input,
            should_mention_user,
            get_retract_delay_ms,
        )
        
        config = self.config
        adapter = MessageAdapter(event, config)
        
        # Check if we should wait for user input
        if should_wait_for_input(config):
            # In Koishi, this would wait for user to click a button
            # In AstrBot, we send instructions for next command
            yield adapter.emit_text("请选择下一步操作：")
        
        # Build response text
        text = "✨ 卡面已渲染"
        
        # Check mention preference
        if should_mention_user(config):
            try:
                name = event.get_sender_name()
                text = f"@{name} {text}"
            except Exception:
                pass
        
        # Send composite
        yield adapter.emit_composite(
            text=text,
            image_bytes=image_bytes,
            buttons=create_adjustment_buttons(),
        )
        
        # Check if message should be retracted
        retract_delay = get_retract_delay_ms(config)
        if retract_delay:
            # Note: Requires AstrBot to support message deletion
            # This is a placeholder for future implementation
            pass


# Example configuration in config/pjsk_config.yaml
"""
# Messaging options
show_success_messages: true
mention_user_on_render: true

# Message control
should_wait_for_user_input_before_sending_commands: false
should_mention_user_in_message: true
retract_delay_ms: 300000  # 5 minutes

# Rendering options
default_curve_intensity: 0.5
enable_text_shadow: true
default_emoji_set: "apple"

# Persistence
persistence_enabled: true
state_ttl_hours: 24
"""


# Integration points with main plugin
"""
In main.py, you would use these adapters like:

1. In draw command:
   config = self.config
   adapter = MessageAdapter(event, config)
   yield adapter.emit_composite(
       text=summary_text,
       image_bytes=image_bytes,
       buttons=create_adjustment_buttons()
   )

2. In error handlers:
   adapter = MessageAdapter(event, config)
   yield adapter.emit_text(f"⚠️ {error_message}")

3. In custom subcommands:
   adapter = self.PjskMessageAdapter(event, config)
   yield adapter.emit_state_summary(state)
"""
