"""
Test suite for PJSk adjustment commands.
"""

import pytest
from unittest.mock import Mock
from main import MyPlugin


class TestPJSkDrawCommand:
    """Tests for the pjsk.draw command."""

    @pytest.fixture
    def mock_context(self):
        """Create a mock Context object."""
        context = Mock()
        return context

    @pytest.fixture
    def plugin(self, mock_context):
        """Create a plugin instance with mock context."""
        return MyPlugin(mock_context)

    @pytest.mark.asyncio
    async def test_draw_creates_initial_state(self, plugin):
        """Test that draw command creates initial state."""
        mock_event = Mock()
        mock_event.platform = "test"
        mock_event.session_id = "test_session"
        mock_event.message_str = ""
        mock_event.plain_result = Mock(return_value="result")

        result_generator = plugin.draw(mock_event)
        result = await result_generator.__anext__()

        key = ("test", "test_session")
        state = plugin._state_manager.get(key)
        assert state is not None
        assert state.text == "这是一个新的卡面"
        assert state.font_size == 42
        assert state.line_spacing == 1.20
        assert state.curve_enabled is False
        assert state.offset_x == 0
        assert state.offset_y == 0
        assert state.role == "初音未来"

    @pytest.mark.asyncio
    async def test_draw_with_custom_text(self, plugin):
        """Test that draw command accepts custom text."""
        mock_event = Mock()
        mock_event.platform = "test"
        mock_event.session_id = "test_session"
        mock_event.message_str = "自定义文本"
        mock_event.plain_result = Mock(return_value="result")

        result_generator = plugin.draw(mock_event)
        await result_generator.__anext__()

        key = ("test", "test_session")
        state = plugin._state_manager.get(key)
        assert state.text == "自定义文本"

    @pytest.mark.asyncio
    async def test_draw_updates_existing_text(self, plugin):
        """Test that draw command updates text on existing state."""
        mock_event = Mock()
        mock_event.platform = "test"
        mock_event.session_id = "test_session"
        mock_event.message_str = "初始文本"
        mock_event.plain_result = Mock(return_value="result")

        result_generator = plugin.draw(mock_event)
        await result_generator.__anext__()

        mock_event.message_str = "更新后的文本"
        result_generator = plugin.draw(mock_event)
        await result_generator.__anext__()

        key = ("test", "test_session")
        state = plugin._state_manager.get(key)
        assert state.text == "更新后的文本"


class TestAdjustCommandErrors:
    """Tests for error handling in adjust commands."""

    @pytest.fixture
    def mock_context(self):
        """Create a mock Context object."""
        context = Mock()
        return context

    @pytest.fixture
    def plugin(self, mock_context):
        """Create a plugin instance with mock context."""
        return MyPlugin(mock_context)

    @pytest.mark.asyncio
    async def test_adjust_without_state_shows_error(self, plugin):
        """Test that adjust command shows error when no state exists."""
        mock_event = Mock()
        mock_event.platform = "test"
        mock_event.session_id = "test_session"
        mock_event.message_str = "字号 48"
        mock_event.plain_result = Mock(return_value="error result")

        result_generator = plugin.adjust(mock_event)
        result = await result_generator.__anext__()

        mock_event.plain_result.assert_called_once()
        call_args = mock_event.plain_result.call_args[0][0]
        assert "未找到历史渲染" in call_args

    @pytest.mark.asyncio
    async def test_adjust_empty_message_shows_guidance(self, plugin):
        """Test that adjust command shows guidance when message is empty."""
        mock_event = Mock()
        mock_event.platform = "test"
        mock_event.session_id = "test_session"
        mock_event.message_str = ""
        mock_event.plain_result = Mock(return_value="guidance result")

        result_generator = plugin.adjust(mock_event)
        result = await result_generator.__anext__()

        mock_event.plain_result.assert_called_once()
        call_args = mock_event.plain_result.call_args[0][0]
        assert "指令指南" in call_args


