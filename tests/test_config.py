"""Tests for configuration management."""

import pytest
import tempfile
import os
from unittest.mock import patch
from config import ConfigManager, PJSkConfig


class TestPJSkConfig:
    """Tests for PJSkConfig dataclass."""

    def test_default_config_values(self):
        """Test that default configuration values are correct."""
        config = PJSkConfig()
        
        # Text processing
        assert config.adaptive_text_sizing is True
        assert config.enable_markdown_flow is False
        
        # Messaging
        assert config.show_success_messages is True
        assert config.mention_user_on_render is False
        
        # Rendering
        assert config.default_curve_intensity == 0.5
        assert config.enable_text_shadow is True
        assert config.default_emoji_set == "apple"
        
        # Persistence
        assert config.persistence_enabled is True
        assert config.state_ttl_hours == 24
        
        # Validation ranges
        assert config.font_size_min == 18
        assert config.font_size_max == 84
        assert config.font_size_step == 4
        assert config.line_spacing_min == 0.6
        assert config.line_spacing_max == 3.0
        assert config.line_spacing_step == 0.1
        assert config.offset_min == -240
        assert config.offset_max == 240
        assert config.offset_step == 12
        assert config.max_text_length == 120


class TestConfigManager:
    """Tests for configuration management."""

    @pytest.fixture
    def temp_config_file(self):
        """Create a temporary config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = f.name
        yield temp_path
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    @pytest.fixture
    def config_manager(self, temp_config_file):
        """Create a ConfigManager with temporary file."""
        return ConfigManager(temp_config_file)

    def test_load_default_config_when_file_missing(self, temp_config_file):
        """Test loading default config when file doesn't exist."""
        # Ensure file doesn't exist
        if os.path.exists(temp_config_file):
            os.unlink(temp_config_file)
        
        manager = ConfigManager(temp_config_file)
        config = manager.load()
        
        assert isinstance(config, PJSkConfig)
        assert config.adaptive_text_sizing is True
        assert config.font_size_min == 18
        
        # File should be created
        assert os.path.exists(temp_config_file)

    def test_load_existing_config(self, config_manager, temp_config_file):
        """Test loading existing configuration."""
        # Create a config file with custom values
        import yaml
        custom_config = {
            'adaptive_text_sizing': False,
            'font_size_min': 20,
            'show_success_messages': False,
            'default_emoji_set': 'google'
        }
        
        with open(temp_config_file, 'w') as f:
            yaml.dump(custom_config, f)
        
        config = config_manager.load()
        
        assert config.adaptive_text_sizing is False
        assert config.font_size_min == 20
        assert config.show_success_messages is False
        assert config.default_emoji_set == 'google'
        
        # Other values should be defaults
        assert config.enable_markdown_flow is False
        assert config.font_size_max == 84

    def test_save_config(self, config_manager, temp_config_file):
        """Test saving configuration."""
        config = PJSkConfig(
            adaptive_text_sizing=False,
            font_size_min=24,
            default_emoji_set='twitter'
        )
        
        config_manager.save(config)
        
        # Load it back
        loaded_config = config_manager.load()
        
        assert loaded_config.adaptive_text_sizing is False
        assert loaded_config.font_size_min == 24
        assert loaded_config.default_emoji_set == 'twitter'

    def test_get_config_caching(self, config_manager):
        """Test that get() returns cached config."""
        config1 = config_manager.get()
        config2 = config_manager.get()
        
        # Should be the same object (cached)
        assert config1 is config2

    def test_update_config(self, config_manager):
        """Test updating configuration values."""
        # Get initial config
        config = config_manager.get()
        original_adaptive = config.adaptive_text_sizing
        
        # Update some values
        config_manager.update(
            adaptive_text_sizing=not original_adaptive,
            font_size_min=30,
            default_emoji_set='facebook'
        )
        
        # Get updated config
        updated_config = config_manager.get()
        
        assert updated_config.adaptive_text_sizing is not original_adaptive
        assert updated_config.font_size_min == 30
        assert updated_config.default_emoji_set == 'facebook'
        
        # Other values should remain unchanged
        assert updated_config.enable_markdown_flow is False
        assert updated_config.font_size_max == 84

    def test_handle_invalid_yaml_file(self, config_manager, temp_config_file):
        """Test handling of invalid YAML file."""
        # Write invalid YAML
        with open(temp_config_file, 'w') as f:
            f.write("invalid: yaml: content: [")
        
        # Should fall back to defaults
        config = config_manager.load()
        assert isinstance(config, PJSkConfig)
        assert config.adaptive_text_sizing is True

    def test_handle_partial_config_file(self, config_manager, temp_config_file):
        """Test handling of partial configuration file."""
        # Write partial config
        import yaml
        partial_config = {
            'adaptive_text_sizing': False,
            'font_size_min': 25
            # Missing many other fields
        }
        
        with open(temp_config_file, 'w') as f:
            yaml.dump(partial_config, f)
        
        config = config_manager.load()
        
        # Should have custom values for specified fields
        assert config.adaptive_text_sizing is False
        assert config.font_size_min == 25
        
        # Should have defaults for missing fields
        assert config.enable_markdown_flow is False
        assert config.font_size_max == 84
        assert config.default_emoji_set == 'apple'

    def test_config_directory_creation(self, temp_config_file):
        """Test that config directory is created if it doesn't exist."""
        # Use a path in a non-existent directory
        dir_path = os.path.dirname(temp_config_file)
        if os.path.exists(dir_path):
            os.rmdir(dir_path)
        
        assert not os.path.exists(dir_path)
        
        manager = ConfigManager(temp_config_file)
        config = manager.load()
        
        # Directory should be created
        assert os.path.exists(dir_path)
        assert os.path.exists(temp_config_file)