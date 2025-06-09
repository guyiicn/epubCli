#!/usr/bin/env python3
"""
Test script to verify UI settings functionality.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config_manager import ConfigManager
from src.ui_manager import UIManager

def test_ui_settings():
    """Test UI settings functionality."""
    print("Testing UI settings functionality...")
    
    # Create config manager and UI manager
    config = ConfigManager()
    ui = UIManager(config)
    
    # Get initial settings
    print("\n1. Initial settings:")
    initial_settings = config.get_all_settings()
    print(f"   Font size: {initial_settings['display']['font_size']}")
    print(f"   Page width: {initial_settings['display']['page_width']}")
    print(f"   Page height: {initial_settings['display']['page_height']}")
    
    # Simulate settings changes (like what the UI would do)
    print("\n2. Simulating UI settings changes...")
    
    # Create modified settings like the UI would
    modified_settings = {
        'display': {
            'font_size': 18,
            'line_spacing': 1.8,
            'page_width': 100,
            'page_height': 35,
            'theme': 'default'
        },
        'reading': {
            'show_progress': False,
            'auto_save_interval': 60,
            'wrap_text': True,
            'show_chapter_title': True
        }
    }
    
    # Test the main.py show_settings logic
    print("   Simulating main.py settings save logic...")
    
    # Save display settings
    if 'display' in modified_settings:
        success1 = config.set_display_settings(modified_settings['display'])
        print(f"   Display settings save: {success1}")
    
    # Save reading settings
    if 'reading' in modified_settings:
        reading_settings = modified_settings['reading']
        for key, value in reading_settings.items():
            config.set('READING', key, str(value))
        print("   Reading settings updated")
    
    # Save the configuration
    save_result = config.save_config()
    print(f"   Config file save: {save_result}")
    
    # Verify settings were applied
    print("\n3. Verifying settings were applied...")
    
    # Reload config to verify persistence
    config2 = ConfigManager()
    final_settings = config2.get_all_settings()
    
    print(f"   Font size: {final_settings['display']['font_size']} (expected: 18)")
    print(f"   Page width: {final_settings['display']['page_width']} (expected: 100)")
    print(f"   Page height: {final_settings['display']['page_height']} (expected: 35)")
    print(f"   Line spacing: {final_settings['display']['line_spacing']} (expected: 1.8)")
    print(f"   Auto save interval: {final_settings['reading']['auto_save_interval']} (expected: 60)")
    print(f"   Show progress: {final_settings['reading']['show_progress']} (expected: False)")
    
    # Test UI manager initialization with new settings
    print("\n4. Testing UI manager with new settings...")
    ui2 = UIManager(config2)
    print(f"   UI page width: {ui2.page_width} (expected: 100)")
    print(f"   UI page height: {ui2.page_height} (expected: 35)")
    
    # Verify all values
    success = True
    checks = [
        (final_settings['display']['font_size'], 18, "Font size"),
        (final_settings['display']['page_width'], 100, "Page width"),
        (final_settings['display']['page_height'], 35, "Page height"),
        (final_settings['display']['line_spacing'], 1.8, "Line spacing"),
        (final_settings['reading']['auto_save_interval'], 60, "Auto save interval"),
        (final_settings['reading']['show_progress'], False, "Show progress"),
        (ui2.page_width, 100, "UI page width"),
        (ui2.page_height, 35, "UI page height")
    ]
    
    for actual, expected, name in checks:
        if actual != expected:
            print(f"   ❌ {name}: got {actual}, expected {expected}")
            success = False
    
    if success:
        print("\n✅ All UI settings functionality working correctly!")
        print("   - Settings are properly saved to config file")
        print("   - Settings persist after restart")
        print("   - UI manager correctly loads new settings")
    else:
        print("\n❌ Some UI settings functionality issues found!")
    
    return success

if __name__ == '__main__':
    test_ui_settings()