class TestAdjustTextCommand:
    """Tests for text adjustment subcommand."""

    @pytest.fixture
    def plugin_with_state(self):
        """Create a plugin with initialized state."""
        context = Mock()
        plugin = MyPlugin(context)
        mock_event = Mock()
        mock_event.platform = "test"
        mock_event.session_id = "test_session"
        mock_event.message_str = ""
        mock_event.plain_result = Mock(return_value="result")
        return plugin, mock_event

    @pytest.mark.asyncio
    async def test_adjust_text(self, plugin_with_state):
        """Test adjusting text."""
        plugin, mock_event = plugin_with_state

        result_generator = plugin.draw(mock_event)
        await result_generator.__anext__()

        mock_event.message_str = "文本 新的文本内容"
        result_generator = plugin.adjust(mock_event)
        await result_generator.__anext__()

        key = ("test", "test_session")
        state = plugin._state_manager.get(key)
        assert state.text == "新的文本内容"

    @pytest.mark.asyncio
    async def test_adjust_text_empty_shows_error(self, plugin_with_state):
        """Test adjusting text with empty value shows error."""
        plugin, mock_event = plugin_with_state

        result_generator = plugin.draw(mock_event)
        await result_generator.__anext__()

        mock_event.message_str = "文本"
        mock_event.plain_result.reset_mock()
        result_generator = plugin.adjust(mock_event)
        await result_generator.__anext__()

        call_args = mock_event.plain_result.call_args[0][0]
        assert "请提供要更新的文本内容" in call_args


class TestAdjustFontSizeCommand:
    """Tests for font size adjustment subcommand."""

    @pytest.fixture
    def plugin_with_state(self):
        """Create a plugin with initialized state."""
        context = Mock()
        plugin = MyPlugin(context)
        mock_event = Mock()
        mock_event.platform = "test"
        mock_event.session_id = "test_session"
        mock_event.message_str = ""
        mock_event.plain_result = Mock(return_value="result")
        return plugin, mock_event

    @pytest.mark.asyncio
    async def test_adjust_font_size_absolute(self, plugin_with_state):
        """Test setting font size to absolute value."""
        plugin, mock_event = plugin_with_state

        result_generator = plugin.draw(mock_event)
        await result_generator.__anext__()

        mock_event.message_str = "字号 60"
        result_generator = plugin.adjust(mock_event)
        await result_generator.__anext__()

        key = ("test", "test_session")
        state = plugin._state_manager.get(key)
        assert state.font_size == 60

    @pytest.mark.asyncio
    async def test_adjust_font_size_increase(self, plugin_with_state):
        """Test increasing font size."""
        plugin, mock_event = plugin_with_state

        result_generator = plugin.draw(mock_event)
        await result_generator.__anext__()

        key = ("test", "test_session")
        original_size = plugin._state_manager.get(key).font_size

        mock_event.message_str = "字号.大"
        result_generator = plugin.adjust(mock_event)
        await result_generator.__anext__()

        state = plugin._state_manager.get(key)
        assert state.font_size == original_size + 4

    @pytest.mark.asyncio
    async def test_adjust_font_size_decrease(self, plugin_with_state):
        """Test decreasing font size."""
        plugin, mock_event = plugin_with_state

        result_generator = plugin.draw(mock_event)
        await result_generator.__anext__()

        key = ("test", "test_session")
        original_size = plugin._state_manager.get(key).font_size

        mock_event.message_str = "字号.小"
        result_generator = plugin.adjust(mock_event)
        await result_generator.__anext__()

        state = plugin._state_manager.get(key)
        assert state.font_size == original_size - 4

    @pytest.mark.asyncio
    async def test_adjust_font_size_clamps_to_max(self, plugin_with_state):
        """Test that font size is clamped to maximum."""
        plugin, mock_event = plugin_with_state

        result_generator = plugin.draw(mock_event)
        await result_generator.__anext__()

        mock_event.message_str = "字号 999"
        result_generator = plugin.adjust(mock_event)
        await result_generator.__anext__()

        key = ("test", "test_session")
        state = plugin._state_manager.get(key)
        assert state.font_size == 84

    @pytest.mark.asyncio
    async def test_adjust_font_size_clamps_to_min(self, plugin_with_state):
        """Test that font size is clamped to minimum."""
        plugin, mock_event = plugin_with_state

        result_generator = plugin.draw(mock_event)
        await result_generator.__anext__()

        mock_event.message_str = "字号 1"
        result_generator = plugin.adjust(mock_event)
        await result_generator.__anext__()

        key = ("test", "test_session")
        state = plugin._state_manager.get(key)
        assert state.font_size == 18


