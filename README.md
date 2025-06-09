# EPUB CLI Reader

A feature-rich command-line EPUB reader with file management, reading progress tracking, and customizable display settings.

## Features

### 📚 Reading Experience
- Clean, distraction-free CLI interface
- Automatic text pagination with customizable page size
- Chapter navigation with table of contents
- Keyboard shortcuts for efficient navigation
- Search functionality within books
- Bookmark system with optional notes

### 💾 File Management
- Automatic library management
- Duplicate detection and prevention
- File validation and integrity checking
- Organized storage in dedicated directory

### 📊 Progress Tracking
- Automatic reading progress saving
- Resume reading from last position
- Reading time tracking
- Recent books quick access

### ⚙️ Customization
- Adjustable font size and line spacing
- Configurable page dimensions
- Auto-save interval settings
- Persistent user preferences

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd epubCli
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Make the script executable (optional):
```bash
chmod +x main.py
```

## Usage

### Basic Usage

Start the application:
```bash
python main.py
```

Open a specific EPUB file:
```bash
python main.py /path/to/book.epub
```

### Keyboard Controls

#### Reading Navigation
- `↑/K/PgUp` - Previous page
- `↓/J/PgDn` - Next page
- `←/H` - Previous chapter
- `→/L` - Next chapter

#### Menu Navigation
- `T` - Table of contents
- `G` - Go to specific page/chapter
- `/` - Search in book
- `B` - Toggle bookmark
- `Shift+B` - Show bookmarks
- `S` - Settings
- `L` - Library
- `O` - Open file
- `Q/Esc` - Quit
- `?` - Help

### Main Menu Options

- **O** - Open EPUB file browser
- **L** - View library of saved books
- **S** - Adjust settings
- **H** - Show help
- **Q** - Quit application
- **1-5** - Quick access to recent books

## Project Structure

```
epubCli/
├── main.py                 # Main application entry point
├── src/
│   ├── __init__.py
│   ├── database.py         # SQLite database management
│   ├── config_manager.py   # Configuration handling
│   ├── file_manager.py     # File operations and library management
│   ├── epub_reader.py      # EPUB parsing and content extraction
│   └── ui_manager.py       # User interface using Rich library
├── data/
│   ├── books/             # EPUB file storage
│   ├── config.ini         # User configuration
│   └── reading_history.db # Reading progress database
├── requirements.txt
└── README.md
```

## Configuration

The application creates a `data/config.ini` file with default settings:

### Display Settings
- `font_size`: Text size (8-72)
- `line_spacing`: Line height multiplier (0.5-3.0)
- `page_width`: Characters per line (40-120)
- `page_height`: Lines per page (10-50)
- `theme`: Display theme

### Reading Settings
- `auto_save_interval`: Progress save frequency in seconds
- `show_progress`: Display reading progress
- `wrap_text`: Enable text wrapping
- `show_chapter_title`: Show chapter titles

### File Settings
- `books_directory`: Library storage location
- `max_recent_books`: Number of recent books to track
- `auto_backup`: Enable automatic backups

## Database Schema

The application uses SQLite to store:

### Reading History
- Book metadata (title, author, file path)
- Reading progress (current chapter, page position)
- Reading time tracking
- Last access timestamps

### Bookmarks
- Position information (chapter, page)
- Optional user notes
- Creation timestamps

### Settings
- User preferences
- Configuration overrides

## Dependencies

- `ebooklib`: EPUB file parsing
- `rich`: Terminal UI and formatting
- `beautifulsoup4`: HTML content processing
- `lxml`: XML parsing
- `keyboard`: Keyboard input handling (optional)

## Error Handling

The application includes comprehensive error handling for:
- Invalid EPUB files
- Corrupted or missing files
- Database connection issues
- Configuration file problems
- User input validation

## Performance Considerations

- Lazy loading of chapter content
- Efficient text pagination algorithms
- Minimal memory footprint
- Fast startup times
- Responsive user interface

## Troubleshooting

### Common Issues

1. **EPUB file won't open**
   - Verify file is a valid EPUB format
   - Check file permissions
   - Ensure file is not corrupted

2. **Settings not saving**
   - Check write permissions in data directory
   - Verify config file is not read-only

3. **Database errors**
   - Delete `data/reading_history.db` to reset
   - Check disk space availability

4. **Display issues**
   - Adjust terminal size
   - Modify page dimensions in settings
   - Check terminal color support

### Debug Mode

Run with Python's verbose mode for debugging:
```bash
python -v main.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Rich](https://github.com/Textualize/rich) for beautiful terminal output
- Uses [ebooklib](https://github.com/aerkalov/ebooklib) for EPUB parsing
- Inspired by various CLI reading applications

## Version History

### v1.0.0
- Initial release
- Basic EPUB reading functionality
- File management and library system
- Progress tracking and bookmarks
- Customizable display settings
- Comprehensive keyboard navigation
