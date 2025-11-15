#!/usr/bin/env python3
"""Simple integration test for PJSk draw command."""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tests.mock_astrbot import setup_mocks
from config import PJSkConfig


async def test_koishi_draw_integration():
    """Integration test for pjsk.绘制 command."""
    
    # Setup mocks
    setup_mocks()
    
    # Import after mocks are set up
    from main import MyPlugin
    from unittest.mock import Mock
    
    # Create plugin instance
    mock_context = Mock()
    plugin = MyPlugin(mock_context)
    
    # Mock config for predictable results
    config = PJSkConfig(adaptive_text_sizing=False)
    plugin._config_manager._config = config
    
    # Test 1: Basic draw
    print("Test 1: Basic draw command")
    event = Mock()
    event.platform = "test"
    event.session_id = "integration_test"
    event.message_str = ""
    event.plain_result = Mock(return_value="result")
    event.get_sender_name = Mock(return_value="TestUser")
    
    result_gen = plugin.draw_koishi(event)
    result = await result_gen.__anext__()
    
    print(f"✓ Basic draw completed: {type(result).__name__}")
    
    # Test 2: Draw with text and options
    print("\nTest 2: Draw with options")
    event.message_str = '-n "Integration Test" -s 36 -c -x 20 -y -10'
    
    result_gen = plugin.draw_koishi(event)
    result = await result_gen.__anext__()
    
    print(f"✓ Draw with options completed: {type(result).__name__}")
    
    # Verify state was saved correctly
    key = ("test", "integration_test")
    state = plugin._state_manager.get(key)
    
    assert state is not None
    assert state.text == "Integration Test"
    assert state.font_size == 36
    assert state.curve_enabled is True
    assert state.offset_x == 20
    assert state.offset_y == -10
    assert state.role == "初音未来"
    
    print("✓ State saved correctly")
    
    # Test 3: Test persistence
    print("\nTest 3: Testing persistence")
    persisted_state = plugin._persistence.get_state("test", "integration_test")
    assert persisted_state is not None
    assert persisted_state.text == "Integration Test"
    assert persisted_state.font_size == 36
    
    print("✓ Persistence working correctly")
    
    # Test 4: Test helper functions
    print("\nTest 4: Testing helper functions")
    from utils import parseKoishiFlags, calculateOffsets, calculateFontSize
    
    flags = parseKoishiFlags('-n "Test" -s 48 -x 10 -y -5')
    assert flags['text'] == "Test"
    assert flags['font_size'] == 48
    assert flags['offset_x'] == 10
    assert flags['offset_y'] == -5
    
    offset_x, offset_y = calculateOffsets("Test", 42, 1.2)
    assert isinstance(offset_x, int)
    assert isinstance(offset_y, int)
    
    font_size = calculateFontSize("This is a longer test text", target_width=400)
    assert 18 <= font_size <= 84
    
    print("✓ Helper functions working correctly")
    
    print("\n🎉 All integration tests passed!")
    print("✅ pjsk.绘制 command implementation is working correctly")


if __name__ == "__main__":
    asyncio.run(test_koishi_draw_integration())