class TestAdjustLineSpacingCommand:
    """Tests for line spacing adjustment subcommand."""

    @pytest.fixture
    def plugin_with_state(self):
        """Create a plugin with initialized state."""
        context = Mock()
        plugin = MyPlugin(context)
        mock_event = Mock()
        mock_event.platform = "test"
        mock_event.session_id = "test_session"
        mock_event.message_str = ""
        mock_event.plain_result = Mock(return_value="result")
        return plugin, mock_event

    @pytest.mark.asyncio
    async def test_adjust_line_spacing_absolute(self, plugin_with_state):
        """Test setting line spacing to absolute value."""
        plugin, mock_event = plugin_with_state

        result_generator = plugin.draw(mock_event)
        await result_generator.__anext__()

        mock_event.message_str = "行距 1.5"
        result_generator = plugin.adjust(mock_event)
        await result_generator.__anext__()

        key = ("test", "test_session")
        state = plugin._state_manager.get(key)
        assert state.line_spacing == 1.5

    @pytest.mark.asyncio
    async def test_adjust_line_spacing_increase(self, plugin_with_state):
        """Test increasing line spacing."""
        plugin, mock_event = plugin_with_state

        result_generator = plugin.draw(mock_event)
        await result_generator.__anext__()

        key = ("test", "test_session")
        original_spacing = plugin._state_manager.get(key).line_spacing

        mock_event.message_str = "行距.大"
        result_generator = plugin.adjust(mock_event)
        await result_generator.__anext__()

        state = plugin._state_manager.get(key)
        assert abs(state.line_spacing - (original_spacing + 0.10)) < 1e-6

    @pytest.mark.asyncio
    async def test_adjust_line_spacing_decrease(self, plugin_with_state):
        """Test decreasing line spacing."""
        plugin, mock_event = plugin_with_state

        result_generator = plugin.draw(mock_event)
        await result_generator.__anext__()

        key = ("test", "test_session")
        original_spacing = plugin._state_manager.get(key).line_spacing

        mock_event.message_str = "行距.小"
        result_generator = plugin.adjust(mock_event)
        await result_generator.__anext__()

        state = plugin._state_manager.get(key)
        assert abs(state.line_spacing - (original_spacing - 0.10)) < 1e-6


class TestAdjustCurveCommand:
    """Tests for curve toggle subcommand."""

    @pytest.fixture
    def plugin_with_state(self):
        """Create a plugin with initialized state."""
        context = Mock()
        plugin = MyPlugin(context)
        mock_event = Mock()
        mock_event.platform = "test"
        mock_event.session_id = "test_session"
        mock_event.message_str = ""
        mock_event.plain_result = Mock(return_value="result")
        return plugin, mock_event

    @pytest.mark.asyncio
    async def test_adjust_curve_toggle(self, plugin_with_state):
        """Test toggling curve."""
        plugin, mock_event = plugin_with_state

        result_generator = plugin.draw(mock_event)
        await result_generator.__anext__()

        key = ("test", "test_session")
        original_state = plugin._state_manager.get(key).curve_enabled

        mock_event.message_str = "曲线 切换"
        result_generator = plugin.adjust(mock_event)
        await result_generator.__anext__()

        state = plugin._state_manager.get(key)
        assert state.curve_enabled == (not original_state)

    @pytest.mark.asyncio
    async def test_adjust_curve_on(self, plugin_with_state):
        """Test turning curve on."""
        plugin, mock_event = plugin_with_state

        result_generator = plugin.draw(mock_event)
        await result_generator.__anext__()

        mock_event.message_str = "曲线 开"
        result_generator = plugin.adjust(mock_event)
        await result_generator.__anext__()

        key = ("test", "test_session")
        state = plugin._state_manager.get(key)
        assert state.curve_enabled is True

    @pytest.mark.asyncio
    async def test_adjust_curve_off(self, plugin_with_state):
        """Test turning curve off."""
        plugin, mock_event = plugin_with_state

        result_generator = plugin.draw(mock_event)
        await result_generator.__anext__()

        mock_event.message_str = "曲线 关"
        result_generator = plugin.adjust(mock_event)
        await result_generator.__anext__()

        key = ("test", "test_session")
        state = plugin._state_manager.get(key)
        assert state.curve_enabled is False


