"""
EPUB parsing and reading module.
"""

import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional, Tuple, Any
import html


class Chapter:
    """Represents a chapter in an EPUB book."""
    
    def __init__(self, title: str, content: str, chapter_id: str = ""):
        self.title = title
        self.content = content
        self.chapter_id = chapter_id
        self.pages: List[str] = []
        self.current_page = 0
    
    def paginate(self, page_width: int = 80, page_height: int = 24) -> None:
        """Split chapter content into pages."""
        lines = self.content.split('\n')
        self.pages = []
        current_page_lines = []
        current_line_count = 0
        
        for line in lines:
            # Wrap long lines
            wrapped_lines = self._wrap_line(line, page_width)
            
            for wrapped_line in wrapped_lines:
                if current_line_count >= page_height - 2:  # Leave space for header/footer
                    # Start new page
                    self.pages.append('\n'.join(current_page_lines))
                    current_page_lines = [wrapped_line]
                    current_line_count = 1
                else:
                    current_page_lines.append(wrapped_line)
                    current_line_count += 1
        
        # Add remaining lines as last page
        if current_page_lines:
            self.pages.append('\n'.join(current_page_lines))
        
        # Ensure at least one page
        if not self.pages:
            self.pages = [""]
    
    def _wrap_line(self, line: str, width: int) -> List[str]:
        """Wrap a line to fit within specified width."""
        if len(line) <= width:
            return [line]
        
        words = line.split()
        wrapped_lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + " " + word) <= width:
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word
            else:
                if current_line:
                    wrapped_lines.append(current_line)
                    current_line = word
                else:
                    # Word is longer than width, split it
                    while len(word) > width:
                        wrapped_lines.append(word[:width])
                        word = word[width:]
                    current_line = word
        
        if current_line:
            wrapped_lines.append(current_line)
        
        return wrapped_lines if wrapped_lines else [""]
    
    def get_current_page(self) -> str:
        """Get current page content."""
        if not self.pages:
            return ""
        return self.pages[self.current_page] if self.current_page < len(self.pages) else ""
    
    def next_page(self) -> bool:
        """Move to next page. Returns True if successful."""
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            return True
        return False
    
    def prev_page(self) -> bool:
        """Move to previous page. Returns True if successful."""
        if self.current_page > 0:
            self.current_page -= 1
            return True
        return False
    
    def goto_page(self, page_num: int) -> bool:
        """Go to specific page. Returns True if successful."""
        if 0 <= page_num < len(self.pages):
            self.current_page = page_num
            return True
        return False
    
    def get_page_info(self) -> Dict[str, int]:
        """Get page information."""
        return {
            'current_page': self.current_page + 1,
            'total_pages': len(self.pages),
            'page_index': self.current_page
        }


