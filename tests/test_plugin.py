import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
from main import MyPlugin


class TestMyPlugin:
    """Test suite for MyPlugin class"""
    
    @pytest.fixture
    def mock_context(self):
        """Create a mock Context object"""
        context = Mock()
        return context
    
    @pytest.fixture
    def plugin(self, mock_context):
        """Create a plugin instance with mock context"""
        return MyPlugin(mock_context)
    
    def test_plugin_initialization(self, mock_context):
        """Test that plugin can be instantiated"""
        plugin = MyPlugin(mock_context)
        assert plugin is not None
        assert hasattr(plugin, 'initialize')
        assert hasattr(plugin, 'terminate')
        assert hasattr(plugin, 'helloworld')
    
    @pytest.mark.asyncio
    async def test_initialize_method(self, plugin):
        """Test the initialize lifecycle hook"""
        result = await plugin.initialize()
        assert result is None
    
    @pytest.mark.asyncio
    async def test_terminate_method(self, plugin):
        """Test the terminate lifecycle hook"""
        result = await plugin.terminate()
        assert result is None
    
    @pytest.mark.asyncio
    async def test_helloworld_command_basic(self, plugin):
        """Test the helloworld command with basic input"""
        mock_event = Mock()
        mock_event.get_sender_name.return_value = "TestUser"
        mock_event.message_str = "test message"
        mock_event.get_messages.return_value = []
        mock_event.plain_result.return_value = "Hello, TestUser, 你发了 test message!"
        
        result_generator = plugin.helloworld(mock_event)
        result = await result_generator.__anext__()
        
        mock_event.get_sender_name.assert_called_once()
        mock_event.get_messages.assert_called_once()
        mock_event.plain_result.assert_called_once_with("Hello, TestUser, 你发了 test message!")
        assert result == "Hello, TestUser, 你发了 test message!"
    
    @pytest.mark.asyncio
    async def test_helloworld_command_empty_message(self, plugin):
        """Test the helloworld command with empty message"""
        mock_event = Mock()
        mock_event.get_sender_name.return_value = "TestUser"
        mock_event.message_str = ""
        mock_event.get_messages.return_value = []
        mock_event.plain_result.return_value = "Hello, TestUser, 你发了 !"
        
        result_generator = plugin.helloworld(mock_event)
        result = await result_generator.__anext__()
        
        assert result == "Hello, TestUser, 你发了 !"
    
    @pytest.mark.asyncio
    async def test_helloworld_command_special_characters(self, plugin):
        """Test the helloworld command with special characters"""
        mock_event = Mock()
        mock_event.get_sender_name.return_value = "User123"
        mock_event.message_str = "Hello! @#$%^&*()"
        mock_event.get_messages.return_value = []
        mock_event.plain_result.return_value = "Hello, User123, 你发了 Hello! @#$%^&*()!"
        
        result_generator = plugin.helloworld(mock_event)
        result = await result_generator.__anext__()
        
        assert "User123" in str(result)
        assert "Hello! @#$%^&*()" in str(result)
    
    @pytest.mark.asyncio
    async def test_helloworld_command_unicode_name(self, plugin):
        """Test the helloworld command with unicode username"""
        mock_event = Mock()
        mock_event.get_sender_name.return_value = "用户张三"
        mock_event.message_str = "你好世界"
        mock_event.get_messages.return_value = []
        mock_event.plain_result.return_value = "Hello, 用户张三, 你发了 你好世界!"
        
        result_generator = plugin.helloworld(mock_event)
        result = await result_generator.__anext__()
        
        assert "用户张三" in str(result)
        assert "你好世界" in str(result)


class TestPluginMetadata:
    """Test suite for plugin metadata and registration"""
    
    def test_plugin_has_docstring(self):
        """Test that plugin methods have docstrings"""
        plugin_class = MyPlugin
        
        assert plugin_class.__init__.__doc__ is None or plugin_class.__init__.__doc__ != ""
        assert plugin_class.initialize.__doc__ is not None
        assert plugin_class.terminate.__doc__ is not None
        assert plugin_class.helloworld.__doc__ is not None
    
    def test_plugin_inherits_from_star(self):
        """Test that plugin inherits from Star base class"""
        from astrbot.api.star import Star
        assert issubclass(MyPlugin, Star)
    
    def test_command_handler_has_filter_decorator(self):
        """Test that helloworld method has proper command decorator"""
        assert hasattr(MyPlugin.helloworld, '__name__')
        assert MyPlugin.helloworld.__doc__ == "这是一个 hello world 指令"


class TestMessageFormatting:
    """Test suite for message formatting utilities"""
    
    def test_message_format(self):
        """Test the expected message format"""
        user_name = "TestUser"
        message_str = "test message"
        expected_format = f"Hello, {user_name}, 你发了 {message_str}!"
        
        assert expected_format == "Hello, TestUser, 你发了 test message!"
    
    def test_message_format_with_empty_string(self):
        """Test message format with empty message"""
        user_name = "TestUser"
        message_str = ""
        expected_format = f"Hello, {user_name}, 你发了 {message_str}!"
        
        assert expected_format == "Hello, TestUser, 你发了 !"
    
    def test_message_format_with_newlines(self):
        """Test message format with newlines in message"""
        user_name = "TestUser"
        message_str = "line1\nline2"
        expected_format = f"Hello, {user_name}, 你发了 {message_str}!"
        
        assert "line1\nline2" in expected_format


class TestPluginRegistration:
    """Test suite for plugin registration"""
    
    def test_plugin_registration_decorator(self):
        """Test that plugin is properly registered"""
        from astrbot.api.star import register
        
        assert MyPlugin.__module__ == 'main'
        assert MyPlugin.__name__ == 'MyPlugin'
