"""Message adapter utilities for AstrBot event handling and response formatting.

This module provides helpers to emit plain text, images, and composite responses
via AstrBot's message result APIs, while honoring configuration options like
user mentions and message timing.

The messaging adapter system abstracts away the details of AstrBot's event object,
providing a unified interface for command handlers to build and send responses.

Key Features:
- Button/quick-reply mapping (Koishi-style)
- Composite message building with text, images, and buttons
- Configuration-aware formatting (mentions, timing, etc.)
- Async generator support for command handlers
- Extensible design for domain-specific adapters

Example Usage:
    from pjsk_emoji.messaging import MessageAdapter, create_adjustment_buttons
    
    async def my_command(self, event: AstrMessageEvent):
        config = self._config_manager.get()
        adapter = MessageAdapter(event, config)
        
        # Build and send response
        async for result in adapter.send_composite_async(
            text="Command executed",
            image_bytes=image_bytes,
            buttons=create_adjustment_buttons()
        ):
            yield result
"""

from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Any, AsyncGenerator, List, Optional, Tuple

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, MessageEventResult


@dataclass
class ButtonMapping:
    """Maps a button/quick-reply to an action.
    
    Represents a single button in a button matrix, mapping display text
    to a command that should be executed when clicked.
    """
    label: str
    command: str
    emoji: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert button to dictionary representation."""
        return {
            'label': self.label,
            'command': self.command,
            'emoji': self.emoji,
        }


@dataclass
class ButtonMatrix:
    """Represents a grid of buttons for quick reply functionality.
    
    Organizes buttons in a matrix structure that can be rendered as
    Koishi-style button groups or AstrBot quick replies.
    """
    rows: List[List[ButtonMapping]]
    title: Optional[str] = None
    
    def flatten(self) -> List[ButtonMapping]:
        """Flatten matrix to single list of buttons."""
        result = []
        for row in self.rows:
            result.extend(row)
        return result
    
    def to_dict(self) -> dict:
        """Convert matrix to dictionary representation."""
        return {
            'title': self.title,
            'rows': [
                [btn.to_dict() for btn in row]
                for row in self.rows
            ],
        }


class MessageComponentBuilder:
    """Builds composite message components with text, images, and buttons.
    
    Provides a fluent interface for constructing messages that can include
    multiple content types, respecting AstrBot's message result API.
    """
    
    def __init__(self, event: AstrMessageEvent) -> None:
        """Initialize builder with an event context.
        
        Args:
            event: The AstrMessageEvent to use for constructing results
        """
        self.event = event
        self._text_parts: List[str] = []
        self._images: List[Tuple[bytes, str]] = []  # (bytes, mime_type)
        self._buttons: Optional[ButtonMatrix] = None
    
    def add_text(self, text: str) -> MessageComponentBuilder:
        """Add plain text to the message.
        
        Args:
            text: Text content to append
            
        Returns:
            Self for method chaining
        """
        if text:
            self._text_parts.append(text)
        return self
    
    def add_image(self, image_bytes: bytes, mime_type: str = "image/png") -> MessageComponentBuilder:
        """Add an image to the message.
        
        Args:
            image_bytes: Raw image bytes
            mime_type: MIME type of the image (default: image/png)
            
        Returns:
            Self for method chaining
        """
        if image_bytes:
            self._images.append((image_bytes, mime_type))
        return self
    
    def add_buttons(self, matrix: ButtonMatrix) -> MessageComponentBuilder:
        """Add button matrix to the message.
        
        Args:
            matrix: ButtonMatrix to append
            
        Returns:
            Self for method chaining
        """
        self._buttons = matrix
        return self
    
    def _build_text_content(self) -> str:
        """Build final text content from accumulated parts."""
        return "\n".join(self._text_parts)
    
    def _build_with_images(self) -> str:
        """Build text content with embedded image references."""
        text = self._build_text_content()
        
        if not self._images:
            return text
        
        # Create image blocks
        image_blocks = []
        for idx, (img_bytes, mime_type) in enumerate(self._images):
            b64 = base64.b64encode(img_bytes).decode('utf-8')
            # Format as data URI for potential embedding
            data_uri = f"data:{mime_type};base64,{b64[:50]}..."
            image_blocks.append(f"[Image {idx + 1}: {len(img_bytes)} bytes, {mime_type}]")
        
        if text:
            return text + "\n\n" + "\n".join(image_blocks)
        return "\n".join(image_blocks)
    
    def get_text_result(self) -> MessageEventResult:
        """Get plain text result (no images/buttons).
        
        Returns:
            MessageEventResult for plain text
        """
        text = self._build_text_content()
        return self.event.plain_result(text)
    
    def get_composite_result(self) -> MessageEventResult:
        """Get composite result (text with optional images and buttons).
        
        Returns:
            MessageEventResult for composite message
        """
        content = self._build_with_images()
        return self.event.plain_result(content)


class MessageAdapter:
    """Adapter for formatting and sending AstrBot responses.
    
    Abstracts the details of AstrBot's message result APIs, providing
    a consistent interface for commands to emit text, images, and
    interactive elements while respecting configuration options.
    """
    
    def __init__(self, event: AstrMessageEvent, config: Any) -> None:
        """Initialize the adapter.
        
        Args:
            event: The AstrMessageEvent to use
            config: Configuration object with messaging preferences
        """
        self.event = event
        self.config = config
    
    def emit_text(self, text: str) -> MessageEventResult:
        """Emit plain text response.
        
        Args:
            text: Text content to send
            
        Returns:
            MessageEventResult for the text
        """
        if not text:
            text = ""
        
        # Apply mention if configured
        if hasattr(self.config, 'mention_user_on_render') and self.config.mention_user_on_render:
            try:
                sender_name = self.event.get_sender_name()
                text = f"@{sender_name} {text}"
            except Exception as e:
                logger.debug("Failed to get sender name for mention: %s", str(e))
        
        return self.event.plain_result(text)
    
    def emit_image(self, image_bytes: bytes, caption: str = "") -> MessageEventResult:
        """Emit image response.
        
        AstrBot may not have native image_result, so this emits
        placeholder text with image information.
        
        Args:
            image_bytes: Raw image bytes (typically PNG)
            caption: Optional caption text
            
        Returns:
            MessageEventResult for the image
        """
        text_parts = []
        
        if caption:
            text_parts.append(caption)
        
        # Create image reference
        b64_preview = base64.b64encode(image_bytes[:32]).decode('utf-8')
        text_parts.append(f"[Image: {len(image_bytes)} bytes]")
        
        result_text = "\n".join(text_parts)
        return self.emit_text(result_text)
    
    def emit_composite(
        self,
        text: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        buttons: Optional[ButtonMatrix] = None,
    ) -> MessageEventResult:
        """Emit composite response with text, image, and/or buttons.
        
        Args:
            text: Optional text content
            image_bytes: Optional image content
            buttons: Optional button matrix
            
        Returns:
            MessageEventResult for the composite message
        """
        builder = MessageComponentBuilder(self.event)
        
        if text:
            builder.add_text(text)
        
        if image_bytes:
            builder.add_image(image_bytes)
        
        if buttons:
            builder.add_buttons(buttons)
        
        # For now, return composite as text
        # Future: Could use event.image_result() if available
        if image_bytes or buttons:
            return builder.get_composite_result()
        else:
            return builder.get_text_result()
    
    async def send_text_async(self, text: str) -> AsyncGenerator[MessageEventResult, None]:
        """Asynchronously emit plain text as generator.
        
        This is designed to work with AstrBot's command handlers
        that use 'yield' for responses.
        
        Args:
            text: Text content to send
            
        Yields:
            MessageEventResult for the text
        """
        yield self.emit_text(text)
    
    async def send_image_async(
        self,
        image_bytes: bytes,
        caption: str = "",
    ) -> AsyncGenerator[MessageEventResult, None]:
        """Asynchronously emit image as generator.
        
        Args:
            image_bytes: Raw image bytes
            caption: Optional caption
            
        Yields:
            MessageEventResult for the image
        """
        yield self.emit_image(image_bytes, caption)
    
    async def send_composite_async(
        self,
        text: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        buttons: Optional[ButtonMatrix] = None,
    ) -> AsyncGenerator[MessageEventResult, None]:
        """Asynchronously emit composite response as generator.
        
        Args:
            text: Optional text content
            image_bytes: Optional image content
            buttons: Optional button matrix
            
        Yields:
            MessageEventResult for the composite message
        """
        yield self.emit_composite(text, image_bytes, buttons)


def create_adjustment_buttons() -> ButtonMatrix:
    """Create button matrix for quick adjustment actions.
    
    Returns a Koishi-style button grid for common card adjustments,
    mapping labels to command strings that can be executed.
    
    Returns:
        ButtonMatrix with adjustment quick-actions
    """
    return ButtonMatrix(
        title="快捷调整",
        rows=[
            [
                ButtonMapping("字号 ↑", "/pjsk.调整 字号.大", "🔠"),
                ButtonMapping("字号 ↓", "/pjsk.调整 字号.小", "🔠"),
            ],
            [
                ButtonMapping("行距 ↑", "/pjsk.调整 行距.大", "📏"),
                ButtonMapping("行距 ↓", "/pjsk.调整 行距.小", "📏"),
            ],
            [
                ButtonMapping("位置 ↑", "/pjsk.调整 位置.上", "📍"),
                ButtonMapping("位置 ↓", "/pjsk.调整 位置.下", "📍"),
                ButtonMapping("位置 ←", "/pjsk.调整 位置.左", "📍"),
                ButtonMapping("位置 →", "/pjsk.调整 位置.右", "📍"),
            ],
            [
                ButtonMapping("曲线", "/pjsk.调整 曲线 切换", "〰️"),
            ],
        ],
    )


def create_list_buttons() -> ButtonMatrix:
    """Create button matrix for list view navigation.
    
    Returns a button grid for browsing character lists and details.
    
    Returns:
        ButtonMatrix with list navigation options
    """
    return ButtonMatrix(
        title="查看列表",
        rows=[
            [
                ButtonMapping("全部角色", "/pjsk.列表.全部", "📋"),
                ButtonMapping("按组分类", "/pjsk.列表.角色分类", "🎭"),
            ],
        ],
    )


def encode_koishi_button_text(buttons: ButtonMatrix) -> str:
    """Encode button matrix as Koishi-style markdown text.
    
    Converts a ButtonMatrix into a formatted text representation
    that mimics Koishi's button styling for environments that don't
    support interactive components.
    
    Args:
        buttons: ButtonMatrix to encode
        
    Returns:
        Formatted text representation
    """
    lines = []
    
    if buttons.title:
        lines.append(f"【{buttons.title}】")
        lines.append("")
    
    for row in buttons.rows:
        row_text = " ｜ ".join(
            f"{btn.emoji} {btn.label}" if btn.emoji else btn.label
            for btn in row
        )
        lines.append(row_text)
    
    return "\n".join(lines)


def should_wait_for_input(config: Any) -> bool:
    """Check if config says to wait for user input before sending commands.
    
    This honors the AstrBot equivalent of Koishi's
    `shouldWaitForUserInputBeforeSendingCommands` setting.
    
    Args:
        config: Configuration object
        
    Returns:
        True if should wait, False otherwise
    """
    if hasattr(config, 'should_wait_for_user_input_before_sending_commands'):
        return config.should_wait_for_user_input_before_sending_commands
    
    # Default: don't wait (fire commands immediately)
    return False


def should_mention_user(config: Any) -> bool:
    """Check if config says to mention user in messages.
    
    This honors the AstrBot equivalent of Koishi's
    `shouldMentionUserInMessage` setting.
    
    Args:
        config: Configuration object
        
    Returns:
        True if should mention, False otherwise
    """
    if hasattr(config, 'mention_user_on_render'):
        return config.mention_user_on_render
    
    # Default: don't mention
    return False


def get_retract_delay_ms(config: Any) -> Optional[int]:
    """Get configured retract/delete delay in milliseconds.
    
    Returns how long to wait before deleting a message, if AstrBot
    supports deletion APIs. Returns None if not configured or
    deletion not supported.
    
    Args:
        config: Configuration object
        
    Returns:
        Delay in milliseconds, or None if not available
    """
    if hasattr(config, 'retract_delay_ms'):
        return config.retract_delay_ms
    
    # Default: no retraction
    return None
