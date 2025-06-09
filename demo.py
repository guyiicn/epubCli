#!/usr/bin/env python3
"""
Demo script for EPUB Reader application.
"""

import os
import sys
import tempfile
import zipfile
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database import Database
from src.config_manager import ConfigManager
from src.file_manager import FileManager
from src.epub_reader import Chapter


def create_sample_epub():
    """Create a sample EPUB file for demonstration."""
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    epub_path = os.path.join(temp_dir, "sample_book.epub")
    
    # Create EPUB structure
    with zipfile.ZipFile(epub_path, 'w', zipfile.ZIP_DEFLATED) as epub:
        # Add mimetype
        epub.writestr("mimetype", "application/epub+zip")
        
        # Add META-INF/container.xml
        container_xml = '''<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>'''
        epub.writestr("META-INF/container.xml", container_xml)
        
        # Add content.opf
        content_opf = '''<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookId" version="2.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
    <dc:title>Sample EPUB Book</dc:title>
    <dc:creator>Demo Author</dc:creator>
    <dc:identifier id="BookId">sample-book-123</dc:identifier>
    <dc:language>en</dc:language>
  </metadata>
  <manifest>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
    <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
    <item id="chapter2" href="chapter2.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine toc="ncx">
    <itemref idref="chapter1"/>
    <itemref idref="chapter2"/>
  </spine>
</package>'''
        epub.writestr("OEBPS/content.opf", content_opf)
        
        # Add toc.ncx
        toc_ncx = '''<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="sample-book-123"/>
  </head>
  <docTitle>
    <text>Sample EPUB Book</text>
  </docTitle>
  <navMap>
    <navPoint id="navpoint-1" playOrder="1">
      <navLabel><text>Chapter 1</text></navLabel>
      <content src="chapter1.xhtml"/>
    </navPoint>
    <navPoint id="navpoint-2" playOrder="2">
      <navLabel><text>Chapter 2</text></navLabel>
      <content src="chapter2.xhtml"/>
    </navPoint>
  </navMap>
</ncx>'''
        epub.writestr("OEBPS/toc.ncx", toc_ncx)
        
        # Add chapter 1
        chapter1 = '''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>Chapter 1</title>
</head>
<body>
    <h1>Chapter 1: Introduction</h1>
    <p>Welcome to this sample EPUB book! This is a demonstration of the EPUB CLI Reader application.</p>
    <p>This chapter contains some sample text to show how the reader handles pagination and text formatting.</p>
    <p>The EPUB format is widely used for digital books and supports rich text formatting, images, and interactive content.</p>
    <p>Our CLI reader focuses on providing a clean, distraction-free reading experience in the terminal.</p>
    <p>You can navigate through pages using keyboard shortcuts, bookmark important sections, and customize the display settings to your preference.</p>
</body>
</html>'''
        epub.writestr("OEBPS/chapter1.xhtml", chapter1)
        
        # Add chapter 2
        chapter2 = '''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>Chapter 2</title>
</head>
<body>
    <h1>Chapter 2: Features</h1>
    <p>This EPUB reader includes many useful features:</p>
    <ul>
        <li>Automatic library management</li>
        <li>Reading progress tracking</li>
        <li>Bookmark system with notes</li>
        <li>Customizable display settings</li>
        <li>Search functionality</li>
        <li>Table of contents navigation</li>
    </ul>
    <p>The application automatically saves your reading progress and allows you to resume where you left off.</p>
    <p>You can adjust font size, line spacing, and page dimensions to create the perfect reading experience.</p>
    <p>All your books are organized in a personal library with easy access to recently read titles.</p>
</body>
</html>'''
        epub.writestr("OEBPS/chapter2.xhtml", chapter2)
    
    return epub_path


def demo_database():
    """Demonstrate database functionality."""
    print("🗄️  Database Demo")
    print("=" * 40)
    
    # Create temporary database
    db_path = tempfile.mktemp(suffix='.db')
    db = Database(db_path)
    
    # Add sample books
    print("Adding sample books to database...")
    db.add_or_update_book("book1.epub", "The Great Gatsby", "F. Scott Fitzgerald", 9)
    db.add_or_update_book("book2.epub", "To Kill a Mockingbird", "Harper Lee", 31)
    db.add_or_update_book("book3.epub", "1984", "George Orwell", 24)
    
    # Update reading progress
    print("Updating reading progress...")
    db.update_reading_progress("book1.epub", 3, 150, 45)
    db.update_reading_progress("book2.epub", 15, 200, 120)
    
    # Add bookmarks
    print("Adding bookmarks...")
    db.add_bookmark("book1.epub", 2, 100, "Important quote about the green light")
    db.add_bookmark("book2.epub", 10, 50, "Atticus's advice to Scout")
    
    # Get recent books
    print("\nRecent books:")
    recent_books = db.get_recent_books(5)
    for book in recent_books:
        progress = f"{book['current_chapter'] + 1}/{book['total_chapters']}"
        print(f"  📖 {book['title']} by {book['author']} ({progress})")
    
    # Get bookmarks
    print(f"\nBookmarks for {recent_books[0]['title']}:")
    bookmarks = db.get_bookmarks(recent_books[0]['file_path'])
    for bookmark in bookmarks:
        print(f"  🔖 Chapter {bookmark['chapter'] + 1}: {bookmark['note']}")
    
    # Cleanup
    os.remove(db_path)
    print("✅ Database demo completed!\n")


