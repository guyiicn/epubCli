#!/usr/bin/env python3
"""
Test script to verify settings save functionality.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config_manager import ConfigManager

def test_settings_save():
    """Test settings save functionality."""
    print("Testing settings save functionality...")
    
    # Create config manager
    config = ConfigManager()
    
    # Get current settings
    print("\n1. Current settings:")
    current_settings = config.get_all_settings()
    print(f"   Font size: {current_settings['display']['font_size']}")
    print(f"   Page width: {current_settings['display']['page_width']}")
    print(f"   Page height: {current_settings['display']['page_height']}")
    print(f"   Auto save interval: {current_settings['reading']['auto_save_interval']}")
    
    # Modify settings
    print("\n2. Modifying settings...")
    new_display_settings = {
        'font_size': 16,
        'page_width': 90,
        'page_height': 30,
        'line_spacing': 1.5,
        'theme': 'default'
    }
    
    # Save display settings
    success = config.set_display_settings(new_display_settings)
    print(f"   Display settings save result: {success}")
    
    # Save reading settings
    config.set('READING', 'auto_save_interval', '45')
    config.set('READING', 'show_progress', 'false')
    
    # Save config file
    save_result = config.save_config()
    print(f"   Config file save result: {save_result}")
    
    # Verify settings were saved
    print("\n3. Verifying saved settings...")
    
    # Create new config manager to reload from file
    config2 = ConfigManager()
    new_settings = config2.get_all_settings()
    
    print(f"   Font size: {new_settings['display']['font_size']} (expected: 16)")
    print(f"   Page width: {new_settings['display']['page_width']} (expected: 90)")
    print(f"   Page height: {new_settings['display']['page_height']} (expected: 30)")
    print(f"   Line spacing: {new_settings['display']['line_spacing']} (expected: 1.5)")
    print(f"   Auto save interval: {new_settings['reading']['auto_save_interval']} (expected: 45)")
    print(f"   Show progress: {new_settings['reading']['show_progress']} (expected: False)")
    
    # Check if values match
    success = True
    if new_settings['display']['font_size'] != 16:
        print("   ❌ Font size not saved correctly!")
        success = False
    if new_settings['display']['page_width'] != 90:
        print("   ❌ Page width not saved correctly!")
        success = False
    if new_settings['display']['page_height'] != 30:
        print("   ❌ Page height not saved correctly!")
        success = False
    if new_settings['display']['line_spacing'] != 1.5:
        print("   ❌ Line spacing not saved correctly!")
        success = False
    if new_settings['reading']['auto_save_interval'] != 45:
        print("   ❌ Auto save interval not saved correctly!")
        success = False
    if new_settings['reading']['show_progress'] != False:
        print("   ❌ Show progress not saved correctly!")
        success = False
    
    if success:
        print("\n✅ All settings saved and loaded correctly!")
    else:
        print("\n❌ Some settings were not saved correctly!")
    
    # Check if config file exists
    config_file = "data/config.ini"
    if os.path.exists(config_file):
        print(f"\n4. Config file exists at: {config_file}")
        with open(config_file, 'r') as f:
            content = f.read()
            print("   Config file content:")
            print("   " + "\n   ".join(content.split('\n')[:20]))  # Show first 20 lines
    else:
        print(f"\n❌ Config file not found at: {config_file}")
    
    return success

if __name__ == '__main__':
    test_settings_save()
