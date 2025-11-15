#!/usr/bin/env python3
"""
Simple renderer test script for quick verification.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


async def quick_test():
    """Quick test of the renderer."""
    print("Quick PJSK Renderer Test")
    print("=" * 30)
    
    # Change to project directory
    os.chdir(project_root)
    
    try:
        from pjsk_emoji.renderer import get_renderer
        
        print("Getting renderer...")
        renderer = await get_renderer()
        print("✓ Renderer obtained")
        
        print("Rendering test card...")
        image_bytes = await renderer.render_emoji_card(
            text="快速测试\nQuick Test",
            character_name="初音未来",
            font_size=48,
            enable_shadow=True
        )
        
        print(f"✓ Rendered {len(image_bytes)} bytes")
        
        # Save test image
        with open('quick_test_output.png', 'wb') as f:
            f.write(image_bytes)
        print("✓ Saved as quick_test_output.png")
        
        print("Rendering character list...")
        list_bytes = await renderer.render_character_list(list_type="all")
        
        with open('quick_test_list.png', 'wb') as f:
            f.write(list_bytes)
        print(f"✓ List rendered ({len(list_bytes)} bytes) saved as quick_test_list.png")
        
        print("\n✓ Quick test completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Quick test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = asyncio.run(quick_test())
    sys.exit(0 if success else 1)