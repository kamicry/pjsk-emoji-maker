"""Tests for the mock renderer."""

import pytest
from unittest.mock import patch
from pjsk_emoji.mock_renderer import MockRenderer


class TestMockRenderer:
    """Tests for MockRenderer class."""

    @pytest.fixture
    def renderer(self):
        """Create a MockRenderer instance."""
        return MockRenderer()

    def test_renderer_initialization(self, renderer):
        """Test renderer initialization."""
        assert renderer.render_count == 0
        info = renderer.get_render_info()
        assert info['renders_completed'] == 0
        assert info['renderer_type'] == 'mock'
        assert 'PNG' in info['supported_formats']

    def test_basic_render(self, renderer):
        """Test basic card rendering."""
        image_bytes = renderer.render_card(
            text="Hello World",
            font_size=42,
            line_spacing=1.2,
            curve_enabled=False,
            offset_x=0,
            offset_y=0,
            role="初音未来"
        )
        
        assert isinstance(image_bytes, bytes)
        assert len(image_bytes) > 0
        assert renderer.render_count == 1

    def test_render_with_curve(self, renderer):
        """Test rendering with curve effect."""
        image_bytes = renderer.render_card(
            text="Curved Text",
            font_size=36,
            line_spacing=1.5,
            curve_enabled=True,
            offset_x=10,
            offset_y=-5,
            role="星乃一歌",
            curve_intensity=0.8
        )
        
        assert isinstance(image_bytes, bytes)
        assert len(image_bytes) > 0
        assert renderer.render_count == 1

    def test_render_multiline_text(self, renderer):
        """Test rendering with multiline text."""
        multiline_text = "Line 1\nLine 2\nLine 3"
        image_bytes = renderer.render_card(
            text=multiline_text,
            font_size=30,
            line_spacing=1.8,
            curve_enabled=False,
            offset_x=0,
            offset_y=0,
            role="Test Role"
        )
        
        assert isinstance(image_bytes, bytes)
        assert len(image_bytes) > 0

    def test_render_empty_text(self, renderer):
        """Test rendering with empty text."""
        image_bytes = renderer.render_card(
            text="",
            font_size=42,
            line_spacing=1.2,
            curve_enabled=False,
            offset_x=0,
            offset_y=0,
            role="初音未来"
        )
        
        assert isinstance(image_bytes, bytes)
        assert len(image_bytes) > 0

    def test_render_with_shadow_disabled(self, renderer):
        """Test rendering with text shadow disabled."""
        image_bytes = renderer.render_card(
            text="No Shadow",
            font_size=42,
            line_spacing=1.2,
            curve_enabled=False,
            offset_x=0,
            offset_y=0,
            role="Test",
            enable_shadow=False
        )
        
        assert isinstance(image_bytes, bytes)
        assert len(image_bytes) > 0

    def test_render_different_emoji_sets(self, renderer):
        """Test rendering with different emoji sets."""
        for emoji_set in ["apple", "google", "twitter", "facebook"]:
            image_bytes = renderer.render_card(
                text=f"Test with {emoji_set}",
                font_size=42,
                line_spacing=1.2,
                curve_enabled=False,
                offset_x=0,
                offset_y=0,
                role="Test",
                emoji_set=emoji_set
            )
            
            assert isinstance(image_bytes, bytes)
            assert len(image_bytes) > 0

    def test_render_extreme_offsets(self, renderer):
        """Test rendering with extreme offset values."""
        image_bytes = renderer.render_card(
            text="Offset Test",
            font_size=42,
            line_spacing=1.2,
            curve_enabled=False,
            offset_x=240,  # Maximum
            offset_y=-240,  # Minimum
            role="Test"
        )
        
        assert isinstance(image_bytes, bytes)
        assert len(image_bytes) > 0

    def test_render_extreme_font_sizes(self, renderer):
        """Test rendering with extreme font sizes."""
        # Minimum font size
        small_image = renderer.render_card(
            text="Small",
            font_size=18,
            line_spacing=1.2,
            curve_enabled=False,
            offset_x=0,
            offset_y=0,
            role="Test"
        )
        
        # Maximum font size
        large_image = renderer.render_card(
            text="Large",
            font_size=84,
            line_spacing=1.2,
            curve_enabled=False,
            offset_x=0,
            offset_y=0,
            role="Test"
        )
        
        assert isinstance(small_image, bytes)
        assert isinstance(large_image, bytes)
        assert len(small_image) > 0
        assert len(large_image) > 0

    def test_render_extreme_line_spacing(self, renderer):
        """Test rendering with extreme line spacing values."""
        # Minimum line spacing
        tight_image = renderer.render_card(
            text="Tight\nSpacing",
            font_size=42,
            line_spacing=0.6,
            curve_enabled=False,
            offset_x=0,
            offset_y=0,
            role="Test"
        )
        
        # Maximum line spacing
        loose_image = renderer.render_card(
            text="Loose\nSpacing",
            font_size=42,
            line_spacing=3.0,
            curve_enabled=False,
            offset_x=0,
            offset_y=0,
            role="Test"
        )
        
        assert isinstance(tight_image, bytes)
        assert isinstance(loose_image, bytes)
        assert len(tight_image) > 0
        assert len(loose_image) > 0

    def test_render_curve_intensity_values(self, renderer):
        """Test rendering with different curve intensity values."""
        for intensity in [0.0, 0.25, 0.5, 0.75, 1.0]:
            image_bytes = renderer.render_card(
                text=f"Curve {intensity}",
                font_size=42,
                line_spacing=1.2,
                curve_enabled=True,
                offset_x=0,
                offset_y=0,
                role="Test",
                curve_intensity=intensity
            )
            
            assert isinstance(image_bytes, bytes)
            assert len(image_bytes) > 0

    def test_multiple_renders(self, renderer):
        """Test multiple renders increment counter."""
        for i in range(5):
            image_bytes = renderer.render_card(
                text=f"Render {i+1}",
                font_size=42,
                line_spacing=1.2,
                curve_enabled=False,
                offset_x=0,
                offset_y=0,
                role="Test"
            )
            
            assert isinstance(image_bytes, bytes)
            assert len(image_bytes) > 0
            assert renderer.render_count == i + 1

    def test_render_info_updates(self, renderer):
        """Test that render info updates after renders."""
        initial_info = renderer.get_render_info()
        assert initial_info['renders_completed'] == 0
        
        # Perform some renders
        renderer.render_card("Test 1", 42, 1.2, False, 0, 0, "Test")
        renderer.render_card("Test 2", 36, 1.5, True, 10, -5, "Test")
        
        updated_info = renderer.get_render_info()
        assert updated_info['renders_completed'] == 2
        assert updated_info['renderer_type'] == 'mock'

    def test_render_with_unicode_text(self, renderer):
        """Test rendering with unicode text."""
        unicode_text = "Hello 世界 🌍 Test\n中文测试"
        image_bytes = renderer.render_card(
            text=unicode_text,
            font_size=42,
            line_spacing=1.2,
            curve_enabled=False,
            offset_x=0,
            offset_y=0,
            role="Test"
        )
        
        assert isinstance(image_bytes, bytes)
        assert len(image_bytes) > 0

    def test_render_with_special_characters(self, renderer):
        """Test rendering with special characters."""
        special_text = "Special: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        image_bytes = renderer.render_card(
            text=special_text,
            font_size=42,
            line_spacing=1.2,
            curve_enabled=False,
            offset_x=0,
            offset_y=0,
            role="Test"
        )
        
        assert isinstance(image_bytes, bytes)
        assert len(image_bytes) > 0

    def test_render_image_format(self, renderer):
        """Test that rendered image is in valid format."""
        image_bytes = renderer.render_card(
            text="Format Test",
            font_size=42,
            line_spacing=1.2,
            curve_enabled=False,
            offset_x=0,
            offset_y=0,
            role="Test"
        )
        
        # Check if it's a valid PNG by trying to open it
        try:
            from PIL import Image
            import io
            
            img = Image.open(io.BytesIO(image_bytes))
            assert img.format == 'PNG'
            assert img.size == (800, 600)  # Default size from mock renderer
        except ImportError:
            # If PIL is not available, just check that we got some bytes
            assert len(image_bytes) > 0

    def test_render_consistency(self, renderer):
        """Test that same parameters produce consistent results."""
        params = {
            'text': 'Consistency Test',
            'font_size': 42,
            'line_spacing': 1.2,
            'curve_enabled': False,
            'offset_x': 0,
            'offset_y': 0,
            'role': 'Test'
        }
        
        # Render twice with same parameters
        image1 = renderer.render_card(**params)
        image2 = renderer.render_card(**params)
        
        # Results should be identical (in mock renderer)
        assert image1 == image2

    @patch('time.strftime')
    def test_render_with_mocked_time(self, mock_strftime, renderer):
        """Test rendering with mocked time for consistent metadata."""
        mock_strftime.return_value = "2023-01-01 00:00:00"
        
        image_bytes = renderer.render_card(
            text="Time Test",
            font_size=42,
            line_spacing=1.2,
            curve_enabled=False,
            offset_x=0,
            offset_y=0,
            role="Test"
        )
        
        assert isinstance(image_bytes, bytes)
        assert len(image_bytes) > 0
        mock_strftime.assert_called_once_with("%Y-%m-%d %H:%M:%S")