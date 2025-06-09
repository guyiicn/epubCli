#!/usr/bin/env python3
"""
Test script to demonstrate visual effects of font size and line spacing settings.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config_manager import ConfigManager
from src.ui_manager import UIManager

def test_visual_effects():
    """Test and demonstrate visual effects of different settings."""
    print("=== EPUB Reader Font Size and Line Spacing Visual Test ===\n")
    
    # Test content
    test_content = "Hello World!\nThis is a test of font size effects.\nYou should see differences between settings."
    
    config = ConfigManager()
    ui = UIManager(config)
    
    # Test different font sizes
    print("1. FONT SIZE COMPARISON:")
    print("-" * 50)
    
    font_sizes = [8, 12, 16, 20, 24]
    for size in font_sizes:
        print(f"\nFont Size {size}:")
        formatted = ui._apply_display_settings(test_content, size, 1.2)
        lines = str(formatted).split('\n')
        for line in lines[:2]:  # Show first 2 lines
            print(f"  {line}")
    
    print("\n" + "=" * 60)
    print("2. LINE SPACING COMPARISON:")
    print("-" * 50)
    
    line_spacings = [0.8, 1.0, 1.5, 2.0, 2.5]
    for spacing in line_spacings:
        print(f"\nLine Spacing {spacing}:")
        formatted = ui._apply_display_settings(test_content, 12, spacing)
        lines = str(formatted).split('\n')
        print(f"  Lines count: {len(lines)}")
        # Show structure
        for i, line in enumerate(lines):
            if line.strip():  # Only show non-empty lines
                print(f"  Line {i+1}: {line}")
            elif i < 6:  # Show first few empty lines to demonstrate spacing
                print(f"  Line {i+1}: [empty line]")
    
    print("\n" + "=" * 60)
    print("3. COMBINED EFFECTS:")
    print("-" * 50)
    
    combinations = [
        (8, 0.8, "Small & Tight"),
        (12, 1.2, "Normal"),
        (20, 2.0, "Large & Spaced"),
        (24, 2.5, "Very Large & Very Spaced")
    ]
    
    for font_size, line_spacing, description in combinations:
        print(f"\n{description} (Font: {font_size}, Spacing: {line_spacing}):")
        formatted = ui._apply_display_settings(test_content, font_size, line_spacing)
        lines = str(formatted).split('\n')
        
        # Show first few lines to demonstrate the effect
        for i, line in enumerate(lines[:6]):
            if line.strip():
                print(f"  {line}")
            else:
                print(f"  [spacing]")
    
    print("\n" + "=" * 60)
    print("4. ANALYSIS:")
    print("-" * 50)
    
    print("Font Size Effects:")
    print("  • Size 8-10: Normal display (slightly dimmed)")
    print("  • Size 12-15: Normal display")
    print("  • Size 16-19: Bold display")
    print("  • Size 20+: Bold + character spacing (T h i s)")
    
    print("\nLine Spacing Effects:")
    print("  • 0.5-0.9: Tight spacing (no extra lines)")
    print("  • 1.0-1.4: Normal spacing (minimal extra lines)")
    print("  • 1.5-2.0: Loose spacing (1-2 extra lines between)")
    print("  • 2.1+: Very loose spacing (3+ extra lines between)")
    
    print("\nTerminal Limitations:")
    print("  • Cannot change actual font size in terminal")
    print("  • Character spacing simulates larger fonts")
    print("  • Bold/dim styles provide visual emphasis")
    print("  • Extra newlines create line spacing effect")
    
    return True

if __name__ == '__main__':
    test_visual_effects()
