"""Tests for PJSk draw command with Koishi-style options."""

import pytest
from unittest.mock import Mock, patch
from main import PjskEmojiMaker
from models import RenderState
from utils import parseKoishiFlags, calculateOffsets, calculateFontSize
from config import PJSkConfig
from persistence import StatePersistence


class TestPJSkDrawKoishiCommand:
    """Tests for the pjsk.绘制 command."""

    @pytest.fixture
    def mock_context(self):
        """Create a mock Context object."""
        context = Mock()
        return context

    @pytest.fixture
    def plugin(self, mock_context):
        """Create a plugin instance with mock context."""
        return PjskEmojiMaker(mock_context)

    @pytest.fixture
    def mock_event(self):
        """Create a mock message event."""
        event = Mock()
        event.platform = "test"
        event.session_id = "test_session"
        event.message_str = ""
        event.plain_result = Mock(return_value="result")
        event.get_sender_name = Mock(return_value="TestUser")
        return event

    @pytest.mark.asyncio
    async def test_draw_koishi_basic(self, plugin, mock_event):
        """Test basic draw command without options."""
        # Mock config to disable adaptive sizing for predictable results
        config = PJSkConfig(adaptive_text_sizing=False)
        plugin._config_manager._config = config
        
        mock_event.message_str = ""
        
        result_generator = plugin.draw_koishi(mock_event)
        result = await result_generator.__anext__()
        
        # Verify state was created and saved
        key = ("test", "test_session")
        state = plugin._state_manager.get(key)
        assert state is not None
        assert state.text == "这是一个新的卡面"
        assert state.font_size == 42
        assert state.role == "初音未来"

    @pytest.mark.asyncio
    async def test_draw_koishi_with_text(self, plugin, mock_event):
        """Test draw command with text option."""
        mock_event.message_str = '-n "Custom text content"'
        
        result_generator = plugin.draw_koishi(mock_event)
        result = await result_generator.__anext__()
        
        key = ("test", "test_session")
        state = plugin._state_manager.get(key)
        assert state is not None
        assert state.text == "Custom text content"

    @pytest.mark.asyncio
    async def test_draw_koishi_with_font_size(self, plugin, mock_event):
        """Test draw command with font size option."""
        # Mock config to disable adaptive sizing
        config = PJSkConfig(adaptive_text_sizing=False)
        plugin._config_manager._config = config
        
        mock_event.message_str = "-n Test -s 48"
        
        result_generator = plugin.draw_koishi(mock_event)
        result = await result_generator.__anext__()
        
        key = ("test", "test_session")
        state = plugin._state_manager.get(key)
        assert state is not None
        assert state.font_size == 48

    @pytest.mark.asyncio
    async def test_draw_koishi_with_curve(self, plugin, mock_event):
        """Test draw command with curve option."""
        mock_event.message_str = "-n Test -c"
        
        result_generator = plugin.draw_koishi(mock_event)
        result = await result_generator.__anext__()
        
        key = ("test", "test_session")
        state = plugin._state_manager.get(key)
        assert state is not None
        assert state.curve_enabled is True

    @pytest.mark.asyncio
    async def test_draw_koishi_with_offsets(self, plugin, mock_event):
        """Test draw command with position offsets."""
        mock_event.message_str = "-n Test -x 50 -y -20"
        
        result_generator = plugin.draw_koishi(mock_event)
        result = await result_generator.__anext__()
        
        key = ("test", "test_session")
        state = plugin._state_manager.get(key)
        assert state is not None
        assert state.offset_x == 50
        assert state.offset_y == -20

    @pytest.mark.asyncio
    async def test_draw_koishi_with_role(self, plugin, mock_event):
        """Test draw command with role option."""
        mock_event.message_str = "-n Test -r 星乃一歌"
        
        result_generator = plugin.draw_koishi(mock_event)
        result = await result_generator.__anext__()
        
        key = ("test", "test_session")
        state = plugin._state_manager.get(key)
        assert state is not None
        assert state.role == "星乃一歌"

    @pytest.mark.asyncio
    async def test_draw_koishi_with_random_role(self, plugin, mock_event):
        """Test draw command with random role option."""
        mock_event.message_str = "-n Test -r -r"
        
        result_generator = plugin.draw_koishi(mock_event)
        result = await result_generator.__anext__()
        
        key = ("test", "test_session")
        state = plugin._state_manager.get(key)
        assert state is not None
        assert state.role in plugin._role_names

    @pytest.mark.asyncio
    async def test_draw_koishi_with_line_spacing(self, plugin, mock_event):
        """Test draw command with line spacing option."""
        mock_event.message_str = "-n Test -l 1.8"
        
        result_generator = plugin.draw_koishi(mock_event)
        result = await result_generator.__anext__()
        
        key = ("test", "test_session")
        state = plugin._state_manager.get(key)
        assert state is not None
        assert state.line_spacing == 1.8

    @pytest.mark.asyncio
    async def test_draw_koishi_with_default_font(self, plugin, mock_event):
        """Test draw command with default font option."""
        mock_event.message_str = "-n Test --daf"
        
        result_generator = plugin.draw_koishi(mock_event)
        result = await result_generator.__anext__()
        
        key = ("test", "test_session")
        state = plugin._state_manager.get(key)
        assert state is not None
        assert state.text == "Test"

    @pytest.mark.asyncio
    async def test_draw_koishi_with_multiple_options(self, plugin, mock_event):
        """Test draw command with multiple options combined."""
        mock_event.message_str = '-n "Multi line test" -s 36 -c -x 20 -y 10 -l 1.5 -r miku'
        
        result_generator = plugin.draw_koishi(mock_event)
        result = await result_generator.__anext__()
        
        key = ("test", "test_session")
        state = plugin._state_manager.get(key)
        assert state is not None
        assert state.text == "Multi line test"
        assert state.font_size == 36
        assert state.curve_enabled is True
        assert state.offset_x == 20
        assert state.offset_y == 10
        assert state.line_spacing == 1.5
        assert state.role == "初音未来"

    @pytest.mark.asyncio
    async def test_draw_koishi_adaptive_sizing(self, plugin, mock_event):
        """Test adaptive text sizing functionality."""
        # Mock config to enable adaptive sizing
        config = PJSkConfig(adaptive_text_sizing=True)
        plugin._config_manager._config = config
        
        # Long text that should trigger adaptive sizing
        long_text = "This is a very long text that should cause adaptive font sizing to kick in and make the font smaller"
        mock_event.message_str = f'-n "{long_text}"'
        
        result_generator = plugin.draw_koishi(mock_event)
        result = await result_generator.__anext__()
        
        key = ("test", "test_session")
        state = plugin._state_manager.get(key)
        assert state is not None
        assert state.text == long_text
        # Font size should be smaller than default due to adaptive sizing
        assert state.font_size < 42

    @pytest.mark.asyncio
    async def test_draw_koishi_persistence(self, plugin, mock_event):
        """Test that state is persisted correctly."""
        mock_event.message_str = "-n Persistence test -s 50"
        
        result_generator = plugin.draw_koishi(mock_event)
        result = await result_generator.__anext__()
        
        # Verify state was saved to persistence
        key = ("test", "test_session")
        persisted_state = plugin._persistence.get_state(key[0], key[1])
        assert persisted_state is not None
        assert persisted_state.text == "Persistence"
        assert persisted_state.font_size == 50
        
        # Check that response contains some indication of success
        mock_event.plain_result.assert_called_once()
        call_args = mock_event.plain_result.call_args[0][0]
        # Response should mention persistence or success
        assert "Persistence" in call_args or "已完成" in call_args

    @pytest.mark.asyncio
    async def test_draw_koishi_error_handling(self, plugin, mock_event):
        """Test error handling in draw command."""
        # Test with invalid font size
        mock_event.message_str = "-n Test -s invalid"
        
        result_generator = plugin.draw_koishi(mock_event)
        result = await result_generator.__anext__()
        
        # Should handle error gracefully and not crash
        assert result is not None

    @pytest.mark.asyncio
    async def test_draw_koishi_validation_ranges(self, plugin, mock_event):
        """Test that values are clamped to valid ranges."""
        # Test with values outside ranges
        mock_event.message_str = "-n Test -s 200 -x 500 -y -500 -l 10"
        
        result_generator = plugin.draw_koishi(mock_event)
        result = await result_generator.__anext__()
        
        key = ("test", "test_session")
        state = plugin._state_manager.get(key)
        assert state is not None
        # Values should be clamped to valid ranges
        assert 18 <= state.font_size <= 84
        assert -240 <= state.offset_x <= 240
        assert -240 <= state.offset_y <= 240
        assert 0.6 <= state.line_spacing <= 3.0


