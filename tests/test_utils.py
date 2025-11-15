"""Tests for utility functions."""

import pytest
from utils import (
    calculateOffsets,
    calculateFontSize,
    findLongestLine,
    calculateTextDimensions,
    sanitizeText,
    validateCurveIntensity,
    parseKoishiFlags,
    applyDefaults,
)


class TestCalculateOffsets:
    """Tests for calculateOffsets function."""

    def test_basic_offsets(self):
        """Test basic offset calculation."""
        text = "Hello World"
        font_size = 42
        line_spacing = 1.2
        
        offset_x, offset_y = calculateOffsets(text, font_size, line_spacing)
        
        assert isinstance(offset_x, int)
        assert isinstance(offset_y, int)
        assert -240 <= offset_x <= 240
        assert -240 <= offset_y <= 240

    def test_empty_text(self):
        """Test offset calculation with empty text."""
        text = ""
        font_size = 42
        line_spacing = 1.2
        
        offset_x, offset_y = calculateOffsets(text, font_size, line_spacing)
        
        assert isinstance(offset_x, int)
        assert isinstance(offset_y, int)

    def test_multiline_text(self):
        """Test offset calculation with multiline text."""
        text = "Line 1\nLine 2\nLine 3"
        font_size = 42
        line_spacing = 1.2
        
        offset_x, offset_y = calculateOffsets(text, font_size, line_spacing)
        
        # Y offset should account for multiple lines
        assert isinstance(offset_y, int)
        # Should be different from single line
        single_line_y = calculateOffsets("Single line", font_size, line_spacing)[1]
        assert offset_y != single_line_y or abs(offset_y) < abs(single_line_y)

    def test_different_font_sizes(self):
        """Test offset calculation with different font sizes."""
        text = "Test text"
        line_spacing = 1.2
        
        small_offsets = calculateOffsets(text, 18, line_spacing)
        large_offsets = calculateOffsets(text, 84, line_spacing)
        
        # Offsets should scale with font size
        assert isinstance(small_offsets[0], int)
        assert isinstance(large_offsets[0], int)

    def test_different_line_spacing(self):
        """Test offset calculation with different line spacing."""
        text = "Line 1\nLine 2"
        font_size = 42
        
        tight_spacing = calculateOffsets(text, font_size, 0.6)
        loose_spacing = calculateOffsets(text, font_size, 3.0)
        
        assert isinstance(tight_spacing[1], int)
        assert isinstance(loose_spacing[1], int)

    def test_offset_bounds(self):
        """Test that offsets stay within bounds."""
        # Extreme cases that might push offsets out of bounds
        very_long_text = "A" * 1000
        many_lines = "\n".join(["Line"] * 50)
        
        for text in [very_long_text, many_lines]:
            for font_size in [18, 42, 84]:
                for line_spacing in [0.6, 1.2, 3.0]:
                    offset_x, offset_y = calculateOffsets(text, font_size, line_spacing)
                    assert -240 <= offset_x <= 240
                    assert -240 <= offset_y <= 240


