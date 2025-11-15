"""Tests for message adapter utilities.

Tests cover button mapping, text formatting, composite messages,
and configuration handling for the messaging adapter.
"""

from __future__ import annotations

import base64
from unittest.mock import Mock, AsyncMock

import pytest

from pjsk_emoji.messaging import (
    ButtonMapping,
    ButtonMatrix,
    MessageComponentBuilder,
    MessageAdapter,
    create_adjustment_buttons,
    create_list_buttons,
    encode_koishi_button_text,
    should_wait_for_input,
    should_mention_user,
    get_retract_delay_ms,
)


class TestButtonMapping:
    """Tests for ButtonMapping class."""
    
    def test_button_mapping_creation(self):
        """Test creating a basic button mapping."""
        btn = ButtonMapping("Test", "/pjsk.test")
        assert btn.label == "Test"
        assert btn.command == "/pjsk.test"
        assert btn.emoji is None
    
    def test_button_mapping_with_emoji(self):
        """Test button mapping with emoji."""
        btn = ButtonMapping("字号", "/pjsk.调整 字号.大", "🔠")
        assert btn.label == "字号"
        assert btn.emoji == "🔠"
        assert btn.command == "/pjsk.调整 字号.大"
    
    def test_button_mapping_to_dict(self):
        """Test converting button to dictionary."""
        btn = ButtonMapping("Test", "/pjsk.test", "📋")
        result = btn.to_dict()
        assert result["label"] == "Test"
        assert result["command"] == "/pjsk.test"
        assert result["emoji"] == "📋"
    
    def test_button_mapping_to_dict_no_emoji(self):
        """Test dict conversion without emoji."""
        btn = ButtonMapping("Test", "/pjsk.test")
        result = btn.to_dict()
        assert result["emoji"] is None


class TestButtonMatrix:
    """Tests for ButtonMatrix class."""
    
    def test_button_matrix_creation(self):
        """Test creating a button matrix."""
        btn1 = ButtonMapping("A", "/cmd/a")
        btn2 = ButtonMapping("B", "/cmd/b")
        matrix = ButtonMatrix([[btn1], [btn2]])
        
        assert len(matrix.rows) == 2
        assert matrix.title is None
    
    def test_button_matrix_with_title(self):
        """Test button matrix with title."""
        btn = ButtonMapping("Test", "/test")
        matrix = ButtonMatrix([[btn]], title="Test Matrix")
        assert matrix.title == "Test Matrix"
    
    def test_button_matrix_flatten(self):
        """Test flattening button matrix."""
        btn1 = ButtonMapping("A", "/cmd/a")
        btn2 = ButtonMapping("B", "/cmd/b")
        btn3 = ButtonMapping("C", "/cmd/c")
        
        matrix = ButtonMatrix([
            [btn1, btn2],
            [btn3],
        ])
        
        flat = matrix.flatten()
        assert len(flat) == 3
        assert flat[0] == btn1
        assert flat[1] == btn2
        assert flat[2] == btn3
    
    def test_button_matrix_to_dict(self):
        """Test converting matrix to dictionary."""
        btn1 = ButtonMapping("A", "/cmd/a", "📝")
        btn2 = ButtonMapping("B", "/cmd/b", "🎨")
        
        matrix = ButtonMatrix([[btn1, btn2]], title="Test")
        result = matrix.to_dict()
        
        assert result["title"] == "Test"
        assert len(result["rows"]) == 1
        assert len(result["rows"][0]) == 2
        assert result["rows"][0][0]["label"] == "A"
        assert result["rows"][0][1]["emoji"] == "🎨"