def demo_config():
    """Demonstrate configuration management."""
    print("⚙️  Configuration Demo")
    print("=" * 40)
    
    # Create temporary config
    config_path = tempfile.mktemp(suffix='.ini')
    config = ConfigManager(config_path)
    
    # Show default settings
    print("Default display settings:")
    display_settings = config.get_display_settings()
    for key, value in display_settings.items():
        print(f"  {key}: {value}")
    
    # Update settings
    print("\nUpdating settings...")
    new_settings = {
        'font_size': 14,
        'line_spacing': 1.5,
        'page_width': 100,
        'page_height': 30
    }
    config.set_display_settings(new_settings)
    
    # Show updated settings
    print("Updated display settings:")
    display_settings = config.get_display_settings()
    for key, value in display_settings.items():
        print(f"  {key}: {value}")
    
    # Show control keys
    print("\nKeyboard controls:")
    controls = config.get_control_keys()
    for action, keys in controls.items():
        print(f"  {action}: {', '.join(keys)}")
    
    # Cleanup
    os.remove(config_path)
    print("✅ Configuration demo completed!\n")


def demo_file_manager():
    """Demonstrate file management."""
    print("📁 File Manager Demo")
    print("=" * 40)
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    file_manager = FileManager(temp_dir)
    
    # Create sample EPUB
    print("Creating sample EPUB file...")
    sample_epub = create_sample_epub()
    
    # Add book to library
    print("Adding book to library...")
    library_path = file_manager.add_book(sample_epub, "Sample EPUB Book", "Demo Author")
    if library_path:
        print(f"  ✅ Book added: {os.path.basename(library_path)}")
    
    # List books in library
    print("\nBooks in library:")
    books = file_manager.list_books()
    for book in books:
        print(f"  📖 {os.path.basename(book)}")
    
    # Get library statistics
    print("\nLibrary statistics:")
    stats = file_manager.get_library_stats()
    print(f"  Total books: {stats['total_books']}")
    print(f"  Total size: {stats['total_size_mb']} MB")
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)
    os.remove(sample_epub)
    print("✅ File manager demo completed!\n")


def demo_chapter():
    """Demonstrate chapter functionality."""
    print("📄 Chapter Demo")
    print("=" * 40)
    
    # Create sample chapter
    content = """This is a sample chapter with multiple paragraphs to demonstrate the pagination functionality of the EPUB reader.

The chapter class handles text wrapping and pagination automatically based on the configured page dimensions.

You can navigate through pages using keyboard shortcuts, and the reader will remember your current position.

This paragraph contains enough text to show how long lines are wrapped to fit within the specified page width, ensuring optimal readability.

The pagination algorithm takes into account line spacing and page height to create properly formatted pages that are easy to read in the terminal environment."""
    
    chapter = Chapter("Sample Chapter", content)
    
    # Paginate chapter
    print("Paginating chapter with 40 characters width and 8 lines height...")
    chapter.paginate(page_width=40, page_height=8)
    
    print(f"Chapter divided into {len(chapter.pages)} pages")
    
    # Show first page
    print("\nFirst page content:")
    print("-" * 40)
    print(chapter.get_current_page())
    print("-" * 40)
    
    # Show page info
    page_info = chapter.get_page_info()
    print(f"Page {page_info['current_page']} of {page_info['total_pages']}")
    
    # Navigate to next page
    if chapter.next_page():
        print("\nSecond page content:")
        print("-" * 40)
        print(chapter.get_current_page())
        print("-" * 40)
        page_info = chapter.get_page_info()
        print(f"Page {page_info['current_page']} of {page_info['total_pages']}")
    
    print("✅ Chapter demo completed!\n")


def main():
    """Run all demonstrations."""
    print("🎉 EPUB CLI Reader - Feature Demonstration")
    print("=" * 50)
    print()
    
    try:
        demo_database()
        demo_config()
        demo_file_manager()
        demo_chapter()
        
        print("🎊 All demos completed successfully!")
        print("\nTo start using the EPUB reader:")
        print("  python main.py                    # Start with main menu")
        print("  python main.py book.epub          # Open specific book")
        print("  python main.py --help             # Show help")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