class TestCalculateFontSize:
    """Tests for calculateFontSize function."""

    def test_short_text_gets_max_size(self):
        """Test that short text gets maximum font size."""
        short_text = "Hi"
        font_size = calculateFontSize(short_text, target_width=400, min_size=18, max_size=84)
        assert font_size == 84

    def test_long_text_gets_reduced_size(self):
        """Test that long text gets reduced font size."""
        long_text = "This is a very long text that should require a smaller font size to fit within the target width"
        font_size = calculateFontSize(long_text, target_width=400, min_size=18, max_size=84)
        assert 18 <= font_size <= 84
        assert font_size < 84  # Should be smaller than max

    def test_empty_text_gets_max_size(self):
        """Test that empty text gets maximum font size."""
        font_size = calculateFontSize("", target_width=400, min_size=18, max_size=84)
        assert font_size == 84

    def test_different_target_widths(self):
        """Test with different target widths."""
        text = "This is a moderately long text"
        
        narrow_width = calculateFontSize(text, target_width=200, min_size=18, max_size=84)
        wide_width = calculateFontSize(text, target_width=800, min_size=18, max_size=84)
        
        # Narrow width should give smaller font
        assert narrow_width <= wide_width

    def test_different_size_ranges(self):
        """Test with different min/max size ranges."""
        text = "Test text"
        
        small_range = calculateFontSize(text, target_width=400, min_size=10, max_size=30)
        large_range = calculateFontSize(text, target_width=400, min_size=20, max_size=100)
        
        assert 10 <= small_range <= 30
        assert 20 <= large_range <= 100

    def test_very_long_text_hits_minimum(self):
        """Test that very long text hits minimum size."""
        extremely_long = "A" * 1000
        font_size = calculateFontSize(extremely_long, target_width=100, min_size=18, max_size=84)
        assert font_size == 18  # Should hit minimum


class TestFindLongestLine:
    """Tests for findLongestLine function."""

    def test_single_line(self):
        """Test with single line text."""
        text = "Hello World"
        result = findLongestLine(text)
        assert result == "Hello World"

    def test_multiple_lines(self):
        """Test with multiple lines."""
        text = "Short\nThis is the longest line\nMedium"
        result = findLongestLine(text)
        assert result == "This is the longest line"

    def test_empty_text(self):
        """Test with empty text."""
        result = findLongestLine("")
        assert result == ""

    def test_tie_breaker(self):
        """Test behavior when lines have same length."""
        text = "Line A\nLine B\nLine C"
        result = findLongestLine(text)
        # Should return one of the lines (all same length)
        assert result in ["Line A", "Line B", "Line C"]

    def test_with_empty_lines(self):
        """Test with empty lines."""
        text = "First line\n\nThird line\n"
        result = findLongestLine(text)
        # Both "First line" and "Third line" have same length, first should be returned
        assert result in ["First line", "Third line"]

    def test_unicode_characters(self):
        """Test with unicode characters."""
        text = "Short\n这是一个很长的中文行\nMedium"
        result = findLongestLine(text)
        assert result == "这是一个很长的中文行"


class TestCalculateTextDimensions:
    """Tests for calculateTextDimensions function."""

    def test_basic_dimensions(self):
        """Test basic dimension calculation."""
        text = "Hello World"
        font_size = 42
        line_spacing = 1.2
        
        width, height = calculateTextDimensions(text, font_size, line_spacing)
        
        assert isinstance(width, int)
        assert isinstance(height, int)
        assert width > 0
        assert height > 0

    def test_empty_text(self):
        """Test dimension calculation with empty text."""
        width, height = calculateTextDimensions("", 42, 1.2)
        assert width == 0
        assert height == 0

    def test_multiline_text(self):
        """Test dimension calculation with multiline text."""
        single_line = "Single line"
        multiline = "Line 1\nLine 2\nLine 3"
        
        single_width, single_height = calculateTextDimensions(single_line, 42, 1.2)
        multi_width, multi_height = calculateTextDimensions(multiline, 42, 1.2)
        
        # Multiline should be taller
        assert multi_height > single_height
        # Width might be similar or different depending on line lengths
        assert isinstance(multi_width, int)

    def test_different_font_sizes(self):
        """Test dimensions with different font sizes."""
        text = "Test text"
        
        small_font = calculateTextDimensions(text, 18, 1.2)
        large_font = calculateTextDimensions(text, 84, 1.2)
        
        # Larger font should give larger dimensions
        assert large_font[0] > small_font[0]  # width
        assert large_font[1] > small_font[1]  # height

    def test_different_line_spacing(self):
        """Test dimensions with different line spacing."""
        text = "Line 1\nLine 2"
        
        tight_spacing = calculateTextDimensions(text, 42, 0.6)
        loose_spacing = calculateTextDimensions(text, 42, 3.0)
        
        # Width should be similar (same longest line)
        assert abs(tight_spacing[0] - loose_spacing[0]) <= 1
        # Height should be different
        assert loose_spacing[1] > tight_spacing[1]