class TestKoishiFlagParser:
    """Tests for the Koishi flag parser."""

    def test_parse_empty_string(self):
        """Test parsing empty string."""
        result = parseKoishiFlags("")
        assert result == {}

    def test_parse_text_flag(self):
        """Test parsing -n flag."""
        result = parseKoishiFlags('-n "Hello World"')
        assert result['text'] == "Hello World"

    def test_parse_text_flag_without_quotes(self):
        """Test parsing -n flag without quotes."""
        result = parseKoishiFlags('-n Hello')
        assert result['text'] == "Hello"

    def test_parse_numeric_flags(self):
        """Test parsing numeric flags."""
        result = parseKoishiFlags('-x 50 -y -20 -s 36 -l 1.5')
        assert result['offset_x'] == 50
        assert result['offset_y'] == -20
        assert result['font_size'] == 36
        assert result['line_spacing'] == 1.5

    def test_parse_boolean_flags(self):
        """Test parsing boolean flags."""
        result = parseKoishiFlags('-c --daf')
        assert result['curve'] is True
        assert result['default_font'] is True

    def test_parse_role_flag(self):
        """Test parsing -r flag."""
        result = parseKoishiFlags('-r miku')
        assert result['role'] == "miku"

    def test_parse_random_role_flag(self):
        """Test parsing -r -r flag."""
        result = parseKoishiFlags('-r -r')
        assert result['role'] == "-r"

    def test_parse_mixed_flags(self):
        """Test parsing mixed flags."""
        result = parseKoishiFlags('-n "Test text" -s 48 -c -x 30 -r ichika')
        expected = {
            'text': 'Test text',
            'font_size': 48,
            'curve': True,
            'offset_x': 30,
            'role': 'ichika',
            'offset_y': None,
            'line_spacing': None,
            'default_font': False
        }
        assert result == expected

    def test_parse_invalid_numeric_values(self):
        """Test parsing invalid numeric values."""
        result = parseKoishiFlags('-s invalid -l not_a_number')
        # Invalid values should be None
        assert result['font_size'] is None
        assert result['line_spacing'] is None

    def test_parse_unrecognized_flags(self):
        """Test parsing unrecognized flags."""
        result = parseKoishiFlags('-z 100 --unknown value')
        # Should return default structure with None for all fields
        expected_keys = {'text', 'offset_x', 'offset_y', 'role', 'font_size', 'line_spacing', 'curve', 'default_font'}
        assert set(result.keys()) == expected_keys
        # All values should be None for unrecognized flags
        for key in expected_keys:
            if key not in ['curve', 'default_font']:  # These might be boolean
                assert result[key] is None
            else:  # For boolean flags, check they're False/None
                assert result[key] in [None, False]


