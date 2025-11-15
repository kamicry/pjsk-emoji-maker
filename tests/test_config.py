"""Tests for configuration management.

Configuration is now handled by AstrBot's _conf_schema.json system.
This tests the ConfigWrapper which bridges AstrBotConfig and plugin code.
"""

import pytest
from unittest.mock import Mock
from main import ConfigWrapper


class TestConfigWrapper:
    """Tests for ConfigWrapper class."""

    @pytest.fixture
    def mock_astrbot_config(self):
        """Create a mock AstrBotConfig."""
        config = Mock()
        config.get = Mock(side_effect=lambda key, default=None: {
            'adaptive_text_sizing': True,
            'enable_markdown_flow': False,
            'show_success_messages': True,
            'mention_user_on_render': True,
            'retract_delay_ms': 0,
            'default_curve_intensity': 0.5,
            'enable_text_shadow': True,
            'persistence_enabled': True,
            'state_ttl_hours': 24,
        }.get(key, default))
        return config

    @pytest.fixture
    def config_wrapper(self, mock_astrbot_config):
        """Create a ConfigWrapper instance."""
        return ConfigWrapper(mock_astrbot_config)

    def test_default_config_values(self, config_wrapper):
        """Test that default configuration values are correct."""
        # Text processing
        assert config_wrapper.adaptive_text_sizing is True
        assert config_wrapper.enable_markdown_flow is False
        
        # Messaging
        assert config_wrapper.show_success_messages is True
        assert config_wrapper.mention_user_on_render is True
        
        # Rendering
        assert config_wrapper.default_curve_intensity == 0.5
        assert config_wrapper.enable_text_shadow is True
        assert config_wrapper.default_emoji_set == "apple"
        
        # Persistence
        assert config_wrapper.persistence_enabled is True
        assert config_wrapper.state_ttl_hours == 24

    def test_hardcoded_validation_ranges(self, config_wrapper):
        """Test that validation ranges are hardcoded."""
        # Validation ranges - hardcoded
        assert config_wrapper.font_size_min == 18
        assert config_wrapper.font_size_max == 84
        assert config_wrapper.font_size_step == 4
        assert config_wrapper.line_spacing_min == 0.6
        assert config_wrapper.line_spacing_max == 3.0
        assert config_wrapper.line_spacing_step == 0.1
        assert config_wrapper.offset_min == -240
        assert config_wrapper.offset_max == 240
        assert config_wrapper.offset_step == 12
        assert config_wrapper.max_text_length == 120

    def test_get_method_with_defaults(self, config_wrapper):
        """Test that get method returns defaults for missing keys."""
        # Test a key that returns default
        result = config_wrapper.get('nonexistent_key', 'default_value')
        assert result == 'default_value'

    def test_config_with_custom_values(self):
        """Test ConfigWrapper with custom AstrBotConfig values."""
        config = Mock()
        config.get = Mock(side_effect=lambda key, default=None: {
            'adaptive_text_sizing': False,
            'show_success_messages': False,
            'mention_user_on_render': False,
            'retract_delay_ms': 5000,
            'default_curve_intensity': 0.7,
            'persistence_enabled': False,
            'state_ttl_hours': 12,
        }.get(key, default))
        
        wrapper = ConfigWrapper(config)
        
        assert wrapper.adaptive_text_sizing is False
        assert wrapper.show_success_messages is False
        assert wrapper.mention_user_on_render is False
        assert wrapper.retract_delay_ms == 5000
        assert wrapper.default_curve_intensity == 0.7
        assert wrapper.persistence_enabled is False
        assert wrapper.state_ttl_hours == 12

    def test_config_error_handling(self):
        """Test that ConfigWrapper handles errors gracefully."""
        config = Mock()
        config.get = Mock(side_effect=AttributeError("Config error"))
        
        wrapper = ConfigWrapper(config)
        
        # Should return defaults when error occurs
        assert wrapper.adaptive_text_sizing is True
        assert wrapper.show_success_messages is True