class TestSanitizeText:
    """Tests for sanitizeText function."""

    def test_normal_text(self):
        """Test with normal text."""
        text = "Hello World"
        result = sanitizeText(text)
        assert result == "Hello World"

    def test_excessive_whitespace(self):
        """Test removal of excessive whitespace."""
        text = "Hello    World\n\n\nTest"
        result = sanitizeText(text)
        assert result == "Hello World Test"

    def test_leading_trailing_whitespace(self):
        """Test removal of leading and trailing whitespace."""
        text = "   Hello World   "
        result = sanitizeText(text)
        assert result == "Hello World"

    def test_empty_text(self):
        """Test with empty text."""
        result = sanitizeText("")
        assert result == ""

    def test_long_text_truncation(self):
        """Test truncation of long text."""
        text = "A" * 150
        result = sanitizeText(text, max_length=100)
        assert len(result) <= 100
        assert result.endswith("...")

    def test_custom_max_length(self):
        """Test with custom max length."""
        text = "Hello World"
        result = sanitizeText(text, max_length=5)
        assert len(result) <= 5
        assert result.endswith("...")

    def test_unicode_handling(self):
        """Test handling of unicode characters."""
        text = "Hello 世界 🌍"
        result = sanitizeText(text)
        assert result == "Hello 世界 🌍"


class TestValidateCurveIntensity:
    """Tests for validateCurveIntensity function."""

    def test_valid_range(self):
        """Test with valid range values."""
        for value in [0.0, 0.5, 1.0]:
            result = validateCurveIntensity(value)
            assert result == value

    def test_below_minimum(self):
        """Test values below minimum."""
        result = validateCurveIntensity(-0.5)
        assert result == 0.0

    def test_above_maximum(self):
        """Test values above maximum."""
        result = validateCurveIntensity(1.5)
        assert result == 1.0

    def test_edge_cases(self):
        """Test edge cases."""
        assert validateCurveIntensity(0.0) == 0.0
        assert validateCurveIntensity(1.0) == 1.0
        assert validateCurveIntensity(-1.0) == 0.0
        assert validateCurveIntensity(2.0) == 1.0


class TestApplyDefaults:
    """Tests for applyDefaults function."""

    def test_apply_all_defaults(self):
        """Test applying all default values."""
        options = {}
        defaults = {
            'text': 'default text',
            'font_size': 42,
            'curve': False
        }
        
        result = applyDefaults(options, defaults)
        assert result == defaults

    def test_override_defaults(self):
        """Test overriding default values."""
        options = {
            'text': 'custom text',
            'font_size': 48
        }
        defaults = {
            'text': 'default text',
            'font_size': 42,
            'curve': False
        }
        
        result = applyDefaults(options, defaults)
        assert result['text'] == 'custom text'
        assert result['font_size'] == 48
        assert result['curve'] is False  # Should keep default

    def test_partial_override(self):
        """Test partial override of defaults."""
        options = {'text': 'custom'}
        defaults = {
            'text': 'default',
            'font_size': 42,
            'curve': False,
            'offset_x': 0
        }
        
        result = applyDefaults(options, defaults)
        assert result['text'] == 'custom'
        assert result['font_size'] == 42
        assert result['curve'] is False
        assert result['offset_x'] == 0

    def test_none_values(self):
        """Test handling of None values."""
        options = {
            'text': None,
            'font_size': 48
        }
        defaults = {
            'text': 'default text',
            'font_size': 42
        }
        
        result = applyDefaults(options, defaults)
        # None should override default
        assert result['text'] is None
        assert result['font_size'] == 48

    def test_empty_options(self):
        """Test with empty options dict."""
        options = {}
        defaults = {'text': 'default', 'font_size': 42}
        
        result = applyDefaults(options, defaults)
        assert result == defaults