class TestMessageComponentBuilder:
    """Tests for MessageComponentBuilder class."""
    
    @pytest.fixture
    def mock_event(self):
        """Create a mock event."""
        event = Mock()
        event.plain_result = Mock(return_value="result")
        return event
    
    def test_builder_initialization(self, mock_event):
        """Test initializing builder."""
        builder = MessageComponentBuilder(mock_event)
        assert builder.event == mock_event
        assert builder._text_parts == []
        assert builder._images == []
        assert builder._buttons is None
    
    def test_add_text(self, mock_event):
        """Test adding text to builder."""
        builder = MessageComponentBuilder(mock_event)
        result = builder.add_text("Hello")
        
        assert result == builder  # Check chaining
        assert "Hello" in builder._text_parts
    
    def test_add_text_multiple(self, mock_event):
        """Test adding multiple text parts."""
        builder = MessageComponentBuilder(mock_event)
        builder.add_text("Line 1").add_text("Line 2")
        
        assert len(builder._text_parts) == 2
        assert builder._text_parts[0] == "Line 1"
        assert builder._text_parts[1] == "Line 2"
    
    def test_add_text_empty(self, mock_event):
        """Test adding empty text (should be skipped)."""
        builder = MessageComponentBuilder(mock_event)
        builder.add_text("")
        
        assert len(builder._text_parts) == 0
    
    def test_add_image(self, mock_event):
        """Test adding image to builder."""
        builder = MessageComponentBuilder(mock_event)
        img_bytes = b"PNG fake data"
        result = builder.add_image(img_bytes)
        
        assert result == builder  # Check chaining
        assert len(builder._images) == 1
        assert builder._images[0] == (img_bytes, "image/png")
    
    def test_add_image_custom_mime_type(self, mock_event):
        """Test adding image with custom MIME type."""
        builder = MessageComponentBuilder(mock_event)
        img_bytes = b"JPEG fake data"
        builder.add_image(img_bytes, "image/jpeg")
        
        assert builder._images[0] == (img_bytes, "image/jpeg")
    
    def test_add_buttons(self, mock_event):
        """Test adding buttons to builder."""
        builder = MessageComponentBuilder(mock_event)
        matrix = ButtonMatrix([[ButtonMapping("Test", "/test")]])
        result = builder.add_buttons(matrix)
        
        assert result == builder  # Check chaining
        assert builder._buttons == matrix
    
    def test_build_text_content(self, mock_event):
        """Test building text content."""
        builder = MessageComponentBuilder(mock_event)
        builder.add_text("Line 1").add_text("Line 2").add_text("Line 3")
        
        text = builder._build_text_content()
        assert text == "Line 1\nLine 2\nLine 3"
    
    def test_build_text_content_empty(self, mock_event):
        """Test building text when empty."""
        builder = MessageComponentBuilder(mock_event)
        text = builder._build_text_content()
        assert text == ""
    
    def test_build_with_images_no_text(self, mock_event):
        """Test building with images but no text."""
        builder = MessageComponentBuilder(mock_event)
        img_bytes = b"PNG fake" * 100  # Make it realistic size
        builder.add_image(img_bytes)
        
        content = builder._build_with_images()
        assert f"[Image 1: {len(img_bytes)} bytes" in content
    
    def test_build_with_images_and_text(self, mock_event):
        """Test building with both text and images."""
        builder = MessageComponentBuilder(mock_event)
        builder.add_text("Caption")
        img_bytes = b"PNG fake" * 100
        builder.add_image(img_bytes)
        
        content = builder._build_with_images()
        assert "Caption" in content
        assert "[Image 1:" in content
    
    def test_build_with_multiple_images(self, mock_event):
        """Test building with multiple images."""
        builder = MessageComponentBuilder(mock_event)
        img1 = b"PNG1" * 100
        img2 = b"PNG2" * 100
        builder.add_image(img1).add_image(img2)
        
        content = builder._build_with_images()
        assert "[Image 1:" in content
        assert "[Image 2:" in content
    
    def test_get_text_result(self, mock_event):
        """Test getting text result."""
        builder = MessageComponentBuilder(mock_event)
        builder.add_text("Hello World")
        
        result = builder.get_text_result()
        assert result == "result"
        mock_event.plain_result.assert_called_once_with("Hello World")
    
    def test_get_composite_result(self, mock_event):
        """Test getting composite result."""
        builder = MessageComponentBuilder(mock_event)
        builder.add_text("Caption")
        builder.add_image(b"PNG" * 100)
        
        result = builder.get_composite_result()
        assert result == "result"
        
        # Check that plain_result was called with composite content
        called_text = mock_event.plain_result.call_args[0][0]
        assert "Caption" in called_text


