"""
File management module for EPUB files storage and organization.
"""

import os
import shutil
import hashlib
from typing import List, Dict, Optional, Tuple
from pathlib import Path


class FileManager:
    """Manages EPUB file storage and organization."""
    
    def __init__(self, books_directory: str = "data/books"):
        self.books_directory = books_directory
        self._ensure_books_dir()
    
    def _ensure_books_dir(self):
        """Ensure books directory exists."""
        os.makedirs(self.books_directory, exist_ok=True)
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate MD5 hash of a file."""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except IOError as e:
            print(f"Error calculating hash for {file_path}: {e}")
            return ""
    
    def _get_safe_filename(self, title: str, author: str = "") -> str:
        """Generate a safe filename from title and author."""
        # Remove invalid characters for filename
        invalid_chars = '<>:"/\\|?*'
        safe_title = ''.join(c for c in title if c not in invalid_chars)
        safe_author = ''.join(c for c in author if c not in invalid_chars)
        
        # Limit length
        safe_title = safe_title[:50].strip()
        safe_author = safe_author[:30].strip()
        
        if safe_author:
            filename = f"{safe_author} - {safe_title}"
        else:
            filename = safe_title
        
        # Replace spaces with underscores and ensure it's not empty
        filename = filename.replace(' ', '_')
        if not filename:
            filename = "unknown_book"
        
        return filename + ".epub"
    
    def add_book(self, source_path: str, title: str, author: str = "") -> Optional[str]:
        """
        Add a book to the library by copying it to the books directory.
        Returns the new file path if successful, None otherwise.
        """
        if not os.path.exists(source_path):
            print(f"Source file does not exist: {source_path}")
            return None
        
        if not source_path.lower().endswith('.epub'):
            print(f"File is not an EPUB: {source_path}")
            return None
        
        try:
            # Calculate hash to check for duplicates
            file_hash = self._calculate_file_hash(source_path)
            if not file_hash:
                return None
            
            # Check if file already exists (by hash)
            existing_file = self._find_file_by_hash(file_hash)
            if existing_file:
                print(f"Book already exists in library: {existing_file}")
                return existing_file
            
            # Generate safe filename
            safe_filename = self._get_safe_filename(title, author)
            target_path = os.path.join(self.books_directory, safe_filename)
            
            # Handle filename conflicts
            counter = 1
            original_target = target_path
            while os.path.exists(target_path):
                name, ext = os.path.splitext(original_target)
                target_path = f"{name}_{counter}{ext}"
                counter += 1
            
            # Copy file
            shutil.copy2(source_path, target_path)
            
            # Store hash for future duplicate detection
            self._store_file_hash(target_path, file_hash)
            
            print(f"Book added to library: {target_path}")
            return target_path
            
        except Exception as e:
            print(f"Error adding book to library: {e}")
            return None
    
    def _find_file_by_hash(self, file_hash: str) -> Optional[str]:
        """Find a file in the library by its hash."""
        hash_file = os.path.join(self.books_directory, ".hashes")
        if not os.path.exists(hash_file):
            return None
        
        try:
            with open(hash_file, 'r') as f:
                for line in f:
                    stored_hash, file_path = line.strip().split(':', 1)
                    if stored_hash == file_hash and os.path.exists(file_path):
                        return file_path
        except Exception as e:
            print(f"Error reading hash file: {e}")
        
        return None
    
    def _store_file_hash(self, file_path: str, file_hash: str):
        """Store file hash for duplicate detection."""
        hash_file = os.path.join(self.books_directory, ".hashes")
        try:
            with open(hash_file, 'a') as f:
                f.write(f"{file_hash}:{file_path}\n")
        except Exception as e:
            print(f"Error storing file hash: {e}")
    
    def remove_book(self, file_path: str) -> bool:
        """Remove a book from the library."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                self._remove_file_hash(file_path)
                print(f"Book removed from library: {file_path}")
                return True
            else:
                print(f"File not found: {file_path}")
                return False
        except Exception as e:
            print(f"Error removing book: {e}")
            return False
    
    def _remove_file_hash(self, file_path: str):
        """Remove file hash entry."""
        hash_file = os.path.join(self.books_directory, ".hashes")
        if not os.path.exists(hash_file):
            return
        
        try:
            lines = []
            with open(hash_file, 'r') as f:
                lines = f.readlines()
            
            with open(hash_file, 'w') as f:
                for line in lines:
                    if not line.strip().endswith(f":{file_path}"):
                        f.write(line)
        except Exception as e:
            print(f"Error removing file hash: {e}")
    
    def list_books(self) -> List[str]:
        """List all EPUB files in the library."""
        try:
            epub_files = []
            for file in os.listdir(self.books_directory):
                if file.lower().endswith('.epub'):
                    epub_files.append(os.path.join(self.books_directory, file))
            return sorted(epub_files)
        except Exception as e:
            print(f"Error listing books: {e}")
            return []
    
    def get_book_info(self, file_path: str) -> Dict[str, str]:
        """Get basic information about a book file."""
        try:
            if not os.path.exists(file_path):
                return {}
            
            stat = os.stat(file_path)
            return {
                'file_path': file_path,
                'filename': os.path.basename(file_path),
                'size': str(stat.st_size),
                'modified': str(stat.st_mtime),
                'created': str(stat.st_ctime)
            }
        except Exception as e:
            print(f"Error getting book info: {e}")
            return {}
    
    def validate_epub(self, file_path: str) -> bool:
        """Basic validation of EPUB file."""
        try:
            if not os.path.exists(file_path):
                return False
            
            if not file_path.lower().endswith('.epub'):
                return False
            
            # Check if file is readable and has content
            with open(file_path, 'rb') as f:
                # Read first few bytes to check if it's a ZIP file (EPUB is ZIP-based)
                header = f.read(4)
                if header[:2] != b'PK':  # ZIP file signature
                    return False
            
            return True
        except Exception as e:
            print(f"Error validating EPUB: {e}")
            return False
    
    def get_library_stats(self) -> Dict[str, int]:
        """Get statistics about the library."""
        try:
            books = self.list_books()
            total_size = 0
            
            for book in books:
                try:
                    total_size += os.path.getsize(book)
                except OSError:
                    continue
            
            return {
                'total_books': len(books),
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2)
            }
        except Exception as e:
            print(f"Error getting library stats: {e}")
            return {'total_books': 0, 'total_size_bytes': 0, 'total_size_mb': 0}
    
    def cleanup_library(self) -> int:
        """Clean up library by removing invalid files and updating hashes."""
        removed_count = 0
        try:
            books = self.list_books()
            for book in books:
                if not self.validate_epub(book):
                    if self.remove_book(book):
                        removed_count += 1
            
            # Clean up hash file
            self._cleanup_hash_file()
            
            return removed_count
        except Exception as e:
            print(f"Error during library cleanup: {e}")
            return removed_count
    
    def _cleanup_hash_file(self):
        """Clean up hash file by removing entries for non-existent files."""
        hash_file = os.path.join(self.books_directory, ".hashes")
        if not os.path.exists(hash_file):
            return
        
        try:
            valid_lines = []
            with open(hash_file, 'r') as f:
                for line in f:
                    if ':' in line:
                        _, file_path = line.strip().split(':', 1)
                        if os.path.exists(file_path):
                            valid_lines.append(line)
            
            with open(hash_file, 'w') as f:
                f.writelines(valid_lines)
        except Exception as e:
            print(f"Error cleaning up hash file: {e}")
    
    def search_books(self, query: str) -> List[str]:
        """Search for books by filename."""
        try:
            query = query.lower()
            books = self.list_books()
            matching_books = []
            
            for book in books:
                filename = os.path.basename(book).lower()
                if query in filename:
                    matching_books.append(book)
            
            return matching_books
        except Exception as e:
            print(f"Error searching books: {e}")
            return []
