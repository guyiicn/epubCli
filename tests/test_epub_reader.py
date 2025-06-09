#!/usr/bin/env python3
"""
Test cases for EPUB Reader application.
"""

import unittest
import os
import sys
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database import Database
from src.config_manager import ConfigManager
from src.file_manager import FileManager
from src.epub_reader import EpubReader, Chapter


class TestDatabase(unittest.TestCase):
    """Test cases for Database class."""
    
    def setUp(self):
        """Set up test database."""
        self.test_db_path = tempfile.mktemp(suffix='.db')
        self.db = Database(self.test_db_path)
    
    def tearDown(self):
        """Clean up test database."""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_database_initialization(self):
        """Test database initialization."""
        self.assertTrue(os.path.exists(self.test_db_path))
    
    def test_add_book(self):
        """Test adding a book to database."""
        result = self.db.add_or_update_book(
            "test_book.epub",
            "Test Book",
            "Test Author",
            10
        )
        self.assertTrue(result)
    
    def test_update_reading_progress(self):
        """Test updating reading progress."""
        # First add a book
        self.db.add_or_update_book("test_book.epub", "Test Book", "Test Author", 10)
        
        # Update progress
        result = self.db.update_reading_progress("test_book.epub", 5, 100, 30)
        self.assertTrue(result)
        
        # Check progress
        progress = self.db.get_reading_progress("test_book.epub")
        self.assertIsNotNone(progress)
        self.assertEqual(progress['chapter'], 5)
        self.assertEqual(progress['position'], 100)
    
    def test_bookmarks(self):
        """Test bookmark functionality."""
        # Add a book first
        self.db.add_or_update_book("test_book.epub", "Test Book", "Test Author", 10)
        
        # Add bookmark
        result = self.db.add_bookmark("test_book.epub", 3, 50, "Important note")
        self.assertTrue(result)
        
        # Get bookmarks
        bookmarks = self.db.get_bookmarks("test_book.epub")
        self.assertEqual(len(bookmarks), 1)
        self.assertEqual(bookmarks[0]['chapter'], 3)
        self.assertEqual(bookmarks[0]['position'], 50)
        self.assertEqual(bookmarks[0]['note'], "Important note")
    
    def test_settings(self):
        """Test settings functionality."""
        # Set a setting
        result = self.db.set_setting("test_key", "test_value")
        self.assertTrue(result)
        
        # Get the setting
        value = self.db.get_setting("test_key")
        self.assertEqual(value, "test_value")
        
        # Get non-existent setting with default
        value = self.db.get_setting("non_existent", "default")
        self.assertEqual(value, "default")


class TestConfigManager(unittest.TestCase):
    """Test cases for ConfigManager class."""
    
    def setUp(self):
        """Set up test configuration."""
        self.test_config_path = tempfile.mktemp(suffix='.ini')
        self.config = ConfigManager(self.test_config_path)
    
    def tearDown(self):
        """Clean up test configuration."""
        if os.path.exists(self.test_config_path):
            os.remove(self.test_config_path)
    
    def test_default_config(self):
        """Test default configuration values."""
        display_settings = self.config.get_display_settings()
        self.assertEqual(display_settings['font_size'], 12)
        self.assertEqual(display_settings['page_width'], 80)
        self.assertEqual(display_settings['page_height'], 24)
    
    def test_set_and_get_settings(self):
        """Test setting and getting configuration values."""
        # Set a value
        result = self.config.set('DISPLAY', 'font_size', '16')
        self.assertTrue(result)
        
        # Get the value
        value = self.config.get_int('DISPLAY', 'font_size')
        self.assertEqual(value, 16)
    
    def test_display_settings(self):
        """Test display settings management."""
        new_settings = {
            'font_size': 14,
            'line_spacing': 1.5,
            'page_width': 100
        }
        
        result = self.config.set_display_settings(new_settings)
        self.assertTrue(result)
        
        # Verify settings were saved
        display_settings = self.config.get_display_settings()
        self.assertEqual(display_settings['font_size'], 14)
        self.assertEqual(display_settings['line_spacing'], 1.5)
        self.assertEqual(display_settings['page_width'], 100)
    
    def test_config_validation(self):
        """Test configuration validation."""
        # Valid config should pass
        self.assertTrue(self.config.validate_config())
        
        # Invalid font size should fail
        self.config.set('DISPLAY', 'font_size', '200')
        self.assertFalse(self.config.validate_config())


