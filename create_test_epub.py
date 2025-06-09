#!/usr/bin/env python3
"""
Create a test EPUB file for testing the reader.
"""

import os
import zipfile
import tempfile


def create_test_epub(output_path="test_book.epub"):
    """Create a simple test EPUB file."""
    
    # Create EPUB structure
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as epub:
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
    <dc:title>Test EPUB Book</dc:title>
    <dc:creator>Test Author</dc:creator>
    <dc:identifier id="BookId">test-book-123</dc:identifier>
    <dc:language>en</dc:language>
  </metadata>
  <manifest>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
    <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
    <item id="chapter2" href="chapter2.xhtml" media-type="application/xhtml+xml"/>
    <item id="chapter3" href="chapter3.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine toc="ncx">
    <itemref idref="chapter1"/>
    <itemref idref="chapter2"/>
    <itemref idref="chapter3"/>
  </spine>
</package>'''
        epub.writestr("OEBPS/content.opf", content_opf)
        
        # Add toc.ncx
        toc_ncx = '''<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="test-book-123"/>
  </head>
  <docTitle>
    <text>Test EPUB Book</text>
  </docTitle>
  <navMap>
    <navPoint id="navpoint-1" playOrder="1">
      <navLabel><text>Chapter 1: Getting Started</text></navLabel>
      <content src="chapter1.xhtml"/>
    </navPoint>
    <navPoint id="navpoint-2" playOrder="2">
      <navLabel><text>Chapter 2: Navigation</text></navLabel>
      <content src="chapter2.xhtml"/>
    </navPoint>
    <navPoint id="navpoint-3" playOrder="3">
      <navLabel><text>Chapter 3: Features</text></navLabel>
      <content src="chapter3.xhtml"/>
    </navPoint>
  </navMap>
</ncx>'''
        epub.writestr("OEBPS/toc.ncx", toc_ncx)
        
        # Add chapter 1
        chapter1 = '''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>Chapter 1: Getting Started</title>
</head>
<body>
    <h1>Chapter 1: Getting Started</h1>
    <p>Welcome to the EPUB CLI Reader test book! This chapter will help you get familiar with the basic navigation controls.</p>
    
    <h2>Basic Navigation</h2>
    <p>Use the following keys to navigate through the book:</p>
    <ul>
        <li><strong>↓ (Down Arrow)</strong> or <strong>J</strong> or <strong>Space</strong> - Next page</li>
        <li><strong>↑ (Up Arrow)</strong> or <strong>K</strong> - Previous page</li>
        <li><strong>→ (Right Arrow)</strong> or <strong>L</strong> - Next chapter</li>
        <li><strong>← (Left Arrow)</strong> or <strong>H</strong> - Previous chapter</li>
    </ul>
    
    <p>This is a longer paragraph to test the pagination functionality. The text should wrap properly and be divided into pages based on your terminal size and the configured page dimensions. You can adjust these settings by pressing 'S' to open the settings menu.</p>
    
    <p>Try navigating to the next page using the Down arrow key or pressing J. You should see the next portion of this chapter.</p>
    
    <p>When you reach the end of this chapter, try using the Right arrow key or pressing L to move to the next chapter.</p>
    
    <h2>Additional Features</h2>
    <p>Press 'T' to open the Table of Contents, where you can jump directly to any chapter.</p>
    <p>Press 'B' to add a bookmark at your current reading position.</p>
    <p>Press 'Q' to quit the reader.</p>
</body>
</html>'''
        epub.writestr("OEBPS/chapter1.xhtml", chapter1)
        
        # Add chapter 2
        chapter2 = '''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>Chapter 2: Navigation</title>
</head>
<body>
    <h1>Chapter 2: Navigation</h1>
    <p>Great! You've successfully navigated to Chapter 2. This demonstrates that the chapter navigation is working correctly.</p>
    
    <h2>Testing Arrow Keys</h2>
    <p>If you're reading this, it means the arrow key navigation has been fixed and is working properly. You can now use:</p>
    
    <ul>
        <li>↑/↓ arrows for page navigation</li>
        <li>←/→ arrows for chapter navigation</li>
    </ul>
    
    <p>This chapter contains multiple pages to test the pagination system. Keep pressing the down arrow or 'J' to see more content.</p>
    
    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
    
    <p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>
    
    <p>Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.</p>
    
    <h2>Bookmarks</h2>
    <p>Try adding a bookmark here by pressing 'B'. You can add an optional note to remember why you bookmarked this location.</p>
    
    <p>Later, you can view all your bookmarks by pressing Shift+B.</p>
</body>
</html>'''
        epub.writestr("OEBPS/chapter2.xhtml", chapter2)
        
        # Add chapter 3
        chapter3 = '''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>Chapter 3: Features</title>
</head>
<body>
    <h1>Chapter 3: Features</h1>
    <p>Welcome to the final chapter! This chapter showcases additional features of the EPUB reader.</p>
    
    <h2>Search Functionality</h2>
    <p>Press '/' to search for text within the book. Try searching for "navigation" or "bookmark" to see how the search feature works.</p>
    
    <h2>Settings</h2>
    <p>Press 'S' to open the settings menu where you can customize:</p>
    <ul>
        <li>Font size</li>
        <li>Line spacing</li>
        <li>Page width and height</li>
        <li>Auto-save interval</li>
    </ul>
    
    <h2>Library Management</h2>
    <p>All books you open are automatically added to your personal library. Press 'L' to view your library and quickly access recently read books.</p>
    
    <h2>Progress Tracking</h2>
    <p>Your reading progress is automatically saved. When you reopen this book, you'll return to exactly where you left off.</p>
    
    <h2>Help</h2>
    <p>Press '?' at any time to view the help screen with all available keyboard shortcuts.</p>
    
    <p>Thank you for testing the EPUB CLI Reader! We hope you enjoy using it for your reading needs.</p>
    
    <p>Press 'Q' to quit the reader when you're done exploring.</p>
</body>
</html>'''
        epub.writestr("OEBPS/chapter3.xhtml", chapter3)
    
    print(f"✅ Test EPUB created: {output_path}")
    return output_path


if __name__ == '__main__':
    create_test_epub()
