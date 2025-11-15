"""Configuration management for PJSk plugin."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import yaml


@dataclass
class PJSkConfig:
    """Configuration for PJSk card rendering."""
    
    # Text processing options
    adaptive_text_sizing: bool = True
    enable_markdown_flow: bool = False
    
    # Messaging options  
    show_success_messages: bool = True
    mention_user_on_render: bool = False
    
    # Rendering options
    default_curve_intensity: float = 0.5
    enable_text_shadow: bool = True
    default_emoji_set: str = "apple"
    
    # Persistence options
    persistence_enabled: bool = True
    state_ttl_hours: int = 24
    
    # Validation ranges
    font_size_min: int = 18
    font_size_max: int = 84
    font_size_step: int = 4
    
    line_spacing_min: float = 0.6
    line_spacing_max: float = 3.0
    line_spacing_step: float = 0.1
    
    offset_min: int = -240
    offset_max: int = 240
    offset_step: int = 12
    
    max_text_length: int = 120


class ConfigManager:
    """Manages plugin configuration."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/pjsk_config.yaml"
        self._config: Optional[PJSkConfig] = None
    
    def load(self) -> PJSkConfig:
        """Load configuration from file or create default."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            
            self._config = PJSkConfig(**data)
        except FileNotFoundError:
            # Create default config
            self._config = PJSkConfig()
            self.save(self._config)
        except Exception as e:
            # Fallback to default config
            self._config = PJSkConfig()
        
        return self._config
    
    def save(self, config: PJSkConfig) -> None:
        """Save configuration to file."""
        import os
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config.__dict__, f, default_flow_style=False, allow_unicode=True)
    
    def get(self) -> PJSkConfig:
        """Get current configuration, loading if necessary."""
        if self._config is None:
            self._config = self.load()
        return self._config
    
    def update(self, **kwargs) -> None:
        """Update configuration values."""
        config = self.get()
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        self.save(config)