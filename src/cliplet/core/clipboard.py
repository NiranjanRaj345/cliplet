"""Clipboard monitoring and history management"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Callable, Any

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
from gi.repository import Gtk, Gdk, GLib

logger = logging.getLogger(__name__)

class ClipboardItem:
    """Represents a single clipboard item with metadata"""
    
    def __init__(self, content: str, content_type: str = "text", timestamp: Optional[datetime] = None):
        self.content = content
        self.content_type = content_type
        self.timestamp = timestamp or datetime.now()
        self.preview = self._generate_preview()
    
    def _generate_preview(self) -> str:
        """Generate a preview string for the clipboard item"""
        if self.content_type == "text":
            # Clean up whitespace and limit length
            preview = ' '.join(self.content.split())
            return preview[:80] + "..." if len(preview) > 80 else preview
        else:
            return f"[{self.content_type.title()} - {self.timestamp.strftime('%H:%M:%S')}]"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'content': self.content,
            'content_type': self.content_type,
            'timestamp': self.timestamp.isoformat(),
            'preview': self.preview
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ClipboardItem':
        """Create ClipboardItem from dictionary"""
        timestamp = datetime.fromisoformat(data['timestamp'])
        return cls(data['content'], data['content_type'], timestamp)


class ClipboardHistory:
    """Manages clipboard history storage and retrieval"""
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.items: List[ClipboardItem] = []
        self.max_items = self.config.get('max_items', 25)
        self.load_history()
    
    def load_history(self) -> None:
        """Load clipboard history from file"""
        from ..config import get_history_file
        history_file = get_history_file()
        
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.items = [ClipboardItem.from_dict(item) for item in data]
                logger.info(f"Loaded {len(self.items)} clipboard items from history")
            except (json.JSONDecodeError, IOError, KeyError) as e:
                logger.error(f"Failed to load clipboard history: {e}")
                self.items = []
    
    def save_history(self) -> None:
        """Save clipboard history to file"""
        from ..config import get_history_file, ensure_directories
        
        try:
            ensure_directories()
            history_file = get_history_file()
            
            data = [item.to_dict() for item in self.items]
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Saved {len(self.items)} clipboard items to history")
        except IOError as e:
            logger.error(f"Failed to save clipboard history: {e}")
    
    def add_item(self, content: str, content_type: str = "text") -> Optional[ClipboardItem]:
        """Add new item to clipboard history"""
        # Validate content
        if not content or (isinstance(content, str) and not content.strip()):
            return None
        
        # Check minimum/maximum length constraints
        min_length = self.config.get('min_text_length', 1)
        max_length = self.config.get('max_text_length', 10000)
        
        if len(content) < min_length or len(content) > max_length:
            logger.debug(f"Content length {len(content)} outside range [{min_length}, {max_length}]")
            return None
        
        # Check if item already exists (avoid duplicates)
        for i, item in enumerate(self.items):
            if item.content == content and item.content_type == content_type:
                # Move existing item to top
                self.items.pop(i)
                logger.debug("Moved duplicate item to top")
                break
        
        # Add new item at the beginning
        new_item = ClipboardItem(content, content_type)
        self.items.insert(0, new_item)
        
        # Trim history to max items
        if len(self.items) > self.max_items:
            removed_count = len(self.items) - self.max_items
            self.items = self.items[:self.max_items]
            logger.debug(f"Trimmed {removed_count} old items from history")
        
        self.save_history()
        logger.debug(f"Added new clipboard item: {new_item.preview}")
        return new_item
    
    def clear_history(self) -> None:
        """Clear all clipboard history"""
        self.items.clear()
        self.save_history()
        logger.info("Clipboard history cleared")
    
    def get_items(self, limit: Optional[int] = None) -> List[ClipboardItem]:
        """Get clipboard items with optional limit"""
        if limit is None:
            return self.items.copy()
        return self.items[:limit]


class ClipboardMonitor:
    """Monitors system clipboard for changes"""
    
    def __init__(self, history: ClipboardHistory, config):
        self.history = history
        self.config = config
        self.clipboard = Gdk.Display.get_default().get_clipboard()
        self.last_content = ""
        self.monitoring = False
        self.callbacks: List[Callable[[ClipboardItem], None]] = []
        
        logger.info("Clipboard monitor initialized")
    
    def add_callback(self, callback: Callable[[ClipboardItem], None]) -> None:
        """Add callback to be called when clipboard changes"""
        self.callbacks.append(callback)
        logger.debug(f"Added clipboard change callback: {callback.__name__}")
    
    def start_monitoring(self) -> None:
        """Start monitoring clipboard changes"""
        self.monitoring = True
        self.clipboard.connect('changed', self._on_clipboard_changed)
        logger.info("Started clipboard monitoring")
    
    def stop_monitoring(self) -> None:
        """Stop monitoring clipboard changes"""
        self.monitoring = False
        logger.info("Stopped clipboard monitoring")
    
    def _should_exclude_content(self, content: str) -> bool:
        """Check if content should be excluded from monitoring"""
        # Check for password-like patterns if enabled
        if self.config.get('exclude_passwords', True):
            # Simple heuristics for password detection
            if len(content) < 50 and any(char in content for char in "!@#$%^&*"):
                # Likely a password
                return True
        
        # Add more exclusion logic here
        return False
    
    def _on_clipboard_changed(self, clipboard) -> None:
        """Handle clipboard change event"""
        if not self.monitoring:
            return
        
        # Get clipboard content asynchronously
        clipboard.read_text_async(None, self._on_clipboard_text_ready)
    
    def _on_clipboard_text_ready(self, clipboard, result) -> None:
        """Handle clipboard text retrieval"""
        try:
            content = clipboard.read_text_finish(result)
            if content and content != self.last_content:
                # Check if content should be excluded
                if self._should_exclude_content(content):
                    logger.debug("Excluded content from clipboard monitoring")
                    return
                
                self.last_content = content
                
                # Add to history
                item = self.history.add_item(content, "text")
                
                if item:
                    # Notify callbacks
                    for callback in self.callbacks:
                        try:
                            GLib.idle_add(callback, item)
                        except Exception as e:
                            logger.error(f"Error in clipboard callback: {e}")
                            
        except Exception as e:
            logger.error(f"Error processing clipboard content: {e}")
    
    def set_clipboard_content(self, content: str) -> None:
        """Set clipboard content programmatically"""
        try:
            self.clipboard.set_text(content)
            logger.debug(f"Set clipboard content: {content[:50]}...")
        except Exception as e:
            logger.error(f"Failed to set clipboard content: {e}")