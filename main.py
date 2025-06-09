#!/usr/bin/env python3
"""
EPUB CLI Reader - Main application entry point.
"""

import sys
import os
import time
import threading
from typing import Optional, Dict, Any
import argparse

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database import Database
from src.config_manager import ConfigManager
from src.file_manager import FileManager
from src.epub_reader import EpubReader
from src.ui_manager import UIManager


class EpubReaderApp:
    """Main EPUB Reader application."""
    
    def __init__(self):
        self.db = Database()
        self.config = ConfigManager()
        self.file_manager = FileManager()
        self.ui = UIManager(self.config)
        self.current_reader: Optional[EpubReader] = None
        self.running = False
        self.auto_save_timer: Optional[threading.Timer] = None
        self.last_save_time = time.time()
    
    def run(self, file_path: Optional[str] = None):
        """Run the main application."""
        self.running = True
        
        try:
            if file_path:
                # Open specific file
                if self.open_book(file_path):
                    self.reading_loop()
                else:
                    self.ui.show_error(f"Failed to open file: {file_path}")
            else:
                # Show main menu
                self.main_menu()
        
        except KeyboardInterrupt:
            self.ui.show_message("Goodbye!", "info")
        except Exception as e:
            self.ui.show_error(f"Unexpected error: {e}")
        finally:
            self.cleanup()
    
    def main_menu(self):
        """Display main menu."""
        while self.running:
            self.ui.clear_screen()
            
            # Get recent books
            recent_books = self.db.get_recent_books(5)
            
            self.ui.console.print("[bold blue]📖 EPUB Reader[/bold blue]\n")
            
            if recent_books:
                self.ui.console.print("[bold]Recent Books:[/bold]")
                for i, book in enumerate(recent_books, 1):
                    progress = f"{book['current_chapter'] + 1}/{book['total_chapters']}"
                    self.ui.console.print(f"  {i}. {book['title']} ({progress})")
                self.ui.console.print()
            
            self.ui.console.print("[bold]Options:[/bold]")
            self.ui.console.print("  O - Open EPUB file")
            self.ui.console.print("  L - Library")
            self.ui.console.print("  S - Settings")
            self.ui.console.print("  H - Help")
            self.ui.console.print("  Q - Quit")
            
            if recent_books:
                self.ui.console.print(f"\n  1-{len(recent_books)} - Open recent book")
            
            choice = self.ui.get_input("\nChoice").lower()
            
            if choice == 'q':
                break
            elif choice == 'o':
                self.open_file_dialog()
            elif choice == 'l':
                self.show_library()
            elif choice == 's':
                self.show_settings()
            elif choice == 'h':
                self.ui.show_help()
            elif choice.isdigit() and recent_books:
                idx = int(choice) - 1
                if 0 <= idx < len(recent_books):
                    if self.open_book(recent_books[idx]['file_path']):
                        self.reading_loop()
        
        self.running = False
    
    def open_file_dialog(self):
        """Open file selection dialog."""
        file_path = self.ui.show_file_browser()
        if file_path:
            if self.open_book(file_path):
                self.reading_loop()
    
    def show_library(self):
        """Show library and select book."""
        books = self.db.get_all_books()
        selected_path = self.ui.show_library(books)
        if selected_path:
            if self.open_book(selected_path):
                self.reading_loop()
    
    def show_settings(self):
        """Show settings menu."""
        current_settings = self.config.get_all_settings()
        updated_settings = self.ui.show_settings(current_settings)
        
        # Always save settings after modification (UI handles the changes)
        # Save all setting categories, not just display
        if updated_settings:
            # Save display settings
            if 'display' in updated_settings:
                self.config.set_display_settings(updated_settings['display'])
            
            # Save reading settings
            if 'reading' in updated_settings:
                reading_settings = updated_settings['reading']
                for key, value in reading_settings.items():
                    self.config.set('READING', key, str(value))
            
            # Save the configuration
            if self.config.save_config():
                self.ui.show_message("Settings saved successfully!", "success")
                
                # Re-paginate if display settings changed and we have a current reader
                if self.current_reader and 'display' in updated_settings:
                    display_settings = self.config.get_display_settings()
                    self.current_reader.paginate_chapters(
                        display_settings['page_width'],
                        display_settings['page_height']
                    )
                    # Update UI manager's page dimensions
                    self.ui.page_width = display_settings['page_width']
                    self.ui.page_height = display_settings['page_height']
            else:
                self.ui.show_message("Failed to save settings!", "error")
            
            time.sleep(1)
    
    def open_book(self, file_path: str) -> bool:
        """Open an EPUB book with proper position restoration."""
        try:
            # Step 1: Validate file
            if not self.file_manager.validate_epub(file_path):
                self.ui.show_error("Invalid EPUB file")
                return False
            
            # Step 2: Create reader and load EPUB content
            self.current_reader = EpubReader(file_path)
            if not self.current_reader.chapters:
                self.ui.show_error("No readable content found in EPUB")
                return False
            
            # Step 3: Add to library and get library path
            library_path = self.file_manager.add_book(
                file_path, 
                self.current_reader.title, 
                self.current_reader.author
            )
            
            # Update database with book info
            if library_path:
                self.db.add_or_update_book(
                    library_path,
                    self.current_reader.title,
                    self.current_reader.author,
                    len(self.current_reader.chapters)
                )
                self.current_reader.file_path = library_path
            
            # Step 4: Paginate chapters
            display_settings = self.config.get_display_settings()
            self.current_reader.paginate_chapters(
                display_settings['page_width'],
                display_settings['page_height']
            )
            
            # Step 5: Read saved position from database
            # Try both library path and original file path
            saved_progress = None
            if library_path:
                saved_progress = self.db.get_reading_progress(library_path)
            if not saved_progress:
                saved_progress = self.db.get_reading_progress(file_path)
            
            # Step 6: Navigate to saved position
            if saved_progress:
                target_chapter = saved_progress['chapter']
                target_page = saved_progress['position']
                
                # Validate and navigate to saved position
                if (0 <= target_chapter < len(self.current_reader.chapters)):
                    # Set chapter index directly
                    self.current_reader.current_chapter = target_chapter
                    
                    # Get the target chapter and set page
                    chapter = self.current_reader.get_current_chapter()
                    if chapter and 0 <= target_page < len(chapter.pages):
                        chapter.current_page = target_page
                    else:
                        # If page is invalid, go to first page of chapter
                        chapter.current_page = 0
                else:
                    # If chapter is invalid, go to first chapter
                    self.current_reader.current_chapter = 0
                    chapter = self.current_reader.get_current_chapter()
                    if chapter:
                        chapter.current_page = 0
            else:
                # No saved position, start from beginning
                self.current_reader.current_chapter = 0
                chapter = self.current_reader.get_current_chapter()
                if chapter:
                    chapter.current_page = 0
            
            # Step 7: Verify final position
            final_position = self.current_reader.get_reading_position()
            
            # Start auto-save timer
            self.start_auto_save()
            
            return True
            
        except Exception as e:
            self.ui.show_error(f"Error opening book: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def reading_loop(self):
        """Main reading loop."""
        if not self.current_reader:
            return
        
        while self.running:
            try:
                self.display_current_page()
                
                # Get user input using keyboard listener
                key = self.ui.get_key_input()
                
                if not self.handle_key_input(key):
                    break
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.ui.show_error(f"Error in reading loop: {e}")
                break
        
        # Save progress before exiting
        self.save_progress()
        self.stop_auto_save()
    
    def display_current_page(self):
        """Display the current page with optimized rendering."""
        if not self.current_reader:
            return
        
        chapter = self.current_reader.get_current_chapter()
        if not chapter:
            return
        
        # Get content
        content = chapter.get_current_page()
        
        # Get info
        book_info = self.current_reader.get_book_info()
        page_info = chapter.get_page_info()
        
        chapter_info = f"Chapter {self.current_reader.current_chapter + 1}/{book_info['total_chapters']}"
        page_display = f"Page {page_info['current_page']}/{page_info['total_pages']}"
        
        # Display with smooth update
        self.ui.show_reading_view(
            book_info['title'],
            book_info['author'],
            chapter.title,
            content,
            chapter_info,
            page_display
        )
    
    def handle_key_input(self, key: str) -> bool:
        """Handle keyboard input. Returns False to exit reading loop."""
        if not self.current_reader:
            return False
        
        chapter = self.current_reader.get_current_chapter()
        if not chapter:
            return False
        
        # Store position before navigation for comparison
        old_position = self.current_reader.get_reading_position()
        
        # Navigation keys
        if key in ['down', 'j', 'enter', 'space']:  # Down/Next page
            if not chapter.next_page():
                self.current_reader.next_chapter()
        
        elif key in ['up', 'k']:  # Up/Previous page
            if not chapter.prev_page():
                if self.current_reader.prev_chapter():
                    new_chapter = self.current_reader.get_current_chapter()
                    if new_chapter and new_chapter.pages:
                        new_chapter.current_page = len(new_chapter.pages) - 1
        
        elif key in ['right', 'l']:  # Next chapter
            self.current_reader.next_chapter()
        
        elif key in ['left', 'h']:  # Previous chapter
            self.current_reader.prev_chapter()
        
        # Auto-save reading position after any navigation
        new_position = self.current_reader.get_reading_position()
        if (old_position['chapter'] != new_position['chapter'] or 
            old_position['page'] != new_position['page']):
            self.auto_save_position()
        
        # Menu keys
        if key == 't':  # Table of contents
            self.show_table_of_contents()
        
        elif key == 'b':  # Toggle bookmark
            self.toggle_bookmark()
        
        elif key == 'shift+b':  # Show bookmarks
            self.show_bookmarks()
        
        elif key == 's':  # Settings
            self.show_settings()
            # Re-paginate if display settings changed
            display_settings = self.config.get_display_settings()
            self.current_reader.paginate_chapters(
                display_settings['page_width'],
                display_settings['page_height']
            )
        
        elif key == 'g':  # Go to page/chapter
            self.goto_dialog()
        
        elif key == '/':  # Search
            self.search_dialog()
        
        elif key == 'o':  # Open new file
            self.save_progress()
            return False  # Exit to main menu
        
        elif key == 'l':  # Library
            self.save_progress()
            return False  # Exit to main menu
        
        elif key == '?':  # Help
            self.ui.show_help()
        
        elif key in ['q', 'esc']:  # Quit
            return False
        
        # Update last activity time
        self.last_save_time = time.time()
        
        return True
    
    def show_table_of_contents(self):
        """Show table of contents."""
        if not self.current_reader:
            return
        
        selected = self.ui.show_table_of_contents(
            self.current_reader.toc, 
            self.current_reader.current_chapter
        )
        
        if selected is not None:
            self.current_reader.goto_chapter(selected)
    
    def toggle_bookmark(self):
        """Toggle bookmark at current position."""
        if not self.current_reader:
            return
        
        position = self.current_reader.get_reading_position()
        note = self.ui.get_input("Bookmark note (optional):")
        
        if self.db.add_bookmark(
            self.current_reader.file_path,
            position['chapter'],
            position['page'],
            note
        ):
            self.ui.show_message("Bookmark added!", "success")
        else:
            self.ui.show_message("Failed to add bookmark", "error")
        
        time.sleep(1)
    
    def show_bookmarks(self):
        """Show bookmarks for current book."""
        if not self.current_reader:
            return
        
        bookmarks = self.db.get_bookmarks(self.current_reader.file_path)
        result = self.ui.show_bookmarks(bookmarks)
        
        if result:
            if result.get('action') == 'delete':
                bookmark = result['bookmark']
                if self.db.delete_bookmark(bookmark['id']):
                    self.ui.show_message("Bookmark deleted!", "success")
                else:
                    self.ui.show_message("Failed to delete bookmark", "error")
                time.sleep(1)
            else:
                # Go to bookmark
                self.current_reader.set_reading_position(
                    result['chapter'],
                    result['position']
                )
    
    def goto_dialog(self):
        """Show go to page/chapter dialog."""
        if not self.current_reader:
            return
        
        choice = self.ui.get_input("Go to (c)hapter or (p)age?").lower()
        
        if choice == 'c':
            chapter_num = self.ui.get_input("Chapter number:")
            try:
                chapter_idx = int(chapter_num) - 1
                if 0 <= chapter_idx < len(self.current_reader.chapters):
                    self.current_reader.goto_chapter(chapter_idx)
                else:
                    self.ui.show_message("Invalid chapter number", "error")
                    time.sleep(1)
            except ValueError:
                self.ui.show_message("Invalid input", "error")
                time.sleep(1)
        
        elif choice == 'p':
            page_num = self.ui.get_input("Page number:")
            try:
                page_idx = int(page_num) - 1
                chapter = self.current_reader.get_current_chapter()
                if chapter and 0 <= page_idx < len(chapter.pages):
                    chapter.goto_page(page_idx)
                else:
                    self.ui.show_message("Invalid page number", "error")
                    time.sleep(1)
            except ValueError:
                self.ui.show_message("Invalid input", "error")
                time.sleep(1)
    
    def search_dialog(self):
        """Show search dialog."""
        if not self.current_reader:
            return
        
        query = self.ui.get_input("Search for:")
        if not query:
            return
        
        results = self.current_reader.search_text(query)
        selected = self.ui.show_search_results(results)
        
        if selected:
            self.current_reader.goto_chapter(selected['chapter_index'])
    
    def auto_save_position(self):
        """Auto-save current reading position immediately after navigation."""
        if not self.current_reader:
            return
        
        position = self.current_reader.get_reading_position()
        
        # Save position without reading time calculation for immediate saves
        self.db.update_reading_progress(
            self.current_reader.file_path,
            position['chapter'],
            position['page'],
            0  # No reading time for auto-saves
        )
    
    def save_progress(self):
        """Save reading progress with reading time."""
        if not self.current_reader:
            return
        
        position = self.current_reader.get_reading_position()
        reading_time = int(time.time() - self.last_save_time)
        
        self.db.update_reading_progress(
            self.current_reader.file_path,
            position['chapter'],
            position['page'],
            reading_time
        )
    
    def start_auto_save(self):
        """Start auto-save timer."""
        self.stop_auto_save()
        
        interval = self.config.get_int('READING', 'auto_save_interval', 30)
        self.auto_save_timer = threading.Timer(interval, self.auto_save_callback)
        self.auto_save_timer.daemon = True
        self.auto_save_timer.start()
    
    def auto_save_callback(self):
        """Auto-save callback."""
        if self.running and self.current_reader:
            self.save_progress()
            self.start_auto_save()  # Schedule next save
    
    def stop_auto_save(self):
        """Stop auto-save timer."""
        if self.auto_save_timer:
            self.auto_save_timer.cancel()
            self.auto_save_timer = None
    
    def cleanup(self):
        """Cleanup resources."""
        self.stop_auto_save()
        if self.current_reader:
            self.save_progress()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='EPUB CLI Reader')
    parser.add_argument('file', nargs='?', help='EPUB file to open')
    parser.add_argument('--version', action='version', version='EPUB Reader 1.0.0')
    
    args = parser.parse_args()
    
    app = EpubReaderApp()
    app.run(args.file)


if __name__ == '__main__':
    main()