class TestMessageAdapter:
    """Tests for MessageAdapter class."""
    
    @pytest.fixture
    def mock_event(self):
        """Create a mock event."""
        event = Mock()
        event.plain_result = Mock(return_value="result")
        event.get_sender_name = Mock(return_value="TestUser")
        return event
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock config."""
        config = Mock()
        config.mention_user_on_render = False
        config.show_success_messages = True
        return config
    
    def test_adapter_initialization(self, mock_event, mock_config):
        """Test initializing adapter."""
        adapter = MessageAdapter(mock_event, mock_config)
        assert adapter.event == mock_event
        assert adapter.config == mock_config
    
    def test_emit_text_simple(self, mock_event, mock_config):
        """Test emitting simple text."""
        adapter = MessageAdapter(mock_event, mock_config)
        result = adapter.emit_text("Hello")
        
        assert result == "result"
        mock_event.plain_result.assert_called_once_with("Hello")
    
    def test_emit_text_empty(self, mock_event, mock_config):
        """Test emitting empty text."""
        adapter = MessageAdapter(mock_event, mock_config)
        adapter.emit_text("")
        
        mock_event.plain_result.assert_called_once_with("")
    
    def test_emit_text_with_mention(self, mock_event, mock_config):
        """Test emitting text with mention enabled."""
        mock_config.mention_user_on_render = True
        adapter = MessageAdapter(mock_event, mock_config)
        
        adapter.emit_text("Message")
        
        called_text = mock_event.plain_result.call_args[0][0]
        assert "@TestUser" in called_text
        assert "Message" in called_text
    
    def test_emit_text_with_mention_failed(self, mock_event, mock_config):
        """Test mention fails gracefully."""
        mock_config.mention_user_on_render = True
        mock_event.get_sender_name = Mock(side_effect=Exception("No sender"))
        
        adapter = MessageAdapter(mock_event, mock_config)
        adapter.emit_text("Message")
        
        # Should still emit text without mention
        mock_event.plain_result.assert_called_once()
    
    def test_emit_image(self, mock_event, mock_config):
        """Test emitting image."""
        adapter = MessageAdapter(mock_event, mock_config)
        img_bytes = b"PNG" * 1000
        
        adapter.emit_image(img_bytes, "Test caption")
        
        called_text = mock_event.plain_result.call_args[0][0]
        assert "Test caption" in called_text
        assert "3000 bytes" in called_text
    
    def test_emit_composite_text_only(self, mock_event, mock_config):
        """Test composite with text only."""
        adapter = MessageAdapter(mock_event, mock_config)
        adapter.emit_composite(text="Hello")
        
        mock_event.plain_result.assert_called()
        called_text = mock_event.plain_result.call_args[0][0]
        assert "Hello" in called_text
    
    def test_emit_composite_with_image(self, mock_event, mock_config):
        """Test composite with image."""
        adapter = MessageAdapter(mock_event, mock_config)
        img_bytes = b"PNG" * 1000
        
        adapter.emit_composite(text="Caption", image_bytes=img_bytes)
        
        called_text = mock_event.plain_result.call_args[0][0]
        assert "Caption" in called_text
        assert "[Image:" in called_text
    
    @pytest.mark.asyncio
    async def test_send_text_async(self, mock_event, mock_config):
        """Test async text sending."""
        adapter = MessageAdapter(mock_event, mock_config)
        
        results = []
        async for result in adapter.send_text_async("Hello"):
            results.append(result)
        
        assert len(results) == 1
        assert results[0] == "result"
    
    @pytest.mark.asyncio
    async def test_send_image_async(self, mock_event, mock_config):
        """Test async image sending."""
        adapter = MessageAdapter(mock_event, mock_config)
        img_bytes = b"PNG" * 1000
        
        results = []
        async for result in adapter.send_image_async(img_bytes, "Caption"):
            results.append(result)
        
        assert len(results) == 1
    
    @pytest.mark.asyncio
    async def test_send_composite_async(self, mock_event, mock_config):
        """Test async composite sending."""
        adapter = MessageAdapter(mock_event, mock_config)
        img_bytes = b"PNG" * 1000
        matrix = ButtonMatrix([[ButtonMapping("Test", "/test")]])
        
        results = []
        async for result in adapter.send_composite_async(
            text="Hello",
            image_bytes=img_bytes,
            buttons=matrix
        ):
            results.append(result)
        
        assert len(results) == 1


class TestButtonFactories:
    """Tests for button creation functions."""
    
    def test_create_adjustment_buttons(self):
        """Test creating adjustment button matrix."""
        matrix = create_adjustment_buttons()
        
        assert matrix.title == "快捷调整"
        assert len(matrix.rows) > 0
        
        # Check flattened buttons
        buttons = matrix.flatten()
        assert len(buttons) > 0
        
        # Check that commands are present
        commands = [btn.command for btn in buttons]
        assert any("字号" in cmd for cmd in commands)
        assert any("行距" in cmd for cmd in commands)
    
    def test_create_list_buttons(self):
        """Test creating list button matrix."""
        matrix = create_list_buttons()
        
        assert matrix.title == "查看列表"
        buttons = matrix.flatten()
        assert len(buttons) >= 2
        
        commands = [btn.command for btn in buttons]
        assert any("列表.全部" in cmd for cmd in commands)
        assert any("列表.角色分类" in cmd for cmd in commands)


class TestKoishiEncoding:
    """Tests for Koishi button text encoding."""
    
    def test_encode_koishi_button_text_simple(self):
        """Test encoding simple button matrix."""
        btn1 = ButtonMapping("Test1", "/cmd1", "📝")
        btn2 = ButtonMapping("Test2", "/cmd2", "🎨")
        
        matrix = ButtonMatrix([[btn1, btn2]], title="Test")
        text = encode_koishi_button_text(matrix)
        
        assert "【Test】" in text
        assert "📝 Test1" in text
        assert "🎨 Test2" in text
        assert "｜" in text
    
    def test_encode_koishi_button_text_no_emoji(self):
        """Test encoding without emojis."""
        btn1 = ButtonMapping("Test1", "/cmd1")
        btn2 = ButtonMapping("Test2", "/cmd2")
        
        matrix = ButtonMatrix([[btn1, btn2]])
        text = encode_koishi_button_text(matrix)
        
        assert "Test1" in text
        assert "Test2" in text
    
    def test_encode_koishi_button_text_multiple_rows(self):
        """Test encoding with multiple rows."""
        row1 = [
            ButtonMapping("A", "/a", "📝"),
            ButtonMapping("B", "/b", "🎨"),
        ]
        row2 = [
            ButtonMapping("C", "/c", "📍"),
        ]
        
        matrix = ButtonMatrix([row1, row2], title="Multi-row")
        text = encode_koishi_button_text(matrix)
        
        assert "【Multi-row】" in text
        assert "A" in text
        assert "C" in text


class TestConfigurationHelpers:
    """Tests for configuration helper functions."""
    
    def test_should_wait_for_input_default(self):
        """Test default behavior."""
        config = Mock(spec=[])
        assert should_wait_for_input(config) is False
    
    def test_should_wait_for_input_enabled(self):
        """Test when enabled."""
        config = Mock()
        config.should_wait_for_user_input_before_sending_commands = True
        assert should_wait_for_input(config) is True
    
    def test_should_wait_for_input_disabled(self):
        """Test when disabled."""
        config = Mock()
        config.should_wait_for_user_input_before_sending_commands = False
        assert should_wait_for_input(config) is False
    
    def test_should_mention_user_default(self):
        """Test default behavior."""
        config = Mock(spec=[])
        assert should_mention_user(config) is False
    
    def test_should_mention_user_enabled(self):
        """Test when enabled."""
        config = Mock()
        config.mention_user_on_render = True
        assert should_mention_user(config) is True
    
    def test_should_mention_user_disabled(self):
        """Test when disabled."""
        config = Mock()
        config.mention_user_on_render = False
        assert should_mention_user(config) is False
    
    def test_get_retract_delay_default(self):
        """Test default (no retraction)."""
        config = Mock(spec=[])
        assert get_retract_delay_ms(config) is None
    
    def test_get_retract_delay_configured(self):
        """Test when configured."""
        config = Mock()
        config.retract_delay_ms = 5000
        assert get_retract_delay_ms(config) == 5000
    
    def test_get_retract_delay_zero(self):
        """Test zero delay."""
        config = Mock()
        config.retract_delay_ms = 0
        assert get_retract_delay_ms(config) == 0


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""
    
    def test_button_mapping_empty_label(self):
        """Test button with empty label."""
        btn = ButtonMapping("", "/cmd")
        assert btn.label == ""
        assert btn.to_dict()["label"] == ""
    
    def test_button_matrix_empty_rows(self):
        """Test matrix with no buttons."""
        matrix = ButtonMatrix([])
        assert matrix.flatten() == []
    
    def test_builder_add_text_unicode(self):
        """Test adding Unicode text."""
        event = Mock()
        event.plain_result = Mock(return_value="result")
        
        builder = MessageComponentBuilder(event)
        builder.add_text("你好世界").add_text("🎨 测试")
        
        text = builder._build_text_content()
        assert "你好世界" in text
        assert "🎨 测试" in text
    
    def test_adapter_large_image(self):
        """Test handling large image."""
        event = Mock()
        event.plain_result = Mock(return_value="result")
        
        config = Mock()
        config.mention_user_on_render = False
        
        adapter = MessageAdapter(event, config)
        large_img = b"X" * (10 * 1024 * 1024)  # 10MB
        
        adapter.emit_image(large_img, "Large image")
        
        called_text = event.plain_result.call_args[0][0]
        assert "10485760 bytes" in called_text
    
    def test_encode_koishi_long_label(self):
        """Test encoding button with long label."""
        btn = ButtonMapping("这是一个很长的按钮标签文本", "/cmd", "📝")
        matrix = ButtonMatrix([[btn]])
        
        text = encode_koishi_button_text(matrix)
        assert "这是一个很长的按钮标签文本" in text
