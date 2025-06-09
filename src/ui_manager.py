"""
User interface management module using Rich library.
"""

import os
import sys
import time
import termios
import tty
import select
from typing import Dict, List, Optional, Any, Callable
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.layout import Layout
from rich.live import Live
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from rich.align import Align
import threading
import queue


class UIManager:
    """Manages the user interface using Rich library."""
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.console = Console()
        self.layout = Layout()
        self.current_screen = "main"
        self.status_message = ""
        self.key_handlers: Dict[str, Callable] = {}
        self.running = False
        self.input_queue = queue.Queue()
        
        # Get display settings
        display_settings = self.config.get_display_settings()
        self.page_width = display_settings['page_width']
        self.page_height = display_settings['page_height']
        
        self._setup_layout()
    
    def _setup_layout(self):
        """Setup the main layout structure."""
        self.layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
    
    def clear_screen(self):
        """Clear the terminal screen."""
        # Use ANSI escape codes for smoother clearing
        if os.name == 'posix':
            # Move cursor to top-left and clear screen
            sys.stdout.write('\033[2J\033[H')
            sys.stdout.flush()
        else:
            os.system('cls')
    
    def show_header(self, title: str, subtitle: str = "", progress: str = "") -> Panel:
        """Create header panel."""
        header_text = Text(title, style="bold blue")
        if subtitle:
            header_text.append(f"\n{subtitle}", style="dim")
        if progress:
            header_text.append(f" | {progress}", style="green")
        
        return Panel(
            Align.center(header_text),
            box=box.ROUNDED,
            style="blue"
        )
    
    def show_footer(self, controls: Dict[str, str]) -> Panel:
        """Create footer panel with controls."""
        control_text = Text()
        for i, (key, action) in enumerate(controls.items()):
            if i > 0:
                control_text.append(" | ", style="dim")
            control_text.append(f"{key}", style="bold")
            control_text.append(f":{action}", style="dim")
        
        return Panel(
            Align.center(control_text),
            box=box.ROUNDED,
            style="dim"
        )
    
    def show_reading_view(self, book_title: str, author: str, chapter_title: str,
                         content: str, chapter_info: str, page_info: str) -> None:
        """Display the main reading view with smooth transitions."""
        # Header
        header = self.show_header(
            f"📖 {book_title}",
            f"by {author} - {chapter_title}",
            f"{chapter_info} | {page_info}"
        )
        
        # Get current display settings
        display_settings = self.config.get_display_settings()
        font_size = display_settings.get('font_size', 12)
        line_spacing = display_settings.get('line_spacing', 1.2)
        
        # Apply font size and line spacing to content
        formatted_content = self._apply_display_settings(content, font_size, line_spacing)
        
        # Main content with applied settings
        content_panel = Panel(
            formatted_content,
            box=box.ROUNDED,
            style="white",
            padding=(1, 2)
        )
        
        # Footer with controls
        controls = {
            "↑/↓": "Page",
            "←/→": "Chapter", 
            "T": "TOC",
            "B": "Bookmark",
            "S": "Settings",
            "Q": "Quit"
        }
        footer = self.show_footer(controls)
        
        # Update layout
        self.layout["header"].update(header)
        self.layout["main"].update(content_panel)
        self.layout["footer"].update(footer)
        
        # Use smooth screen update
        self.smooth_display_update()
    
    def _apply_display_settings(self, content: str, font_size: int, line_spacing: float) -> Text:
        """Apply display settings (font size and line spacing) to content."""
        # Create Rich Text object for advanced formatting
        text = Text()
        
        # Split content into lines
        lines = content.split('\n')
        
        # Apply font size simulation through character spacing and formatting
        # Since terminal can't change actual font size, we simulate it through:
        # 1. Character spacing for larger fonts
        # 2. Text compression for smaller fonts
        # 3. Style changes for visual emphasis
        
        font_style = "white"
        char_spacing = ""
        
        if font_size >= 20:
            # Very large font: character spacing only (no bright background)
            font_style = "white"
            char_spacing = " "  # Add space between characters
        elif font_size >= 16:
            # Large font: normal white
            font_style = "white"
        elif font_size >= 12:
            # Normal font: default
            font_style = "white"
        elif font_size >= 10:
            # Small font: slightly dim
            font_style = "dim white"
        else:
            # Very small font: very dim + compressed
            font_style = "dim"
        
        # Apply line spacing by adding extra newlines
        extra_lines = max(0, int((line_spacing - 1.0) * 2))  # Convert spacing to extra lines
        
        for i, line in enumerate(lines):
            # Apply character spacing for larger fonts
            if char_spacing and font_size >= 20:
                # Add spacing between characters for "larger" appearance
                spaced_line = char_spacing.join(line)
                text.append(spaced_line, style=font_style)
            elif font_size < 10:
                # For very small fonts, we could compress by removing some spaces
                compressed_line = line.replace('  ', ' ')  # Reduce double spaces
                text.append(compressed_line, style=font_style)
            else:
                # Normal display
                text.append(line, style=font_style)
            
            # Add line spacing (except for the last line)
            if i < len(lines) - 1:
                text.append('\n')
                # Add extra newlines for line spacing
                for _ in range(extra_lines):
                    text.append('\n')
        
        return text
    
    def smooth_display_update(self):
        """Smooth display update with reduced flicker."""
        # Hide cursor during update
        if os.name == 'posix':
            sys.stdout.write('\033[?25l')  # Hide cursor
            sys.stdout.flush()
        
        # Clear and redraw
        self.clear_screen()
        self.console.print(self.layout)
        
        # Show cursor again
        if os.name == 'posix':
            sys.stdout.write('\033[?25h')  # Show cursor
            sys.stdout.flush()
    
    def show_table_of_contents(self, toc: List[Dict[str, Any]], current_chapter: int) -> Optional[int]:
        """Display table of contents and return selected chapter."""
        self.clear_screen()
        
        table = Table(title="📚 Table of Contents", box=box.ROUNDED)
        table.add_column("No.", style="cyan", width=6)
        table.add_column("Chapter", style="white")
        table.add_column("Level", style="dim", width=8)
        
        for i, item in enumerate(toc):
            style = "bold green" if i == current_chapter else "white"
            level_indicator = "  " * item.get('level', 0) + "•"
            table.add_row(
                str(i + 1),
                item['title'],
                level_indicator,
                style=style
            )
        
        self.console.print(table)
        self.console.print("\n[dim]Enter chapter number (0 to cancel):[/dim]")
        
        try:
            choice = IntPrompt.ask("Chapter", default=0)
            if 1 <= choice <= len(toc):
                return choice - 1
        except (ValueError, KeyboardInterrupt):
            pass
        
        return None
    
    def show_bookmarks(self, bookmarks: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Display bookmarks and return selected bookmark."""
        if not bookmarks:
            self.console.print("[yellow]No bookmarks found.[/yellow]")
            self.console.input("\nPress Enter to continue...")
            return None
        
        self.clear_screen()
        
        table = Table(title="🔖 Bookmarks", box=box.ROUNDED)
        table.add_column("No.", style="cyan", width=6)
        table.add_column("Chapter", style="white")
        table.add_column("Note", style="dim")
        table.add_column("Created", style="dim")
        
        for i, bookmark in enumerate(bookmarks):
            table.add_row(
                str(i + 1),
                f"Chapter {bookmark['chapter'] + 1}",
                bookmark.get('note', '')[:50] + ('...' if len(bookmark.get('note', '')) > 50 else ''),
                bookmark.get('created_at', '')[:16]
            )
        
        self.console.print(table)
        self.console.print("\n[dim]Enter bookmark number (0 to cancel, -1 to delete):[/dim]")
        
        try:
            choice = IntPrompt.ask("Bookmark", default=0)
            if 1 <= choice <= len(bookmarks):
                return bookmarks[choice - 1]
            elif choice == -1:
                delete_choice = IntPrompt.ask("Delete bookmark number", default=0)
                if 1 <= delete_choice <= len(bookmarks):
                    return {'action': 'delete', 'bookmark': bookmarks[delete_choice - 1]}
        except (ValueError, KeyboardInterrupt):
            pass
        
        return None
    
    def show_settings(self, current_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Display settings menu and return updated settings."""
        self.clear_screen()
        
        # Create a copy to track changes
        modified_settings = {
            'display': current_settings.get('display', {}).copy(),
            'reading': current_settings.get('reading', {}).copy()
        }
        settings_changed = False
        
        while True:
            table = Table(title="⚙️ Settings", box=box.ROUNDED)
            table.add_column("Setting", style="cyan")
            table.add_column("Current Value", style="white")
            table.add_column("Description", style="dim")
            
            display = modified_settings.get('display', {})
            reading = modified_settings.get('reading', {})
            
            table.add_row("1", f"Font Size: {display.get('font_size', 12)}", "Text size (8-72)")
            table.add_row("2", f"Line Spacing: {display.get('line_spacing', 1.2)}", "Line height (0.5-3.0)")
            table.add_row("3", f"Page Width: {display.get('page_width', 80)}", "Characters per line")
            table.add_row("4", f"Page Height: {display.get('page_height', 24)}", "Lines per page")
            table.add_row("5", f"Show Progress: {reading.get('show_progress', True)}", "Display reading progress")
            table.add_row("6", f"Auto Save: {reading.get('auto_save_interval', 30)}s", "Auto save interval")
            table.add_row("0", "Save and return", "Save changes and return to book")
            
            self.console.print(table)
            
            if settings_changed:
                self.console.print("\n[yellow]⚠️  You have unsaved changes[/yellow]")
            
            try:
                choice = IntPrompt.ask("\nSelect setting to change", default=0)
                
                if choice == 0:
                    break
                elif choice == 1:
                    new_size = IntPrompt.ask("Font size (8-72)", default=display.get('font_size', 12))
                    if 8 <= new_size <= 72:
                        modified_settings['display']['font_size'] = new_size
                        settings_changed = True
                        self.console.print(f"[green]✓ Font size changed to {new_size}[/green]")
                    else:
                        self.console.print("[red]Invalid font size! Must be between 8-72[/red]")
                elif choice == 2:
                    new_spacing = float(Prompt.ask("Line spacing (0.5-3.0)", default=str(display.get('line_spacing', 1.2))))
                    if 0.5 <= new_spacing <= 3.0:
                        modified_settings['display']['line_spacing'] = new_spacing
                        settings_changed = True
                        self.console.print(f"[green]✓ Line spacing changed to {new_spacing}[/green]")
                    else:
                        self.console.print("[red]Invalid line spacing! Must be between 0.5-3.0[/red]")
                elif choice == 3:
                    new_width = IntPrompt.ask("Page width (40-120)", default=display.get('page_width', 80))
                    if 40 <= new_width <= 120:
                        modified_settings['display']['page_width'] = new_width
                        self.page_width = new_width
                        settings_changed = True
                        self.console.print(f"[green]✓ Page width changed to {new_width}[/green]")
                    else:
                        self.console.print("[red]Invalid page width! Must be between 40-120[/red]")
                elif choice == 4:
                    new_height = IntPrompt.ask("Page height (10-50)", default=display.get('page_height', 24))
                    if 10 <= new_height <= 50:
                        modified_settings['display']['page_height'] = new_height
                        self.page_height = new_height
                        settings_changed = True
                        self.console.print(f"[green]✓ Page height changed to {new_height}[/green]")
                    else:
                        self.console.print("[red]Invalid page height! Must be between 10-50[/red]")
                elif choice == 5:
                    new_progress = Confirm.ask("Show progress")
                    modified_settings['reading']['show_progress'] = new_progress
                    settings_changed = True
                    self.console.print(f"[green]✓ Show progress changed to {new_progress}[/green]")
                elif choice == 6:
                    new_interval = IntPrompt.ask("Auto save interval (10-300 seconds)", default=reading.get('auto_save_interval', 30))
                    if 10 <= new_interval <= 300:
                        modified_settings['reading']['auto_save_interval'] = new_interval
                        settings_changed = True
                        self.console.print(f"[green]✓ Auto save interval changed to {new_interval}s[/green]")
                    else:
                        self.console.print("[red]Invalid interval! Must be between 10-300 seconds[/red]")
                
                if choice != 0:
                    time.sleep(1)  # Brief pause to show the confirmation message
                    self.clear_screen()
                
            except (ValueError, KeyboardInterrupt):
                break
        
        # Return modified settings only if changes were made
        return modified_settings if settings_changed else None
    
    def show_library(self, books: List[Dict[str, Any]]) -> Optional[str]:
        """Display library and return selected book path."""
        if not books:
            self.console.print("[yellow]No books in library.[/yellow]")
            self.console.input("\nPress Enter to continue...")
            return None
        
        self.clear_screen()
        
        table = Table(title="📚 Library", box=box.ROUNDED)
        table.add_column("No.", style="cyan", width=6)
        table.add_column("Title", style="white")
        table.add_column("Author", style="dim")
        table.add_column("Progress", style="green")
        table.add_column("Last Read", style="dim")
        
        for i, book in enumerate(books):
            progress = f"{book.get('current_chapter', 0) + 1}/{book.get('total_chapters', 1)}"
            last_read = book.get('last_read', '')[:16] if book.get('last_read') else 'Never'
            
            table.add_row(
                str(i + 1),
                book.get('title', 'Unknown')[:40],
                book.get('author', 'Unknown')[:30],
                progress,
                last_read
            )
        
        self.console.print(table)
        self.console.print("\n[dim]Enter book number (0 to cancel):[/dim]")
        
        try:
            choice = IntPrompt.ask("Book", default=0)
            if 1 <= choice <= len(books):
                return books[choice - 1]['file_path']
        except (ValueError, KeyboardInterrupt):
            pass
        
        return None
    
    def show_file_browser(self, current_path: str = ".") -> Optional[str]:
        """Show file browser for selecting EPUB files."""
        self.clear_screen()
        
        try:
            files = []
            dirs = []
            
            # Add parent directory option
            if current_path != "/":
                dirs.append("..")
            
            # List directories and EPUB files
            for item in sorted(os.listdir(current_path)):
                item_path = os.path.join(current_path, item)
                if os.path.isdir(item_path):
                    dirs.append(item)
                elif item.lower().endswith('.epub'):
                    files.append(item)
            
            table = Table(title=f"📁 File Browser - {current_path}", box=box.ROUNDED)
            table.add_column("No.", style="cyan", width=6)
            table.add_column("Name", style="white")
            table.add_column("Type", style="dim")
            
            all_items = []
            
            # Add directories
            for i, dir_name in enumerate(dirs):
                table.add_row(str(i + 1), f"📁 {dir_name}", "Directory")
                all_items.append(('dir', dir_name))
            
            # Add EPUB files
            for i, file_name in enumerate(files):
                table.add_row(str(len(dirs) + i + 1), f"📖 {file_name}", "EPUB")
                all_items.append(('file', file_name))
            
            if not all_items:
                self.console.print("[yellow]No directories or EPUB files found.[/yellow]")
                self.console.input("\nPress Enter to continue...")
                return None
            
            self.console.print(table)
            self.console.print("\n[dim]Enter number to select (0 to cancel):[/dim]")
            
            choice = IntPrompt.ask("Selection", default=0)
            if 1 <= choice <= len(all_items):
                item_type, item_name = all_items[choice - 1]
                
                if item_type == 'dir':
                    if item_name == "..":
                        new_path = os.path.dirname(current_path)
                    else:
                        new_path = os.path.join(current_path, item_name)
                    return self.show_file_browser(new_path)
                else:
                    return os.path.join(current_path, item_name)
            
        except (OSError, ValueError, KeyboardInterrupt):
            pass
        
        return None
    
    def show_search_results(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Display search results and return selected result."""
        if not results:
            self.console.print("[yellow]No results found.[/yellow]")
            self.console.input("\nPress Enter to continue...")
            return None
        
        self.clear_screen()
        
        table = Table(title="🔍 Search Results", box=box.ROUNDED)
        table.add_column("No.", style="cyan", width=6)
        table.add_column("Chapter", style="white")
        table.add_column("Line", style="dim", width=8)
        table.add_column("Content", style="white")
        
        for i, result in enumerate(results[:20]):  # Limit to 20 results
            table.add_row(
                str(i + 1),
                result['chapter_title'][:30],
                str(result['line_number']),
                result['line_content'][:60] + ('...' if len(result['line_content']) > 60 else '')
            )
        
        if len(results) > 20:
            self.console.print(f"\n[dim]Showing first 20 of {len(results)} results[/dim]")
        
        self.console.print(table)
        self.console.print("\n[dim]Enter result number (0 to cancel):[/dim]")
        
        try:
            choice = IntPrompt.ask("Result", default=0)
            if 1 <= choice <= min(20, len(results)):
                return results[choice - 1]
        except (ValueError, KeyboardInterrupt):
            pass
        
        return None
    
    def show_progress(self, message: str, total: int = 100) -> Progress:
        """Show progress bar."""
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True
        )
        task = progress.add_task(message, total=total)
        return progress, task
    
    def show_message(self, message: str, message_type: str = "info") -> None:
        """Show a message to the user."""
        style_map = {
            "info": "blue",
            "success": "green", 
            "warning": "yellow",
            "error": "red"
        }
        
        style = style_map.get(message_type, "white")
        self.console.print(f"[{style}]{message}[/{style}]")
    
    def get_input(self, prompt: str, default: str = "") -> str:
        """Get user input."""
        return Prompt.ask(prompt, default=default)
    
    def get_confirmation(self, message: str) -> bool:
        """Get user confirmation."""
        return Confirm.ask(message)
    
    def show_help(self) -> None:
        """Display help information."""
        self.clear_screen()
        
        help_text = """
[bold blue]📖 EPUB Reader Help[/bold blue]

[bold]Reading Controls:[/bold]
  ↑/K/PgUp     - Previous page
  ↓/J/PgDn     - Next page
  ←/H          - Previous chapter
  →/L          - Next chapter
  
[bold]Navigation:[/bold]
  T            - Table of contents
  G            - Go to page/chapter
  /            - Search in book
  
[bold]Bookmarks:[/bold]
  B            - Toggle bookmark
  Shift+B      - Show bookmarks
  
[bold]Other:[/bold]
  S            - Settings
  L            - Library
  O            - Open file
  Q/Esc        - Quit
  ?            - This help

[bold]Tips:[/bold]
  • All opened books are automatically saved to your library
  • Reading progress is automatically saved
  • Use settings to customize display preferences
  • Bookmarks are saved with optional notes
        """
        
        panel = Panel(help_text, box=box.ROUNDED, title="Help", title_align="left")
        self.console.print(panel)
        self.console.input("\nPress Enter to continue...")
    
    def show_error(self, error_message: str) -> None:
        """Display error message."""
        error_panel = Panel(
            f"[red]Error: {error_message}[/red]",
            box=box.ROUNDED,
            style="red"
        )
        self.console.print(error_panel)
        self.console.input("\nPress Enter to continue...")
    
    def get_key_input(self) -> str:
        """Get single key input without showing prompt."""
        if os.name == 'posix':
            return self._get_key_unix()
        else:
            return self._get_key_windows()
    
    def _get_key_unix(self) -> str:
        """Get key input on Unix/Linux systems."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            
            # Handle escape sequences for arrow keys
            if ch == '\x1b':  # ESC sequence
                ch += sys.stdin.read(2)
                if ch == '\x1b[A':
                    return 'up'
                elif ch == '\x1b[B':
                    return 'down'
                elif ch == '\x1b[C':
                    return 'right'
                elif ch == '\x1b[D':
                    return 'left'
                else:
                    return 'esc'
            elif ch == '\r' or ch == '\n':
                return 'enter'
            elif ch == '\x7f':  # Backspace
                return 'backspace'
            elif ch == ' ':
                return 'space'
            elif ch == '\t':
                return 'tab'
            elif ord(ch) == 3:  # Ctrl+C
                raise KeyboardInterrupt
            elif ord(ch) == 4:  # Ctrl+D
                return 'q'
            else:
                return ch.lower()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    
    def _get_key_windows(self) -> str:
        """Get key input on Windows systems."""
        try:
            import msvcrt
            ch = msvcrt.getch()
            
            # Handle special keys
            if ch == b'\xe0':  # Arrow keys prefix on Windows
                ch = msvcrt.getch()
                if ch == b'H':
                    return 'up'
                elif ch == b'P':
                    return 'down'
                elif ch == b'M':
                    return 'right'
                elif ch == b'K':
                    return 'left'
            elif ch == b'\r':
                return 'enter'
            elif ch == b'\x08':  # Backspace
                return 'backspace'
            elif ch == b' ':
                return 'space'
            elif ch == b'\t':
                return 'tab'
            elif ch == b'\x1b':  # ESC
                return 'esc'
            elif ch == b'\x03':  # Ctrl+C
                raise KeyboardInterrupt
            else:
                return ch.decode('utf-8', errors='ignore').lower()
        except ImportError:
            # Fallback for systems without msvcrt
            return input().lower()
        except Exception:
            return 'q'
