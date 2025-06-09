"""
Configuration management module for EPUB reader settings.
"""

import configparser
import os
from typing import Dict, Any, Optional


class ConfigManager:
    """Manages application configuration and user settings."""
    
    def __init__(self, config_path: str = "data/config.ini"):
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        self._ensure_data_dir()
        self._load_default_config()
        self._load_config()
    
    def _ensure_data_dir(self):
        """Ensure data directory exists."""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
    
    def _load_default_config(self):
        """Load default configuration values."""
        self.config['DISPLAY'] = {
            'font_size': '12',
            'line_spacing': '1.2',
            'page_width': '80',
            'page_height': '24',
            'theme': 'default'
        }
        
        self.config['READING'] = {
            'auto_save_interval': '30',
            'show_progress': 'true',
            'wrap_text': 'true',
            'show_chapter_title': 'true'
        }
        
        self.config['CONTROLS'] = {
            'page_up': 'up,k,pgup',
            'page_down': 'down,j,pgdn',
            'next_chapter': 'right,l',
            'prev_chapter': 'left,h',
            'goto_toc': 't',
            'toggle_bookmark': 'b',
            'show_bookmarks': 'shift+b',
            'settings': 's',
            'quit': 'q,esc'
        }
        
        self.config['FILES'] = {
            'books_directory': 'data/books',
            'max_recent_books': '20',
            'auto_backup': 'true'
        }
    
    def _load_config(self):
        """Load configuration from file."""
        if os.path.exists(self.config_path):
            try:
                self.config.read(self.config_path)
            except configparser.Error as e:
                print(f"Error loading config: {e}")
                print("Using default configuration.")
    
    def save_config(self) -> bool:
        """Save current configuration to file."""
        try:
            with open(self.config_path, 'w') as config_file:
                self.config.write(config_file)
            return True
        except IOError as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, section: str, key: str, fallback: str = "") -> str:
        """Get a configuration value."""
        try:
            return self.config.get(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback
    
    def get_int(self, section: str, key: str, fallback: int = 0) -> int:
        """Get a configuration value as integer."""
        try:
            return self.config.getint(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def get_float(self, section: str, key: str, fallback: float = 0.0) -> float:
        """Get a configuration value as float."""
        try:
            return self.config.getfloat(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def get_bool(self, section: str, key: str, fallback: bool = False) -> bool:
        """Get a configuration value as boolean."""
        try:
            return self.config.getboolean(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def set(self, section: str, key: str, value: str) -> bool:
        """Set a configuration value."""
        try:
            if not self.config.has_section(section):
                self.config.add_section(section)
            self.config.set(section, key, str(value))
            return True
        except configparser.Error as e:
            print(f"Error setting config: {e}")
            return False
    
    def get_display_settings(self) -> Dict[str, Any]:
        """Get display-related settings."""
        return {
            'font_size': self.get_int('DISPLAY', 'font_size', 12),
            'line_spacing': self.get_float('DISPLAY', 'line_spacing', 1.2),
            'page_width': self.get_int('DISPLAY', 'page_width', 80),
            'page_height': self.get_int('DISPLAY', 'page_height', 24),
            'theme': self.get('DISPLAY', 'theme', 'default')
        }
    
    def set_display_settings(self, settings: Dict[str, Any]) -> bool:
        """Set display-related settings."""
        try:
            for key, value in settings.items():
                self.set('DISPLAY', key, str(value))
            return self.save_config()
        except Exception as e:
            print(f"Error setting display settings: {e}")
            return False
    
    def get_reading_settings(self) -> Dict[str, Any]:
        """Get reading-related settings."""
        return {
            'auto_save_interval': self.get_int('READING', 'auto_save_interval', 30),
            'show_progress': self.get_bool('READING', 'show_progress', True),
            'wrap_text': self.get_bool('READING', 'wrap_text', True),
            'show_chapter_title': self.get_bool('READING', 'show_chapter_title', True)
        }
    
    def get_control_keys(self) -> Dict[str, list]:
        """Get keyboard control mappings."""
        controls = {}
        for key, value in self.config['CONTROLS'].items():
            controls[key] = [k.strip() for k in value.split(',')]
        return controls
    
    def get_file_settings(self) -> Dict[str, Any]:
        """Get file-related settings."""
        return {
            'books_directory': self.get('FILES', 'books_directory', 'data/books'),
            'max_recent_books': self.get_int('FILES', 'max_recent_books', 20),
            'auto_backup': self.get_bool('FILES', 'auto_backup', True)
        }
    
    def reset_to_defaults(self) -> bool:
        """Reset configuration to default values."""
        try:
            self.config.clear()
            self._load_default_config()
            return self.save_config()
        except Exception as e:
            print(f"Error resetting config: {e}")
            return False
    
    def get_all_settings(self) -> Dict[str, Dict[str, Any]]:
        """Get all configuration settings."""
        return {
            'display': self.get_display_settings(),
            'reading': self.get_reading_settings(),
            'controls': self.get_control_keys(),
            'files': self.get_file_settings()
        }
    
    def validate_config(self) -> bool:
        """Validate current configuration."""
        try:
            # Check required sections
            required_sections = ['DISPLAY', 'READING', 'CONTROLS', 'FILES']
            for section in required_sections:
                if not self.config.has_section(section):
                    print(f"Missing required section: {section}")
                    return False
            
            # Validate numeric values
            font_size = self.get_int('DISPLAY', 'font_size')
            if font_size < 8 or font_size > 72:
                print("Invalid font size")
                return False
            
            line_spacing = self.get_float('DISPLAY', 'line_spacing')
            if line_spacing < 0.5 or line_spacing > 3.0:
                print("Invalid line spacing")
                return False
            
            return True
        except Exception as e:
            print(f"Config validation error: {e}")
            return False
