#!/usr/bin/env python3
"""
Test script to verify that settings changes affect pagination correctly.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config_manager import ConfigManager
from src.epub_reader import EpubReader, Chapter

def test_pagination_with_settings():
    """Test that settings changes affect pagination."""
    print("Testing pagination with different settings...")
    
    # Create a test chapter with some content
    test_content = """This is a test chapter with multiple lines of text to test pagination.
Each line should be wrapped according to the page width setting.
When we change the page width and height settings, the pagination should change accordingly.
This allows us to verify that the settings are actually being applied to the reading experience.
The font size setting would affect how text is displayed, though in a terminal it mainly affects the conceptual size.
Line spacing affects how much vertical space is between lines.
Page width determines how many characters fit on each line before wrapping.
Page height determines how many lines fit on each page.
All of these settings should be saved and restored properly.
This is line 10 of our test content.
This is line 11 of our test content.
This is line 12 of our test content.
This is line 13 of our test content.
This is line 14 of our test content.
This is line 15 of our test content."""
    
    # Test with default settings
    print("\n1. Testing with default settings...")
    config1 = ConfigManager()
    
    # Reset to known default values
    default_settings = {
        'font_size': 12,
        'line_spacing': 1.2,
        'page_width': 80,
        'page_height': 24,
        'theme': 'default'
    }
    config1.set_display_settings(default_settings)
    config1.save_config()
    
    display_settings1 = config1.get_display_settings()
    print(f"   Page width: {display_settings1['page_width']}")
    print(f"   Page height: {display_settings1['page_height']}")
    
    # Create chapter and paginate
    chapter1 = Chapter("Test Chapter", test_content)
    chapter1.paginate(display_settings1['page_width'], display_settings1['page_height'])
    
    print(f"   Total pages with default settings: {len(chapter1.pages)}")
    print(f"   First page preview: {repr(chapter1.pages[0][:100])}...")
    
    # Test with modified settings
    print("\n2. Testing with modified settings...")
    config2 = ConfigManager()
    
    # Use smaller page dimensions
    modified_settings = {
        'font_size': 16,
        'line_spacing': 1.5,
        'page_width': 50,  # Narrower
        'page_height': 15,  # Shorter
        'theme': 'default'
    }
    config2.set_display_settings(modified_settings)
    config2.save_config()
    
    display_settings2 = config2.get_display_settings()
    print(f"   Page width: {display_settings2['page_width']}")
    print(f"   Page height: {display_settings2['page_height']}")
    
    # Create chapter and paginate with new settings
    chapter2 = Chapter("Test Chapter", test_content)
    chapter2.paginate(display_settings2['page_width'], display_settings2['page_height'])
    
    print(f"   Total pages with modified settings: {len(chapter2.pages)}")
    print(f"   First page preview: {repr(chapter2.pages[0][:100])}...")
    
    # Verify that pagination changed
    print("\n3. Verifying pagination differences...")
    
    if len(chapter2.pages) > len(chapter1.pages):
        print("   ✅ Smaller page dimensions resulted in more pages (correct)")
    else:
        print("   ❌ Page count didn't increase as expected")
    
    # Check line wrapping
    first_line_1 = chapter1.pages[0].split('\n')[0]
    first_line_2 = chapter2.pages[0].split('\n')[0]
    
    print(f"   Default settings first line length: {len(first_line_1)}")
    print(f"   Modified settings first line length: {len(first_line_2)}")
    
    if len(first_line_2) < len(first_line_1):
        print("   ✅ Narrower page width resulted in shorter lines (correct)")
    else:
        print("   ❌ Line length didn't decrease as expected")
    
    # Test with very large settings
    print("\n4. Testing with large page settings...")
    config3 = ConfigManager()
    
    large_settings = {
        'font_size': 20,
        'line_spacing': 2.0,
        'page_width': 120,  # Very wide
        'page_height': 40,   # Very tall
        'theme': 'default'
    }
    config3.set_display_settings(large_settings)
    config3.save_config()
    
    display_settings3 = config3.get_display_settings()
    print(f"   Page width: {display_settings3['page_width']}")
    print(f"   Page height: {display_settings3['page_height']}")
    
    chapter3 = Chapter("Test Chapter", test_content)
    chapter3.paginate(display_settings3['page_width'], display_settings3['page_height'])
    
    print(f"   Total pages with large settings: {len(chapter3.pages)}")
    
    if len(chapter3.pages) < len(chapter1.pages):
        print("   ✅ Larger page dimensions resulted in fewer pages (correct)")
    else:
        print("   ❌ Page count didn't decrease as expected")
    
    # Summary
    print(f"\n5. Summary:")
    print(f"   Default (80x24): {len(chapter1.pages)} pages")
    print(f"   Small (50x15): {len(chapter2.pages)} pages")
    print(f"   Large (120x40): {len(chapter3.pages)} pages")
    
    # Verify settings persistence
    print("\n6. Verifying settings persistence...")
    config4 = ConfigManager()
    final_settings = config4.get_display_settings()
    
    if (final_settings['page_width'] == 120 and 
        final_settings['page_height'] == 40 and
        final_settings['font_size'] == 20):
        print("   ✅ Settings persisted correctly after restart")
    else:
        print("   ❌ Settings did not persist correctly")
        print(f"   Got: {final_settings}")
    
    return True

if __name__ == '__main__':
    test_pagination_with_settings()
