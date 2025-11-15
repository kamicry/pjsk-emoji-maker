#!/usr/bin/env python3
"""
Smoke test for the PJSK renderer.

This script tests the renderer functionality and generates sample output
for manual verification.
"""

import asyncio
import io
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from pjsk_emoji.renderer import PJSKRenderer
from pjsk_emoji.domain import CHARACTERS


async def test_emoji_card_renderer(renderer: PJSKRenderer) -> bool:
    """Test emoji card rendering."""
    print("Testing emoji card rendering...")
    
    try:
        # Test basic card
        image_bytes = await renderer.render_emoji_card(
            text="Hello World!\n这是一个测试",
            character_name="初音未来",
            font_size=42,
            line_spacing=1.2,
            curve_enabled=False,
            offset_x=0,
            offset_y=0,
            enable_shadow=True,
            emoji_set="apple"
        )
        
        # Verify we got some bytes
        assert len(image_bytes) > 0, "No image bytes generated"
        assert image_bytes[:8] == b'\x89PNG\r\n\x1a\n', "Not a valid PNG"
        
        # Save sample
        with open('test_output_emoji_card.png', 'wb') as f:
            f.write(image_bytes)
        print("✓ Emoji card rendered successfully (test_output_emoji_card.png)")
        
        # Test with curve effect
        image_bytes_curved = await renderer.render_emoji_card(
            text="Curved Text\n曲线文字效果",
            character_name="星乃一歌",
            font_size=36,
            line_spacing=1.5,
            curve_enabled=True,
            curve_intensity=0.8,
            enable_shadow=True,
            emoji_set="google"
        )
        
        with open('test_output_emoji_card_curved.png', 'wb') as f:
            f.write(image_bytes_curved)
        print("✓ Curved emoji card rendered successfully (test_output_emoji_card_curved.png)")
        
        return True
        
    except Exception as e:
        print(f"✗ Emoji card test failed: {e}")
        return False


async def test_character_list_renderer(renderer: PJSKRenderer) -> bool:
    """Test character list rendering."""
    print("\nTesting character list rendering...")
    
    try:
        # Test all characters list
        image_bytes = await renderer.render_character_list(
            list_type="all"
        )
        
        assert len(image_bytes) > 0, "No image bytes generated"
        assert image_bytes[:8] == b'\x89PNG\r\n\x1a\n', "Not a valid PNG"
        
        with open('test_output_list_all.png', 'wb') as f:
            f.write(image_bytes)
        print("✓ All characters list rendered successfully (test_output_list_all.png)")
        
        # Test groups list
        image_bytes_groups = await renderer.render_character_list(
            list_type="groups"
        )
        
        with open('test_output_list_groups.png', 'wb') as f:
            f.write(image_bytes_groups)
        print("✓ Groups list rendered successfully (test_output_list_groups.png)")
        
        # Test group detail
        image_bytes_detail = await renderer.render_character_list(
            list_type="group_detail",
            group_filter="Leo/need"
        )
        
        with open('test_output_list_group_detail.png', 'wb') as f:
            f.write(image_bytes_detail)
        print("✓ Group detail rendered successfully (test_output_list_group_detail.png)")
        
        return True
        
    except Exception as e:
        print(f"✗ Character list test failed: {e}")
        return False


async def test_all_characters(renderer: PJSKRenderer) -> bool:
    """Test rendering cards for all characters."""
    print("\nTesting all character cards...")
    
    success_count = 0
    total_count = len(CHARACTERS)
    
    for character_name in CHARACTERS.keys():
        try:
            image_bytes = await renderer.render_emoji_card(
                text=f"测试卡面\n{character_name}",
                character_name=character_name,
                font_size=32,
                curve_enabled=False,
                enable_shadow=True
            )
            
            # Save individual character card
            safe_name = character_name.replace('/', '_').replace(' ', '_')
            filename = f'test_output_character_{safe_name}.png'
            with open(filename, 'wb') as f:
                f.write(image_bytes)
                
            print(f"✓ {character_name} card rendered successfully")
            success_count += 1
            
        except Exception as e:
            print(f"✗ {character_name} card failed: {e}")
    
    print(f"\nCharacter cards: {success_count}/{total_count} successful")
    return success_count == total_count


async def main():
    """Run smoke tests."""
    print("PJSK Renderer Smoke Test")
    print("=" * 50)
    
    # Change to project directory
    os.chdir(project_root)
    
    # Initialize renderer
    renderer = PJSKRenderer(headless=True)
    
    try:
        print("Initializing renderer...")
        await renderer.initialize()
        print("✓ Renderer initialized successfully")
        
        # Run tests
        results = []
        
        results.append(await test_emoji_card_renderer(renderer))
        results.append(await test_character_list_renderer(renderer))
        results.append(await test_all_characters(renderer))
        
        # Summary
        passed = sum(results)
        total = len(results)
        
        print("\n" + "=" * 50)
        print(f"Smoke Test Results: {passed}/{total} test groups passed")
        
        if passed == total:
            print("✓ All tests passed!")
            print("\nGenerated files:")
            for file in Path('.').glob('test_output_*.png'):
                size = file.stat().st_size
                print(f"  {file.name} ({size:,} bytes)")
            return 0
        else:
            print("✗ Some tests failed!")
            return 1
            
    except Exception as e:
        print(f"✗ Smoke test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        await renderer.close()
        print("✓ Renderer closed")


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)