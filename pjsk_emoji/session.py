"""Session management for multi-step interactive flows."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple, Any
from enum import Enum

try:
    from astrbot.api import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class SessionState(Enum):
    """Session states for multi-step flows."""
    WAITING_CHARACTER_SELECTION = "waiting_character_selection"
    WAITING_TEXT_INPUT = "waiting_text_input"
    COMPLETED = "completed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class InteractiveSession:
    """Represents an interactive session with a user."""
    session_id: str
    platform: str
    user_id: str
    state: SessionState
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    selected_character: Optional[str] = None
    timeout_seconds: int = 30
    
    def is_expired(self) -> bool:
        """Check if session has expired."""
        return time.time() - self.last_activity > self.timeout_seconds
    
    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = time.time()


class SessionManager:
    """Manages interactive sessions for multi-step flows."""
    
    def __init__(self):
        self._sessions: Dict[Tuple[str, str], InteractiveSession] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False
    
    def start_cleanup_task(self) -> None:
        """Start the background cleanup task."""
        if not self._running:
            try:
                self._running = True
                self._cleanup_task = asyncio.create_task(self._cleanup_expired_sessions())
            except RuntimeError:
                # No event loop running - cleanup will be done manually
                logger.debug("No event loop available, cleanup task not started")
                self._running = False
    
    async def stop_cleanup_task(self) -> None:
        """Stop the background cleanup task."""
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
    
    async def _cleanup_expired_sessions(self) -> None:
        """Background task to clean up expired sessions."""
        while self._running:
            try:
                await asyncio.sleep(10)  # Check every 10 seconds
                current_time = time.time()
                expired_keys = [
                    key for key, session in self._sessions.items()
                    if current_time - session.last_activity > session.timeout_seconds
                ]
                
                for key in expired_keys:
                    session = self._sessions.get(key)
                    if session:
                        session.state = SessionState.TIMEOUT
                        logger.debug(f"Session {key} expired due to timeout")
                    del self._sessions[key]
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in session cleanup: {e}")
    
    def create_session(
        self,
        platform: str,
        user_id: str,
        initial_state: SessionState = SessionState.WAITING_CHARACTER_SELECTION,
        timeout_seconds: int = 30
    ) -> InteractiveSession:
        """Create a new interactive session."""
        key = (platform, user_id)
        
        # Cancel existing session if any
        if key in self._sessions:
            self._sessions[key].state = SessionState.CANCELLED
        
        session = InteractiveSession(
            session_id=f"{platform}_{user_id}_{int(time.time())}",
            platform=platform,
            user_id=user_id,
            state=initial_state,
            timeout_seconds=timeout_seconds
        )
        
        self._sessions[key] = session
        
        # Start cleanup task if not running
        if not self._running:
            self.start_cleanup_task()
        
        logger.debug(f"Created session {key} in state {initial_state}")
        return session
    
    def get_session(self, platform: str, user_id: str) -> Optional[InteractiveSession]:
        """Get existing session for user."""
        key = (platform, user_id)
        session = self._sessions.get(key)
        
        if session and session.is_expired():
            session.state = SessionState.TIMEOUT
            del self._sessions[key]
            return None
        
        return session
    
    def update_session(
        self,
        platform: str,
        user_id: str,
        state: Optional[SessionState] = None,
        selected_character: Optional[str] = None,
        timeout_seconds: Optional[int] = None
    ) -> Optional[InteractiveSession]:
        """Update existing session."""
        key = (platform, user_id)
        session = self._sessions.get(key)
        
        if not session or session.is_expired():
            return None
        
        if state:
            session.state = state
        if selected_character:
            session.selected_character = selected_character
        if timeout_seconds:
            session.timeout_seconds = timeout_seconds
            
        session.update_activity()
        return session
    
    def cancel_session(self, platform: str, user_id: str) -> bool:
        """Cancel existing session."""
        key = (platform, user_id)
        session = self._sessions.get(key)
        
        if session:
            session.state = SessionState.CANCELLED
            del self._sessions[key]
            logger.debug(f"Cancelled session {key}")
            return True
        
        return False
    
    def get_all_sessions(self) -> Dict[Tuple[str, str], InteractiveSession]:
        """Get all active sessions (for debugging)."""
        return {
            key: session for key, session in self._sessions.items()
            if not session.is_expired()
        }


# Global session manager instance
session_manager = SessionManager()