#!/usr/bin/env python3
"""
Test script to verify that all character images can be correctly accessed.
"""

import json
from pathlib import Path

def test_image_paths():
    """Test that all character images are accessible."""
    assets_path = Path(__file__).parent / 'pjsk_emoji' / 'assets'
    
    # Load characters.json
    with open(assets_path / 'characters.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("=" * 60)
    print("PJSK Character Images Access Test")
    print("=" * 60)
    
    # Verify metadata
    metadata = data['metadata']
    print(f"\nMetadata:")
    print(f"  Version: {metadata['version']}")
    print(f"  Total Characters: {metadata['total_characters']}")
    print(f"  Total Character Images: {metadata['total_character_images']}")
    print(f"  Image Source: {metadata['image_source']}")
    print(f"  Import Date: {metadata['image_import_date']}")
    
    # Verify each character's images
    print(f"\nCharacter Image Verification:")
    print("-" * 60)
    
    all_accessible = True
    total_files = 0
    
    for name, char_data in data['characters'].items():
        img_path_rel = char_data.get('character_images_path')
        if not img_path_rel:
            print(f"  ✗ {name}: character_images_path not found")
            all_accessible = False
            continue
        
        img_dir = assets_path / img_path_rel
        
        if not img_dir.is_dir():
            print(f"  ✗ {name}: Directory not found at {img_dir}")
            all_accessible = False
            continue
        
        png_files = list(img_dir.glob('*.png'))
        if not png_files:
            print(f"  ✗ {name}: No PNG files found in {img_path_rel}")
            all_accessible = False
            continue
        
        total_files += len(png_files)
        
        # Get file URLs
        file_urls = [f"file://{f.absolute()}" for f in sorted(png_files)[:3]]
        extra = f"... and {len(png_files) - 3} more" if len(png_files) > 3 else ""
        
        print(f"  ✓ {name}")
        print(f"    Path: {img_path_rel}")
        print(f"    Count: {len(png_files)} files")
        print(f"    Sample URLs:")
        for url in file_urls:
            print(f"      - {url}")
        if extra:
            print(f"      {extra}")
    
    print("-" * 60)
    print(f"\nResults:")
    print(f"  Total Files Verified: {total_files}")
    print(f"  Status: {'✓ ALL TESTS PASSED' if all_accessible and total_files == metadata['total_character_images'] else '✗ SOME TESTS FAILED'}")
    
    return all_accessible and total_files == metadata['total_character_images']

if __name__ == '__main__':
    success = test_image_paths()
    exit(0 if success else 1)
