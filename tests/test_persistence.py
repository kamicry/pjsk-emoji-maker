"""Tests for state persistence."""

import pytest
import tempfile
import os
import time
from unittest.mock import patch
from persistence import StatePersistence
from models import RenderState


class TestStatePersistence:
    """Tests for state persistence functionality."""

    @pytest.fixture
    def temp_storage_file(self):
        """Create a temporary storage file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        yield temp_path
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    @pytest.fixture
    def persistence(self, temp_storage_file):
        """Create a StatePersistence instance with temporary file."""
        return StatePersistence(temp_storage_file)

    @pytest.fixture
    def sample_state(self):
        """Create a sample RenderState for testing."""
        return RenderState(
            text="Test text",
            font_size=42,
            line_spacing=1.2,
            curve_enabled=True,
            offset_x=10,
            offset_y=-5,
            role="初音未来"
        )

    def test_storage_directory_creation(self, temp_storage_file):
        """Test that storage directory is created."""
        dir_path = os.path.dirname(temp_storage_file)
        if os.path.exists(dir_path):
            os.rmdir(dir_path)
        
        assert not os.path.exists(dir_path)
        
        persistence = StatePersistence(temp_storage_file)
        
        # Directory should be created
        assert os.path.exists(dir_path)

    def test_save_and_get_state(self, persistence, sample_state):
        """Test saving and retrieving state."""
        platform = "test_platform"
        session_id = "test_session"
        
        # Save state
        persistence.set_state(platform, session_id, sample_state)
        
        # Retrieve state
        retrieved_state = persistence.get_state(platform, session_id)
        
        assert retrieved_state is not None
        assert retrieved_state.text == sample_state.text
        assert retrieved_state.font_size == sample_state.font_size
        assert retrieved_state.line_spacing == sample_state.line_spacing
        assert retrieved_state.curve_enabled == sample_state.curve_enabled
        assert retrieved_state.offset_x == sample_state.offset_x
        assert retrieved_state.offset_y == sample_state.offset_y
        assert retrieved_state.role == sample_state.role

    def test_get_nonexistent_state(self, persistence):
        """Test retrieving non-existent state."""
        state = persistence.get_state("nonexistent", "session")
        assert state is None

    def test_delete_state(self, persistence, sample_state):
        """Test deleting state."""
        platform = "test_platform"
        session_id = "test_session"
        
        # Save state first
        persistence.set_state(platform, session_id, sample_state)
        assert persistence.get_state(platform, session_id) is not None
        
        # Delete state
        result = persistence.delete_state(platform, session_id)
        assert result is True
        
        # State should be gone
        assert persistence.get_state(platform, session_id) is None

    def test_delete_nonexistent_state(self, persistence):
        """Test deleting non-existent state."""
        result = persistence.delete_state("nonexistent", "session")
        assert result is False

    def test_state_expiration(self, persistence, sample_state):
        """Test that states expire after TTL."""
        platform = "test_platform"
        session_id = "test_session"
        ttl_hours = 1
        
        # Save state
        persistence.set_state(platform, session_id, sample_state)
        
        # Should be retrievable immediately
        state = persistence.get_state(platform, session_id, ttl_hours)
        assert state is not None
        
        # Mock time to simulate expiration
        with patch('time.time') as mock_time:
            # First call returns current time
            # Second call returns time 2 hours later (past TTL)
            mock_time.side_effect = [time.time(), time.time() + (2 * 3600)]
            
            # State should be expired
            expired_state = persistence.get_state(platform, session_id, ttl_hours)
            assert expired_state is None

    def test_cleanup_expired_states(self, persistence, sample_state):
        """Test cleanup of expired states."""
        ttl_hours = 1
        
        # Save multiple states
        persistence.set_state("platform1", "session1", sample_state)
        persistence.set_state("platform2", "session2", sample_state)
        persistence.set_state("platform3", "session3", sample_state)
        
        # Mock time to simulate expiration
        with patch('time.time') as mock_time:
            # First calls for saving, second call for cleanup (2 hours later)
            mock_time.side_effect = [
                time.time(), time.time(), time.time(),  # Save times
                time.time() + (2 * 3600)  # Cleanup time
            ]
            
            # Run cleanup
            removed_count = persistence.cleanup_expired(ttl_hours)
            
            # Should have removed all 3 states
            assert removed_count == 3
            
            # All states should be gone
            assert persistence.get_state("platform1", "session1", ttl_hours) is None
            assert persistence.get_state("platform2", "session2", ttl_hours) is None
            assert persistence.get_state("platform3", "session3", ttl_hours) is None

    def test_get_all_states(self, persistence, sample_state):
        """Test retrieving all states."""
        # Save multiple states
        persistence.set_state("platform1", "session1", sample_state)
        persistence.set_state("platform2", "session2", sample_state)
        
        # Modify second state
        sample_state2 = RenderState(
            text="Different text",
            font_size=36,
            line_spacing=1.5,
            curve_enabled=False,
            offset_x=0,
            offset_y=0,
            role="星乃一歌"
        )
        persistence.set_state("platform2", "session2", sample_state2)
        
        # Get all states
        all_states = persistence.get_all_states()
        
        assert len(all_states) == 2
        assert "platform1:session1" in all_states
        assert "platform2:session2" in all_states
        
        state1 = all_states["platform1:session1"]
        assert state1.text == "Test text"
        
        state2 = all_states["platform2:session2"]
        assert state2.text == "Different text"

    def test_handle_corrupted_storage_file(self, temp_storage_file):
        """Test handling of corrupted storage file."""
        # Write invalid JSON
        with open(temp_storage_file, 'w') as f:
            f.write("invalid json content")
        
        persistence = StatePersistence(temp_storage_file)
        
        # Should handle gracefully and return empty results
        state = persistence.get_state("platform", "session")
        assert state is None
        
        all_states = persistence.get_all_states()
        assert all_states == {}

    def test_multiple_platforms_and_sessions(self, persistence, sample_state):
        """Test handling multiple platforms and sessions."""
        # Save states for different platforms and sessions
        platforms_sessions = [
            ("discord", "user123"),
            ("telegram", "user456"),
            ("discord", "user789"),
            ("qq", "user101")
        ]
        
        for platform, session in platforms_sessions:
            # Modify state for each
            state = RenderState(
                text=f"Text for {platform}:{session}",
                font_size=42,
                line_spacing=1.2,
                curve_enabled=False,
                offset_x=0,
                offset_y=0,
                role="初音未来"
            )
            persistence.set_state(platform, session, state)
        
        # Verify all states can be retrieved
        for platform, session in platforms_sessions:
            state = persistence.get_state(platform, session)
            assert state is not None
            assert state.text == f"Text for {platform}:{session}"

    def test_state_persistence_across_instances(self, temp_storage_file, sample_state):
        """Test that states persist across different persistence instances."""
        platform = "test_platform"
        session_id = "test_session"
        
        # Save with first instance
        persistence1 = StatePersistence(temp_storage_file)
        persistence1.set_state(platform, session_id, sample_state)
        
        # Create new instance and retrieve
        persistence2 = StatePersistence(temp_storage_file)
        retrieved_state = persistence2.get_state(platform, session_id)
        
        assert retrieved_state is not None
        assert retrieved_state.text == sample_state.text
        assert retrieved_state.font_size == sample_state.font_size

    def test_make_key_format(self, persistence):
        """Test internal key format."""
        # Test the private method
        key = persistence._make_key("test_platform", "test_session")
        assert key == "test_platform:test_session"