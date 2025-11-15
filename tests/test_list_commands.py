"""Test suite for PJSk list commands."""

import pytest
from unittest.mock import Mock
from main import PjskEmojiMaker


class TestListRootCommand:
    """Tests for the pjsk root command."""

    @pytest.fixture
    def mock_context(self):
        """Create a mock Context object."""
        context = Mock()
        return context

    @pytest.fixture
    def plugin(self, mock_context):
        """Create a plugin instance with mock context."""
        return PjskEmojiMaker(mock_context)

    @pytest.mark.asyncio
    async def test_list_root_shows_help(self, plugin):
        """Test that pjsk root command shows help."""
        mock_event = Mock()
        mock_event.message_str = ""
        
        def side_effect(text):
            return text
        mock_event.plain_result.side_effect = side_effect
        
        result_generator = plugin.list_root(mock_event)
        result = await result_generator.__anext__()
        
        result_text = str(result)
        assert "Project SEKAI" in result_text or "表情包制作工具" in result_text


class TestListGuideCommand:
    """Tests for the pjsk.列表 list guide command."""

    @pytest.fixture
    def mock_context(self):
        """Create a mock Context object."""
        context = Mock()
        return context

    @pytest.fixture
    def plugin(self, mock_context):
        """Create a plugin instance with mock context."""
        return PjskEmojiMaker(mock_context)

    @pytest.mark.asyncio
    async def test_list_guide_without_args_shows_options(self, plugin):
        """Test that list guide without args shows options."""
        mock_event = Mock()
        mock_event.message_str = ""
        
        def side_effect(text):
            return text
        mock_event.plain_result.side_effect = side_effect
        
        result_generator = plugin.list_guide(mock_event)
        result = await result_generator.__anext__()
        
        result_text = str(result)
        assert "全部" in result_text or "角色分类" in result_text or "展开指定角色" in result_text

    @pytest.mark.asyncio
    async def test_list_guide_with_all_option(self, plugin):
        """Test that list guide with 全部 option shows all characters."""
        mock_event = Mock()
        mock_event.message_str = "全部"
        
        def side_effect(text):
            return text
        mock_event.plain_result.side_effect = side_effect
        
        result_generator = plugin.list_guide(mock_event)
        result = await result_generator.__anext__()
        
        result_text = str(result)
        assert "初音未来" in result_text

    @pytest.mark.asyncio
    async def test_list_guide_with_group_option(self, plugin):
        """Test that list guide with 角色分类 option shows grouped characters."""
        mock_event = Mock()
        mock_event.message_str = "角色分类"
        
        def side_effect(text):
            return text
        mock_event.plain_result.side_effect = side_effect
        
        result_generator = plugin.list_guide(mock_event)
        result = await result_generator.__anext__()
        
        result_text = str(result)
        assert "Leo" in result_text or "MORE" in result_text or "SQUAD" in result_text or "25:00" in result_text


class TestListAllCommand:
    """Tests for the pjsk.列表.全部 list all command."""

    @pytest.fixture
    def mock_context(self):
        """Create a mock Context object."""
        context = Mock()
        return context

    @pytest.fixture
    def plugin(self, mock_context):
        """Create a plugin instance with mock context."""
        return PjskEmojiMaker(mock_context)

    @pytest.mark.asyncio
    async def test_list_all_shows_all_characters(self, plugin):
        """Test that list all command shows all characters."""
        mock_event = Mock()
        mock_event.message_str = ""
        
        def side_effect(text):
            return text
        mock_event.plain_result.side_effect = side_effect
        
        result_generator = plugin.list_all(mock_event)
        result = await result_generator.__anext__()
        
        result_text = str(result)
        assert "初音未来" in result_text
        assert "星乃一歌" in result_text or "一歌" in result_text


class TestListByGroupCommand:
    """Tests for the pjsk.列表.角色分类 list by group command."""

    @pytest.fixture
    def mock_context(self):
        """Create a mock Context object."""
        context = Mock()
        return context

    @pytest.fixture
    def plugin(self, mock_context):
        """Create a plugin instance with mock context."""
        return PjskEmojiMaker(mock_context)

    @pytest.mark.asyncio
    async def test_list_by_group_shows_groups(self, plugin):
        """Test that list by group command shows character groups."""
        mock_event = Mock()
        mock_event.message_str = ""
        
        def side_effect(text):
            return text
        mock_event.plain_result.side_effect = side_effect
        
        result_generator = plugin.list_by_group(mock_event)
        result = await result_generator.__anext__()
        
        result_text = str(result)
        # Should show at least one group name
        assert ("Leo/need" in result_text or
                "MORE MORE JUMP!" in result_text or
                "Vivid BAD SQUAD" in result_text or
                "Nightcord at 25:00" in result_text or
                "角色分类" in result_text)


class TestListExpandCharacterCommand:
    """Tests for the pjsk.列表.展开指定角色 expand specific character command."""

    @pytest.fixture
    def mock_context(self):
        """Create a mock Context object."""
        context = Mock()
        return context

    @pytest.fixture
    def plugin(self, mock_context):
        """Create a plugin instance with mock context."""
        return PjskEmojiMaker(mock_context)

    @pytest.mark.asyncio
    async def test_list_expand_without_character_shows_error(self, plugin):
        """Test that expand without character name shows error."""
        mock_event = Mock()
        mock_event.message_str = ""
        
        def side_effect(text):
            return text
        mock_event.plain_result.side_effect = side_effect
        
        result_generator = plugin.list_expand_character(mock_event)
        result = await result_generator.__anext__()
        
        result_text = str(result)
        assert "请提供" in result_text or "角色名称" in result_text

    @pytest.mark.asyncio
    async def test_list_expand_with_character_name(self, plugin):
        """Test that expand with valid character name shows details."""
        mock_event = Mock()
        mock_event.message_str = "初音未来"
        
        def side_effect(text):
            return text
        mock_event.plain_result.side_effect = side_effect
        
        result_generator = plugin.list_expand_character(mock_event)
        result = await result_generator.__anext__()
        
        result_text = str(result)
        assert "初音未来" in result_text or "miku" in result_text

    @pytest.mark.asyncio
    async def test_list_expand_with_character_alias(self, plugin):
        """Test that expand with character alias resolves correctly."""
        mock_event = Mock()
        mock_event.message_str = "miku"
        
        def side_effect(text):
            return text
        mock_event.plain_result.side_effect = side_effect
        
        result_generator = plugin.list_expand_character(mock_event)
        result = await result_generator.__anext__()
        
        result_text = str(result)
        assert "初音未来" in result_text or "miku" in result_text or "Hatsune" in result_text or "hatsune" in result_text

    @pytest.mark.asyncio
    async def test_list_expand_with_invalid_character(self, plugin):
        """Test that expand with invalid character shows error."""
        mock_event = Mock()
        mock_event.message_str = "不存在的角色"
        
        def side_effect(text):
            return text
        mock_event.plain_result.side_effect = side_effect
        
        result_generator = plugin.list_expand_character(mock_event)
        result = await result_generator.__anext__()
        
        result_text = str(result)
        assert "未找到" in result_text or "not found" in result_text.lower()
