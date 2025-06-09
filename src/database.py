"""
Database module for managing reading history and bookmarks.
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any


class Database:
    """Manages SQLite database for reading history and bookmarks."""
    
    def __init__(self, db_path: str = "data/reading_history.db"):
        self.db_path = db_path
        self._ensure_data_dir()
        self._init_database()
    
    def _ensure_data_dir(self):
        """Ensure data directory exists."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def _init_database(self):
        """Initialize database tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Reading history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reading_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    author TEXT,
                    current_chapter INTEGER DEFAULT 0,
                    current_position INTEGER DEFAULT 0,
                    total_chapters INTEGER DEFAULT 0,
                    last_read TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    reading_time INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Bookmarks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bookmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    chapter INTEGER NOT NULL,
                    position INTEGER NOT NULL,
                    note TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (file_path) REFERENCES reading_history (file_path)
                )
            ''')
            
            # Settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def add_or_update_book(self, file_path: str, title: str, author: str = "", 
                          total_chapters: int = 0) -> bool:
        """Add a new book or update existing book information."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if book already exists
                cursor.execute('SELECT id FROM reading_history WHERE file_path = ?', (file_path,))
                exists = cursor.fetchone()
                
                if exists:
                    # Update existing book, preserve reading progress
                    cursor.execute('''
                        UPDATE reading_history 
                        SET title = ?, author = ?, total_chapters = ?, last_read = ?
                        WHERE file_path = ?
                    ''', (title, author, total_chapters, datetime.now(), file_path))
                else:
                    # Insert new book
                    cursor.execute('''
                        INSERT INTO reading_history 
                        (file_path, title, author, total_chapters, last_read)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (file_path, title, author, total_chapters, datetime.now()))
                
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
    
    def update_reading_progress(self, file_path: str, chapter: int, 
                              position: int, reading_time: int = 0) -> bool:
        """Update reading progress for a book."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE reading_history 
                    SET current_chapter = ?, current_position = ?, 
                        reading_time = reading_time + ?, last_read = ?
                    WHERE file_path = ?
                ''', (chapter, position, reading_time, datetime.now(), file_path))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
    
    def get_reading_progress(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get reading progress for a book."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT current_chapter, current_position, reading_time, last_read
                    FROM reading_history WHERE file_path = ?
                ''', (file_path,))
                result = cursor.fetchone()
                if result:
                    return {
                        'chapter': result[0],
                        'position': result[1],
                        'reading_time': result[2],
                        'last_read': result[3]
                    }
                return None
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
    
    def get_recent_books(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recently read books."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT file_path, title, author, current_chapter, 
                           total_chapters, last_read, reading_time
                    FROM reading_history 
                    ORDER BY last_read DESC 
                    LIMIT ?
                ''', (limit,))
                results = cursor.fetchall()
                return [
                    {
                        'file_path': row[0],
                        'title': row[1],
                        'author': row[2],
                        'current_chapter': row[3],
                        'total_chapters': row[4],
                        'last_read': row[5],
                        'reading_time': row[6]
                    }
                    for row in results
                ]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
    
    def add_bookmark(self, file_path: str, chapter: int, position: int, 
                    note: str = "") -> bool:
        """Add a bookmark."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO bookmarks (file_path, chapter, position, note)
                    VALUES (?, ?, ?, ?)
                ''', (file_path, chapter, position, note))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
    
    def get_bookmarks(self, file_path: str) -> List[Dict[str, Any]]:
        """Get bookmarks for a book."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, chapter, position, note, created_at
                    FROM bookmarks WHERE file_path = ?
                    ORDER BY chapter, position
                ''', (file_path,))
                results = cursor.fetchall()
                return [
                    {
                        'id': row[0],
                        'chapter': row[1],
                        'position': row[2],
                        'note': row[3],
                        'created_at': row[4]
                    }
                    for row in results
                ]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
    
    def delete_bookmark(self, bookmark_id: int) -> bool:
        """Delete a bookmark."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM bookmarks WHERE id = ?', (bookmark_id,))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
    
    def get_setting(self, key: str, default: str = "") -> str:
        """Get a setting value."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
                result = cursor.fetchone()
                return result[0] if result else default
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return default
    
    def set_setting(self, key: str, value: str) -> bool:
        """Set a setting value."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO settings (key, value, updated_at)
                    VALUES (?, ?, ?)
                ''', (key, value, datetime.now()))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
    
    def get_all_books(self) -> List[Dict[str, Any]]:
        """Get all books in the library."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT file_path, title, author, current_chapter, 
                           total_chapters, last_read, reading_time
                    FROM reading_history 
                    ORDER BY title
                ''')
                results = cursor.fetchall()
                return [
                    {
                        'file_path': row[0],
                        'title': row[1],
                        'author': row[2],
                        'current_chapter': row[3],
                        'total_chapters': row[4],
                        'last_read': row[5],
                        'reading_time': row[6]
                    }
                    for row in results
                ]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
