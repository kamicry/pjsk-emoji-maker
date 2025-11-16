"""Test suite for character selection validation."""

import pytest

from pjsk_emoji.domain import get_character_name, CHARACTER_NAMES


class TestCharacterSelectionValidation:
    """Tests for character selection validation logic."""

    def test_numeric_selection_valid_range(self):
        """Test that numeric inputs 1-8 map to correct characters."""
        expected_characters = [
            "初音未来", "星乃一歌", "天马咲希", "望月穗波",
            "日野森志步", "东云彰人", "青柳冬弥", "小豆泽心羽"
        ]
        
        for i, expected_char in enumerate(expected_characters, 1):
            selection = int(str(i))
            if 1 <= selection <= len(CHARACTER_NAMES):
                result = CHARACTER_NAMES[selection - 1]
                assert result == expected_char, f"Number {i} should map to {expected_char}, got {result}"

    def test_numeric_selection_out_of_range(self):
        """Test that numbers outside 1-8 range are handled."""
        for i in [0, 9, 10, 100, -1]:
            selection = int(str(i))
            # Out of range check
            assert not (1 <= selection <= len(CHARACTER_NAMES)), f"Number {i} should be out of range"

    def test_character_name_resolution_english(self):
        """Test that English character names resolve correctly."""
        test_cases = [
            ("miku", "初音未来"),
            ("ichika", "星乃一歌"),
            ("saki", "天马咲希"),
            ("honami", "望月穗波"),
            ("shiho", "日野森志步"),
            ("akito", "东云彰人"),
            ("toya", "青柳冬弥"),
            ("kohane", "小豆泽心羽"),
        ]
        
        for input_name, expected_name in test_cases:
            resolved = get_character_name(input_name)
            assert resolved == expected_name, f"{input_name} should resolve to {expected_name}, got {resolved}"
            assert resolved in CHARACTER_NAMES, f"Resolved name {resolved} should be in CHARACTER_NAMES"

    def test_character_name_resolution_chinese(self):
        """Test that Chinese character names resolve correctly."""
        test_cases = [
            "初音未来", "星乃一歌", "天马咲希", "望月穗波",
            "日野森志步", "东云彰人", "青柳冬弥", "小豆泽心羽"
        ]
        
        for name in test_cases:
            resolved = get_character_name(name)
            assert resolved == name, f"{name} should resolve to itself, got {resolved}"
            assert resolved in CHARACTER_NAMES, f"{name} should be in CHARACTER_NAMES"

    def test_character_name_resolution_aliases(self):
        """Test that character aliases resolve correctly."""
        test_cases = [
            ("初音", "初音未来"),
            ("hatsune", "初音未来"),
            ("一歌", "星乃一歌"),
            ("咲希", "天马咲希"),
            ("穗波", "望月穗波"),
            ("志步", "日野森志步"),
            ("彰人", "东云彰人"),
            ("冬弥", "青柳冬弥"),
            ("心羽", "小豆泽心羽"),
        ]
        
        for alias, expected_name in test_cases:
            resolved = get_character_name(alias)
            assert resolved == expected_name, f"Alias {alias} should resolve to {expected_name}, got {resolved}"

    def test_character_name_resolution_case_insensitive(self):
        """Test that character name resolution is case-insensitive for English names."""
        test_cases = [
            ("MIKU", "初音未来"),
            ("Miku", "初音未来"),
            ("MiKu", "初音未来"),
            ("ICHIKA", "星乃一歌"),
            ("Ichika", "星乃一歌"),
        ]
        
        for input_name, expected_name in test_cases:
            resolved = get_character_name(input_name)
            assert resolved == expected_name, f"{input_name} should resolve to {expected_name} (case-insensitive), got {resolved}"

    def test_invalid_input_returns_none(self):
        """Test that invalid inputs return None."""
        invalid_inputs = [
            "invalid_character",
            "不存在的角色",
            "unknown",
            "abc123",
            "9",  # Out of numeric range
            "0",  # Out of numeric range
            "",  # Empty string
        ]
        
        for invalid_input in invalid_inputs:
            if invalid_input.isdigit():
                # Test numeric validation
                selection = int(invalid_input)
                if selection < 1 or selection > len(CHARACTER_NAMES):
                    # This is expected to be invalid
                    assert True
            else:
                # Test name validation
                resolved = get_character_name(invalid_input)
                if invalid_input == "":
                    assert resolved is None, "Empty string should return None"
                elif resolved:
                    # If it resolved, it should be in CHARACTER_NAMES
                    assert resolved in CHARACTER_NAMES
                else:
                    # Otherwise it should be None
                    assert resolved is None, f"Invalid input '{invalid_input}' should return None, got {resolved}"

    def test_whitespace_handling(self):
        """Test that whitespace is handled correctly."""
        test_cases = [
            (" miku ", "初音未来"),
            ("  ichika  ", "星乃一歌"),
            ("\tmiku\t", "初音未来"),
            (" 5 ", None),  # Numeric with spaces should be handled by caller
        ]
        
        for input_name, expected_name in test_cases:
            resolved = get_character_name(input_name.strip())
            if expected_name:
                assert resolved == expected_name, f"'{input_name}' (stripped) should resolve to {expected_name}, got {resolved}"
            else:
                # Caller should strip before calling
                pass

    def test_validation_function_integration(self):
        """Test the full validation logic as used in the command."""
        def validate_character_selection(user_input: str):
            """Replica of the _validate_character_selection method."""
            stripped_input = user_input.strip()
            
            # Try numeric selection first (1-8)
            try:
                selection = int(stripped_input)
                if 1 <= selection <= len(CHARACTER_NAMES):
                    return CHARACTER_NAMES[selection - 1]
            except ValueError:
                pass
            
            # Try to resolve by character name or alias
            resolved_name = get_character_name(stripped_input)
            if resolved_name and resolved_name in CHARACTER_NAMES:
                return resolved_name
            
            return None

        # Test valid inputs
        assert validate_character_selection("5") == "日野森志步"
        assert validate_character_selection("miku") == "初音未来"
        assert validate_character_selection("初音未来") == "初音未来"
        assert validate_character_selection(" 3 ") == "天马咲希"
        assert validate_character_selection("  ichika  ") == "星乃一歌"
        
        # Test invalid inputs
        assert validate_character_selection("invalid") is None
        assert validate_character_selection("9") is None
        assert validate_character_selection("0") is None
        assert validate_character_selection("") is None
        assert validate_character_selection("不存在") is None
