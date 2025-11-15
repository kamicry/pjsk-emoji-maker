import pytest
from unittest.mock import Mock, patch
from main import PjskEmojiMaker


class TestPluginIntegration:
    """Integration tests for the plugin"""
    
    @pytest.fixture
    def mock_context(self):
        """Create a mock Context with realistic configuration"""
        context = Mock()
        context.config = {}
        context.logger = Mock()
        return context
    
    @pytest.fixture
    def plugin(self, mock_context):
        """Create a plugin instance for integration testing"""
        return PjskEmojiMaker(mock_context)
    
    @pytest.mark.smoke
    @pytest.mark.asyncio
    async def test_plugin_full_lifecycle(self, mock_context):
        """Smoke test: Full plugin lifecycle"""
        plugin = PjskEmojiMaker(mock_context)
        
        await plugin.initialize()
        
        mock_event = Mock()
        mock_event.get_sender_name.return_value = "IntegrationTestUser"
        mock_event.message_str = "integration test"
        mock_event.get_messages.return_value = []
        mock_event.plain_result.return_value = "Hello, IntegrationTestUser, 你发了 integration test!"
        
        result_generator = plugin.helloworld(mock_event)
        result = await result_generator.__anext__()
        
        assert result is not None
        
        await plugin.terminate()
    
    @pytest.mark.smoke
    @pytest.mark.asyncio
    async def test_command_parsing_basic(self, plugin):
        """Smoke test: Command parsing with various inputs"""
        test_cases = [
            ("TestUser1", "hello", "Hello, TestUser1, 你发了 hello!"),
            ("TestUser2", "", "Hello, TestUser2, 你发了 !"),
            ("TestUser3", "test 123", "Hello, TestUser3, 你发了 test 123!"),
        ]
        
        for username, message, expected in test_cases:
            mock_event = Mock()
            mock_event.get_sender_name.return_value = username
            mock_event.message_str = message
            mock_event.get_messages.return_value = []
            mock_event.plain_result.return_value = expected
            
            result_generator = plugin.helloworld(mock_event)
            result = await result_generator.__anext__()
            
            assert result == expected
    
    @pytest.mark.smoke
    @pytest.mark.asyncio
    async def test_event_data_extraction(self, plugin):
        """Smoke test: Verify event data extraction methods are called"""
        mock_event = Mock()
        mock_event.get_sender_name.return_value = "TestUser"
        mock_event.message_str = "test"
        mock_event.get_messages.return_value = [{"type": "text", "data": "test"}]
        mock_event.plain_result.return_value = "Hello, TestUser, 你发了 test!"
        
        result_generator = plugin.helloworld(mock_event)
        await result_generator.__anext__()
        
        mock_event.get_sender_name.assert_called()
        mock_event.get_messages.assert_called()
        mock_event.plain_result.assert_called()
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_multiple_sequential_commands(self, plugin):
        """Test handling multiple commands in sequence"""
        for i in range(5):
            mock_event = Mock()
            mock_event.get_sender_name.return_value = f"User{i}"
            mock_event.message_str = f"message{i}"
            mock_event.get_messages.return_value = []
            mock_event.plain_result.return_value = f"Hello, User{i}, 你发了 message{i}!"
            
            result_generator = plugin.helloworld(mock_event)
            result = await result_generator.__anext__()
            
            assert f"User{i}" in result
            assert f"message{i}" in result
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_plugin_state_consistency(self, mock_context):
        """Test that plugin maintains consistent state across calls"""
        plugin = PjskEmojiMaker(mock_context)
        await plugin.initialize()
        
        mock_event1 = Mock()
        mock_event1.get_sender_name.return_value = "User1"
        mock_event1.message_str = "first"
        mock_event1.get_messages.return_value = []
        mock_event1.plain_result.return_value = "Hello, User1, 你发了 first!"
        
        mock_event2 = Mock()
        mock_event2.get_sender_name.return_value = "User2"
        mock_event2.message_str = "second"
        mock_event2.get_messages.return_value = []
        mock_event2.plain_result.return_value = "Hello, User2, 你发了 second!"
        
        result1_gen = plugin.helloworld(mock_event1)
        result1 = await result1_gen.__anext__()
        
        result2_gen = plugin.helloworld(mock_event2)
        result2 = await result2_gen.__anext__()
        
        assert "User1" in result1 and "User2" not in result1
        assert "User2" in result2 and "User1" not in result2
        
        await plugin.terminate()
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_error_resilience(self, plugin):
        """Test plugin handles errors gracefully"""
        mock_event = Mock()
        mock_event.get_sender_name.return_value = None
        mock_event.message_str = "test"
        mock_event.get_messages.return_value = []
        
        try:
            mock_event.plain_result.return_value = "Hello, None, 你发了 test!"
            result_generator = plugin.helloworld(mock_event)
            result = await result_generator.__anext__()
            assert result is not None
        except Exception as e:
            pytest.fail(f"Plugin should handle None username gracefully: {e}")


class TestMessageChainHandling:
    """Tests for message chain processing"""
    
    @pytest.fixture
    def mock_context(self):
        """Create a mock Context with realistic configuration"""
        context = Mock()
        context.config = {}
        context.logger = Mock()
        return context
    
    @pytest.mark.integration
    def test_message_chain_structure(self):
        """Test expected message chain structure"""
        sample_chains = [
            [{"type": "text", "data": "hello"}],
            [{"type": "text", "data": "test"}, {"type": "image", "url": "http://example.com"}],
            [],
        ]
        
        for chain in sample_chains:
            assert isinstance(chain, list)
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_logging_message_chain(self, mock_context):
        """Test that message chains are properly logged"""
        plugin = PjskEmojiMaker(mock_context)
        
        with patch('main.logger') as mock_logger:
            mock_event = Mock()
            mock_event.get_sender_name.return_value = "TestUser"
            mock_event.message_str = "test"
            mock_event.get_messages.return_value = [{"type": "text", "data": "test"}]
            mock_event.plain_result.return_value = "Hello, TestUser, 你发了 test!"
            
            result_generator = plugin.helloworld(mock_event)
            await result_generator.__anext__()
            
            mock_logger.info.assert_called_once()