class EpubReader:
    """EPUB file reader and parser."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.book: Optional[epub.EpubBook] = None
        self.chapters: List[Chapter] = []
        self.current_chapter = 0
        self.title = ""
        self.author = ""
        self.toc: List[Dict[str, Any]] = []
        self._load_book()
    
    def _load_book(self) -> bool:
        """Load EPUB book from file."""
        try:
            self.book = epub.read_epub(self.file_path)
            self._extract_metadata()
            self._extract_chapters()
            self._build_toc()
            return True
        except Exception as e:
            print(f"Error loading EPUB: {e}")
            return False
    
    def _extract_metadata(self) -> None:
        """Extract book metadata."""
        if not self.book:
            return
        
        try:
            # Get title
            title = self.book.get_metadata('DC', 'title')
            self.title = title[0][0] if title else "Unknown Title"
            
            # Get author
            creator = self.book.get_metadata('DC', 'creator')
            self.author = creator[0][0] if creator else "Unknown Author"
            
        except Exception as e:
            print(f"Error extracting metadata: {e}")
            self.title = "Unknown Title"
            self.author = "Unknown Author"
    
    def _extract_chapters(self) -> None:
        """Extract chapters from EPUB."""
        if not self.book:
            return
        
        self.chapters = []
        chapter_num = 0
        
        try:
            # Get all document items
            for item in self.book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    content = item.get_content().decode('utf-8')
                    text_content = self._html_to_text(content)
                    
                    if text_content.strip():  # Only add non-empty chapters
                        chapter_title = self._extract_chapter_title(content) or f"Chapter {chapter_num + 1}"
                        chapter = Chapter(chapter_title, text_content, item.get_id())
                        self.chapters.append(chapter)
                        chapter_num += 1
        
        except Exception as e:
            print(f"Error extracting chapters: {e}")
    
    def _html_to_text(self, html_content: str) -> str:
        """Convert HTML content to plain text."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text and clean it up
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Decode HTML entities
            text = html.unescape(text)
            
            # Add paragraph breaks
            text = re.sub(r'\s*\n\s*\n\s*', '\n\n', text)
            
            return text
        
        except Exception as e:
            print(f"Error converting HTML to text: {e}")
            return ""
    
    def _extract_chapter_title(self, html_content: str) -> Optional[str]:
        """Extract chapter title from HTML content."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for title in various header tags
            for tag in ['h1', 'h2', 'h3', 'title']:
                element = soup.find(tag)
                if element and element.get_text().strip():
                    return element.get_text().strip()
            
            # Look for title in class names
            for class_name in ['title', 'chapter-title', 'heading']:
                element = soup.find(class_=class_name)
                if element and element.get_text().strip():
                    return element.get_text().strip()
            
            return None
        
        except Exception as e:
            print(f"Error extracting chapter title: {e}")
            return None
    
    def _build_toc(self) -> None:
        """Build table of contents."""
        self.toc = []
        
        try:
            if self.book and hasattr(self.book, 'toc'):
                self._process_toc_item(self.book.toc, 0)
            
            # If no TOC found, create one from chapters
            if not self.toc:
                for i, chapter in enumerate(self.chapters):
                    self.toc.append({
                        'title': chapter.title,
                        'chapter_index': i,
                        'level': 0
                    })
        
        except Exception as e:
            print(f"Error building TOC: {e}")
            # Fallback: create simple TOC from chapters
            for i, chapter in enumerate(self.chapters):
                self.toc.append({
                    'title': chapter.title,
                    'chapter_index': i,
                    'level': 0
                })
    
    def _process_toc_item(self, toc_item, level: int) -> None:
        """Process table of contents item recursively."""
        if isinstance(toc_item, list):
            for item in toc_item:
                self._process_toc_item(item, level)
        elif hasattr(toc_item, 'title') and hasattr(toc_item, 'href'):
            # Find corresponding chapter
            chapter_index = self._find_chapter_by_href(toc_item.href)
            if chapter_index is not None:
                self.toc.append({
                    'title': toc_item.title,
                    'chapter_index': chapter_index,
                    'level': level
                })
        elif isinstance(toc_item, tuple) and len(toc_item) >= 2:
            # Handle tuple format (section, children)
            section = toc_item[0]
            children = toc_item[1] if len(toc_item) > 1 else []
            
            if hasattr(section, 'title') and hasattr(section, 'href'):
                chapter_index = self._find_chapter_by_href(section.href)
                if chapter_index is not None:
                    self.toc.append({
                        'title': section.title,
                        'chapter_index': chapter_index,
                        'level': level
                    })
            
            # Process children
            if children:
                for child in children:
                    self._process_toc_item(child, level + 1)
    
    def _find_chapter_by_href(self, href: str) -> Optional[int]:
        """Find chapter index by href."""
        # Remove fragment identifier
        href = href.split('#')[0]
        
        for i, chapter in enumerate(self.chapters):
            if chapter.chapter_id and href.endswith(chapter.chapter_id):
                return i
        
        return None
    
    def paginate_chapters(self, page_width: int = 80, page_height: int = 24) -> None:
        """Paginate all chapters."""
        for chapter in self.chapters:
            chapter.paginate(page_width, page_height)
    
    def get_current_chapter(self) -> Optional[Chapter]:
        """Get current chapter."""
        if 0 <= self.current_chapter < len(self.chapters):
            return self.chapters[self.current_chapter]
        return None
    
    def next_chapter(self) -> bool:
        """Move to next chapter."""
        if self.current_chapter < len(self.chapters) - 1:
            self.current_chapter += 1
            return True
        return False
    
    def prev_chapter(self) -> bool:
        """Move to previous chapter."""
        if self.current_chapter > 0:
            self.current_chapter -= 1
            return True
        return False
    
    def goto_chapter(self, chapter_index: int) -> bool:
        """Go to specific chapter."""
        if 0 <= chapter_index < len(self.chapters):
            self.current_chapter = chapter_index
            # Reset page to 0 when changing chapters
            chapter = self.get_current_chapter()
            if chapter:
                chapter.current_page = 0
            return True
        return False
    
    def get_book_info(self) -> Dict[str, Any]:
        """Get book information."""
        return {
            'title': self.title,
            'author': self.author,
            'total_chapters': len(self.chapters),
            'current_chapter': self.current_chapter,
            'file_path': self.file_path
        }
    
    def get_reading_position(self) -> Dict[str, int]:
        """Get current reading position."""
        chapter = self.get_current_chapter()
        if chapter:
            page_info = chapter.get_page_info()
            return {
                'chapter': self.current_chapter,
                'page': page_info['page_index'],
                'total_chapters': len(self.chapters),
                'total_pages_in_chapter': page_info['total_pages']
            }
        return {
            'chapter': 0,
            'page': 0,
            'total_chapters': len(self.chapters),
            'total_pages_in_chapter': 0
        }
    
    def set_reading_position(self, chapter: int, page: int) -> bool:
        """Set reading position."""
        # Set chapter without resetting page
        if 0 <= chapter < len(self.chapters):
            self.current_chapter = chapter
            current_chapter = self.get_current_chapter()
            if current_chapter:
                return current_chapter.goto_page(page)
        return False
    
    def search_text(self, query: str) -> List[Dict[str, Any]]:
        """Search for text in the book."""
        results = []
        query_lower = query.lower()
        
        for chapter_idx, chapter in enumerate(self.chapters):
            lines = chapter.content.split('\n')
            for line_idx, line in enumerate(lines):
                if query_lower in line.lower():
                    results.append({
                        'chapter_index': chapter_idx,
                        'chapter_title': chapter.title,
                        'line_number': line_idx + 1,
                        'line_content': line.strip(),
                        'context': self._get_search_context(lines, line_idx)
                    })
        
        return results
    
    def _get_search_context(self, lines: List[str], line_idx: int, context_lines: int = 2) -> str:
        """Get context around a search result."""
        start = max(0, line_idx - context_lines)
        end = min(len(lines), line_idx + context_lines + 1)
        context = lines[start:end]
        return '\n'.join(line.strip() for line in context)
