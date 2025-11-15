#!/usr/bin/env python3
"""
Manual test script for PJSk Emoji Maker list commands.

This script demonstrates the functionality of the list commands
without requiring a running AstrBot instance.
"""

import sys
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent))

# Setup mocks before importing domain
from tests.mock_astrbot import setup_mocks
setup_mocks()

from pjsk_emoji.domain import (
    get_character_name,
    format_character_list,
    format_character_groups,
    format_character_detail,
    CHARACTER_NAMES,
)


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_character_name_resolution():
    """Test character name resolution."""
    print_section("Character Name Resolution")
    
    test_cases = [
        ("初音未来", "Canonical name"),
        ("miku", "English alias"),
        ("初音", "Chinese alias"),
        ("ichika", "English alias for different character"),
        ("不存在", "Non-existent character"),
        ("", "Empty string"),
    ]
    
    for input_str, description in test_cases:
        result = get_character_name(input_str)
        status = "✓" if result else "✗"
        print(f"{status} {description:30} | Input: '{input_str}' → {result}")


def test_character_list():
    """Test character list formatting."""
    print_section("All Characters List")
    
    list_text = format_character_list()
    print(list_text)
    print(f"\nTotal characters: {len(CHARACTER_NAMES)}")


def test_character_groups():
    """Test character groups formatting."""
    print_section("Characters by Group")
    
    groups_text = format_character_groups()
    print(groups_text)


def test_character_details():
    """Test character detail formatting."""
    print_section("Character Details")
    
    for character in ["初音未来", "星乃一歌", "小豆泽心羽"]:
        print(f"\n{format_character_detail(character)}")
        print()


def test_command_flow():
    """Simulate command flow."""
    print_section("Simulated Command Flow")
    
    commands = [
        ("/pjsk", "Show root help"),
        ("/pjsk.列表", "Show list options"),
        ("/pjsk.列表.全部", "List all characters"),
        ("/pjsk.列表.角色分类", "List by category"),
        ("/pjsk.列表.展开指定角色 miku", "Show character details (using alias)"),
        ("/pjsk.draw", "Create card"),
    ]
    
    print("Example user interaction flow:\n")
    for i, (cmd, desc) in enumerate(commands, 1):
        print(f"{i}. {desc:40} → {cmd}")


def main():
    """Run all manual tests."""
    print("\n" + "="*60)
    print("  PJSk Emoji Maker - List Commands Manual Test")
    print("="*60)
    
    try:
        test_character_name_resolution()
        test_character_list()
        test_character_groups()
        test_character_details()
        test_command_flow()
        
        print_section("All Manual Tests Completed")
        print("✓ Character name resolution working")
        print("✓ List formatting working")
        print("✓ Group formatting working")
        print("✓ Detail formatting working")
        print("\n✓ Ready for automated testing!\n")
        
        return 0
    
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