class TestHelperFunctions:
    """Tests for utility helper functions."""

    def test_calculate_offsets(self):
        """Test offset calculation."""
        text = "Test text"
        font_size = 42
        line_spacing = 1.2
        
        offset_x, offset_y = calculateOffsets(text, font_size, line_spacing)
        
        assert isinstance(offset_x, int)
        assert isinstance(offset_y, int)
        assert -240 <= offset_x <= 240
        assert -240 <= offset_y <= 240

    def test_calculate_font_size(self):
        """Test adaptive font size calculation."""
        # Short text should get max size
        short_text = "Hi"
        font_size = calculateFontSize(short_text, target_width=400, min_size=18, max_size=84)
        assert font_size == 84
        
        # Long text should get smaller size
        long_text = "This is a very long text that should require a smaller font size to fit"
        font_size = calculateFontSize(long_text, target_width=400, min_size=18, max_size=84)
        assert 18 <= font_size <= 84

    def test_calculate_font_size_empty_text(self):
        """Test font size calculation with empty text."""
        font_size = calculateFontSize("", target_width=400, min_size=18, max_size=84)
        assert font_size == 84

    def test_calculate_offsets_multiline(self):
        """Test offset calculation with multiline text."""
        multiline_text = "Line 1\nLine 2\nLine 3"
        font_size = 42
        line_spacing = 1.2
        
        offset_x, offset_y = calculateOffsets(multiline_text, font_size, line_spacing)
        
        # Y offset should account for multiple lines
        assert isinstance(offset_y, int)
        assert -240 <= offset_y <= 240