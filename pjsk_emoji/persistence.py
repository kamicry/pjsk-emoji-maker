"""Persistence layer for PJSk plugin state."""

from __future__ import annotations

import json
import os
import time
from dataclasses import asdict
from typing import Dict, Optional, Tuple

from .models import RenderState


class StatePersistence:
    """Handles persistent storage of render states."""
    
    def __init__(self, storage_path: str = "data/pjsk_states.json"):
        self.storage_path = storage_path
        self._ensure_storage_dir()
    
    def _ensure_storage_dir(self) -> None:
        """Ensure storage directory exists."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
    
    def _load_states(self) -> Dict[str, dict]:
        """Load states from storage file."""
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('states', {})
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}
    
    def _save_states(self, states: Dict[str, dict]) -> None:
        """Save states to storage file."""
        data = {
            'states': states,
            'last_updated': time.time()
        }
        
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _make_key(self, platform: str, session_id: str) -> str:
        """Create storage key from platform and session."""
        return f"{platform}:{session_id}"
    
    def get_state(self, platform: str, session_id: str, ttl_hours: int = 24) -> Optional[RenderState]:
        """Get stored state if not expired."""
        key = self._make_key(platform, session_id)
        states = self._load_states()
        
        if key not in states:
            return None
        
        state_data = states[key]
        
        # Check TTL
        if 'timestamp' in state_data:
            age_seconds = time.time() - state_data['timestamp']
            if age_seconds > ttl_hours * 3600:
                # Expired, remove it
                del states[key]
                self._save_states(states)
                return None
        
        # Reconstruct RenderState
        try:
            state_dict = state_data['state']
            return RenderState(**state_dict)
        except (KeyError, TypeError):
            return None
    
    def set_state(self, platform: str, session_id: str, state: RenderState) -> None:
        """Store state with timestamp."""
        key = self._make_key(platform, session_id)
        states = self._load_states()
        
        states[key] = {
            'state': asdict(state),
            'timestamp': time.time()
        }
        
        self._save_states(states)
    
    def delete_state(self, platform: str, session_id: str) -> bool:
        """Delete stored state."""
        key = self._make_key(platform, session_id)
        states = self._load_states()
        
        if key in states:
            del states[key]
            self._save_states(states)
            return True
        
        return False
    
    def cleanup_expired(self, ttl_hours: int = 24) -> int:
        """Remove expired states and return count of removed items."""
        states = self._load_states()
        cutoff_time = time.time() - (ttl_hours * 3600)
        
        expired_keys = []
        for key, state_data in states.items():
            if 'timestamp' in state_data and state_data['timestamp'] < cutoff_time:
                expired_keys.append(key)
        
        for key in expired_keys:
            del states[key]
        
        if expired_keys:
            self._save_states(states)
        
        return len(expired_keys)
    
    def get_all_states(self) -> Dict[str, RenderState]:
        """Get all non-expired states."""
        states = self._load_states()
        result = {}
        
        for key, state_data in states.items():
            try:
                state_dict = state_data['state']
                result[key] = RenderState(**state_dict)
            except (KeyError, TypeError):
                # Skip invalid states
                continue
        
        return result