class TestAdjustPositionCommand:
    """Tests for position adjustment subcommand."""

    @pytest.fixture
    def plugin_with_state(self):
        """Create a plugin with initialized state."""
        context = Mock()
        plugin = MyPlugin(context)
        mock_event = Mock()
        mock_event.platform = "test"
        mock_event.session_id = "test_session"
        mock_event.message_str = ""
        mock_event.plain_result = Mock(return_value="result")
        return plugin, mock_event

    @pytest.mark.asyncio
    async def test_adjust_position_up(self, plugin_with_state):
        """Test moving position up."""
        plugin, mock_event = plugin_with_state

        result_generator = plugin.draw(mock_event)
        await result_generator.__anext__()

        key = ("test", "test_session")
        original_y = plugin._state_manager.get(key).offset_y

        mock_event.message_str = "位置.上"
        result_generator = plugin.adjust(mock_event)
        await result_generator.__anext__()

        state = plugin._state_manager.get(key)
        assert state.offset_y == original_y - 12

    @pytest.mark.asyncio
    async def test_adjust_position_down(self, plugin_with_state):
        """Test moving position down."""
        plugin, mock_event = plugin_with_state

        result_generator = plugin.draw(mock_event)
        await result_generator.__anext__()

        key = ("test", "test_session")
        original_y = plugin._state_manager.get(key).offset_y

        mock_event.message_str = "位置.下"
        result_generator = plugin.adjust(mock_event)
        await result_generator.__anext__()

        state = plugin._state_manager.get(key)
        assert state.offset_y == original_y + 12

    @pytest.mark.asyncio
    async def test_adjust_position_left(self, plugin_with_state):
        """Test moving position left."""
        plugin, mock_event = plugin_with_state

        result_generator = plugin.draw(mock_event)
        await result_generator.__anext__()

        key = ("test", "test_session")
        original_x = plugin._state_manager.get(key).offset_x

        mock_event.message_str = "位置.左"
        result_generator = plugin.adjust(mock_event)
        await result_generator.__anext__()

        state = plugin._state_manager.get(key)
        assert state.offset_x == original_x - 12

    @pytest.mark.asyncio
    async def test_adjust_position_right(self, plugin_with_state):
        """Test moving position right."""
        plugin, mock_event = plugin_with_state

        result_generator = plugin.draw(mock_event)
        await result_generator.__anext__()

        key = ("test", "test_session")
        original_x = plugin._state_manager.get(key).offset_x

        mock_event.message_str = "位置.右"
        result_generator = plugin.adjust(mock_event)
        await result_generator.__anext__()

        state = plugin._state_manager.get(key)
        assert state.offset_x == original_x + 12

    @pytest.mark.asyncio
    async def test_adjust_position_with_custom_step(self, plugin_with_state):
        """Test moving position with custom step."""
        plugin, mock_event = plugin_with_state

        result_generator = plugin.draw(mock_event)
        await result_generator.__anext__()

        key = ("test", "test_session")
        original_x = plugin._state_manager.get(key).offset_x

        mock_event.message_str = "位置.右 24"
        result_generator = plugin.adjust(mock_event)
        await result_generator.__anext__()

        state = plugin._state_manager.get(key)
        assert state.offset_x == original_x + 24


class TestAdjustRoleCommand:
    """Tests for role change subcommand."""

    @pytest.fixture
    def plugin_with_state(self):
        """Create a plugin with initialized state."""
        context = Mock()
        plugin = MyPlugin(context)
        mock_event = Mock()
        mock_event.platform = "test"
        mock_event.session_id = "test_session"
        mock_event.message_str = ""
        mock_event.plain_result = Mock(return_value="result")
        return plugin, mock_event

    @pytest.mark.asyncio
    async def test_adjust_role_by_name(self, plugin_with_state):
        """Test changing role by name."""
        plugin, mock_event = plugin_with_state

        result_generator = plugin.draw(mock_event)
        await result_generator.__anext__()

        mock_event.message_str = "人物 星乃一歌"
        result_generator = plugin.adjust(mock_event)
        await result_generator.__anext__()

        key = ("test", "test_session")
        state = plugin._state_manager.get(key)
        assert state.role == "星乃一歌"

    @pytest.mark.asyncio
    async def test_adjust_role_by_alias(self, plugin_with_state):
        """Test changing role by alias."""
        plugin, mock_event = plugin_with_state

        result_generator = plugin.draw(mock_event)
        await result_generator.__anext__()

        mock_event.message_str = "人物 一歌"
        result_generator = plugin.adjust(mock_event)
        await result_generator.__anext__()

        key = ("test", "test_session")
        state = plugin._state_manager.get(key)
        assert state.role == "星乃一歌"

    @pytest.mark.asyncio
    async def test_adjust_role_random(self, plugin_with_state):
        """Test changing role randomly."""
        plugin, mock_event = plugin_with_state

        result_generator = plugin.draw(mock_event)
        await result_generator.__anext__()

        key = ("test", "test_session")
        original_role = plugin._state_manager.get(key).role

        mock_event.message_str = "人物 -r"
        result_generator = plugin.adjust(mock_event)
        await result_generator.__anext__()

        state = plugin._state_manager.get(key)
        assert state.role in plugin._role_names

    @pytest.mark.asyncio
    async def test_adjust_role_invalid_shows_error(self, plugin_with_state):
        """Test invalid role shows error."""
        plugin, mock_event = plugin_with_state

        result_generator = plugin.draw(mock_event)
        await result_generator.__anext__()

        mock_event.message_str = "人物 不存在的角色"
        mock_event.plain_result.reset_mock()
        result_generator = plugin.adjust(mock_event)
        await result_generator.__anext__()

        call_args = mock_event.plain_result.call_args[0][0]
        assert "未识别的角色" in call_args