class TestFileManager(unittest.TestCase):
    """Test cases for FileManager class."""
    
    def setUp(self):
        """Set up test file manager."""
        self.test_dir = tempfile.mkdtemp()
        self.file_manager = FileManager(self.test_dir)
    
    def tearDown(self):
        """Clean up test directory."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_safe_filename_generation(self):
        """Test safe filename generation."""
        # Test normal case
        filename = self.file_manager._get_safe_filename("Test Book", "Test Author")
        self.assertEqual(filename, "Test_Author_-_Test_Book.epub")
        
        # Test with invalid characters
        filename = self.file_manager._get_safe_filename("Test/Book<>", "Test|Author")
        self.assertNotIn('/', filename)
        self.assertNotIn('<', filename)
        self.assertNotIn('>', filename)
        self.assertNotIn('|', filename)
    
    def test_library_stats(self):
        """Test library statistics."""
        stats = self.file_manager.get_library_stats()
        self.assertEqual(stats['total_books'], 0)
        self.assertEqual(stats['total_size_bytes'], 0)
    
    def test_epub_validation(self):
        """Test EPUB file validation."""
        # Test non-existent file
        self.assertFalse(self.file_manager.validate_epub("non_existent.epub"))
        
        # Test non-EPUB file
        test_file = os.path.join(self.test_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("Not an EPUB file")
        self.assertFalse(self.file_manager.validate_epub(test_file))


class TestChapter(unittest.TestCase):
    """Test cases for Chapter class."""
    
    def setUp(self):
        """Set up test chapter."""
        self.content = "This is a test chapter with multiple lines.\n\nIt has paragraphs and should be paginated properly when the content is long enough to span multiple pages."
        self.chapter = Chapter("Test Chapter", self.content)
    
    def test_chapter_initialization(self):
        """Test chapter initialization."""
        self.assertEqual(self.chapter.title, "Test Chapter")
        self.assertEqual(self.chapter.content, self.content)
        self.assertEqual(self.chapter.current_page, 0)
    
    def test_pagination(self):
        """Test chapter pagination."""
        self.chapter.paginate(page_width=20, page_height=5)
        self.assertGreater(len(self.chapter.pages), 0)
    
    def test_page_navigation(self):
        """Test page navigation."""
        self.chapter.paginate(page_width=20, page_height=3)
        
        # Test next page
        if len(self.chapter.pages) > 1:
            result = self.chapter.next_page()
            self.assertTrue(result)
            self.assertEqual(self.chapter.current_page, 1)
        
        # Test previous page
        result = self.chapter.prev_page()
        if len(self.chapter.pages) > 1:
            self.assertTrue(result)
        self.assertEqual(self.chapter.current_page, 0)
    
    def test_goto_page(self):
        """Test going to specific page."""
        self.chapter.paginate(page_width=20, page_height=3)
        
        # Valid page
        if len(self.chapter.pages) > 1:
            result = self.chapter.goto_page(1)
            self.assertTrue(result)
            self.assertEqual(self.chapter.current_page, 1)
        
        # Invalid page
        result = self.chapter.goto_page(999)
        self.assertFalse(result)
    
    def test_page_info(self):
        """Test page information."""
        self.chapter.paginate(page_width=20, page_height=3)
        info = self.chapter.get_page_info()
        
        self.assertIn('current_page', info)
        self.assertIn('total_pages', info)
        self.assertIn('page_index', info)
        self.assertEqual(info['current_page'], 1)  # 1-based
        self.assertEqual(info['page_index'], 0)    # 0-based


class TestEpubReaderMocked(unittest.TestCase):
    """Test cases for EpubReader class with mocked dependencies."""
    
    @patch('src.epub_reader.epub.read_epub')
    def test_epub_reader_initialization(self, mock_read_epub):
        """Test EPUB reader initialization."""
        # Mock the epub book
        mock_book = Mock()
        mock_book.get_metadata.return_value = [("Test Title",)]
        mock_book.get_items.return_value = []
        mock_book.toc = []
        mock_read_epub.return_value = mock_book
        
        reader = EpubReader("test.epub")
        self.assertEqual(reader.title, "Test Title")
        self.assertEqual(reader.file_path, "test.epub")
    
    @patch('src.epub_reader.epub.read_epub')
    def test_book_info(self, mock_read_epub):
        """Test getting book information."""
        # Mock the epub book
        mock_book = Mock()
        mock_book.get_metadata.return_value = [("Test Title",)]
        mock_book.get_items.return_value = []
        mock_book.toc = []
        mock_read_epub.return_value = mock_book
        
        reader = EpubReader("test.epub")
        info = reader.get_book_info()
        
        self.assertEqual(info['title'], "Test Title")
        self.assertEqual(info['file_path'], "test.epub")
        self.assertEqual(info['total_chapters'], 0)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system."""
    
    def setUp(self):
        """Set up integration test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test.db")
        self.config_path = os.path.join(self.test_dir, "test.ini")
        
        self.db = Database(self.db_path)
        self.config = ConfigManager(self.config_path)
        self.file_manager = FileManager(os.path.join(self.test_dir, "books"))
    
    def tearDown(self):
        """Clean up integration test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_complete_workflow(self):
        """Test complete workflow integration."""
        # Test database and config initialization
        self.assertTrue(os.path.exists(self.db_path))
        # Config file is created when save_config is called
        self.config.save_config()
        self.assertTrue(os.path.exists(self.config_path))
        
        # Test adding a book to database
        result = self.db.add_or_update_book(
            "test_book.epub",
            "Integration Test Book",
            "Test Author",
            5
        )
        self.assertTrue(result)
        
        # Test updating progress
        result = self.db.update_reading_progress("test_book.epub", 2, 50, 120)
        self.assertTrue(result)
        
        # Test getting recent books
        recent_books = self.db.get_recent_books(10)
        self.assertEqual(len(recent_books), 1)
        self.assertEqual(recent_books[0]['title'], "Integration Test Book")
        
        # Test configuration management
        display_settings = self.config.get_display_settings()
        self.assertIsInstance(display_settings, dict)
        self.assertIn('font_size', display_settings)


def create_test_suite():
    """Create and return test suite."""
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestDatabase))
    suite.addTest(unittest.makeSuite(TestConfigManager))
    suite.addTest(unittest.makeSuite(TestFileManager))
    suite.addTest(unittest.makeSuite(TestChapter))
    suite.addTest(unittest.makeSuite(TestEpubReaderMocked))
    suite.addTest(unittest.makeSuite(TestIntegration))
    
    return suite


def run_tests():
    """Run all tests."""
    print("Running EPUB Reader Test Suite...")
    print("=" * 50)
    
    # Create test suite
    suite = create_test_suite()
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nOverall result: {'PASS' if success else 'FAIL'}")
    
    return success


if __name__ == '__main__':
    run_tests()