class TestAdjustCommandSequence:
    """Tests for sequences of adjustment commands."""

    @pytest.fixture
    def plugin_with_state(self):
        """Create a plugin with initialized state."""
        context = Mock()
        plugin = MyPlugin(context)
        mock_event = Mock()
        mock_event.platform = "test"
        mock_event.session_id = "test_session"
        mock_event.message_str = ""
        mock_event.plain_result = Mock(return_value="result")
        return plugin, mock_event

    @pytest.mark.asyncio
    async def test_multiple_adjustments_in_sequence(self, plugin_with_state):
        """Test multiple adjustments update state correctly."""
        plugin, mock_event = plugin_with_state

        result_generator = plugin.draw(mock_event)
        await result_generator.__anext__()

        mock_event.message_str = "文本 测试文本"
        result_generator = plugin.adjust(mock_event)
        await result_generator.__anext__()

        mock_event.message_str = "字号 50"
        result_generator = plugin.adjust(mock_event)
        await result_generator.__anext__()

        mock_event.message_str = "行距 1.8"
        result_generator = plugin.adjust(mock_event)
        await result_generator.__anext__()

        mock_event.message_str = "曲线 开"
        result_generator = plugin.adjust(mock_event)
        await result_generator.__anext__()

        mock_event.message_str = "位置.上"
        result_generator = plugin.adjust(mock_event)
        await result_generator.__anext__()

        mock_event.message_str = "人物 一歌"
        result_generator = plugin.adjust(mock_event)
        await result_generator.__anext__()

        key = ("test", "test_session")
        state = plugin._state_manager.get(key)
        assert state.text == "测试文本"
        assert state.font_size == 50
        assert state.line_spacing == 1.8
        assert state.curve_enabled is True
        assert state.offset_y == -12
        assert state.role == "星乃一歌"


class TestStateKeyGeneration:
    """Tests for state key generation logic."""

    @pytest.fixture
    def plugin(self):
        """Create a plugin instance."""
        context = Mock()
        return MyPlugin(context)

    def test_state_key_uses_session_id(self, plugin):
        """Test that state key uses session_id when available."""
        mock_event = Mock()
        mock_event.platform = "test_platform"
        mock_event.session_id = "test_session_id"

        key = plugin._state_key(mock_event)
        assert key == ("test_platform", "test_session_id")

    def test_state_key_falls_back_to_sender_id(self, plugin):
        """Test that state key falls back to sender_id."""
        mock_event = Mock()
        mock_event.platform = "test_platform"
        mock_event.session_id = None
        mock_event.get_sender_id = Mock(return_value="sender_123")

        key = plugin._state_key(mock_event)
        assert key == ("test_platform", "sender_123")

    def test_state_key_falls_back_to_sender_name(self, plugin):
        """Test that state key falls back to sender_name."""
        mock_event = Mock()
        mock_event.platform = "test_platform"
        mock_event.session_id = None
        mock_event.get_sender_id = Mock(return_value=None)
        mock_event.get_sender_name = Mock(return_value="TestUser")

        key = plugin._state_key(mock_event)
        assert key == ("test_platform", "TestUser")
