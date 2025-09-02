# 📖 API Reference

Complete API documentation for Cliplet components.

## Core Architecture

### Module Structure
```
cliplet/
├── core/           # Core functionality
├── ui/             # User interface components  
├── config/         # Configuration management
└── utils/          # Utility functions
```

---

## Core Module (`cliplet.core`)

### `ClipboardDaemon`
Main daemon process that coordinates all components.

```python
class ClipboardDaemon:
    """Main daemon process for clipboard management."""
```

#### Constructor
```python
def __init__(self, config_path: Optional[str] = None) -> None:
    """Initialize the clipboard daemon.
    
    Args:
        config_path: Optional path to configuration file
    """
```

#### Methods
```python
def start(self) -> None:
    """Start the daemon and all monitoring services."""

def stop(self) -> None:
    """Stop the daemon and cleanup resources."""

def reload_config(self) -> None:
    """Reload configuration from file."""

def show_popup(self) -> None:
    """Display the clipboard popup window."""
```

#### Properties
```python
@property
def is_running(self) -> bool:
    """Check if daemon is currently running."""

@property
def config(self) -> ConfigManager:
    """Get the configuration manager instance."""
```

---

### `ClipboardManager`
Handles clipboard monitoring and change detection.

```python
class ClipboardManager:
    """Monitors system clipboard for changes."""
```

#### Constructor
```python
def __init__(self, history: ClipboardHistory, config) -> None:
    """Initialize clipboard monitor.
    
    Args:
        history: ClipboardHistory instance for storage
        config: Configuration manager instance
    """
```

#### Methods
```python
def start_monitoring(self) -> None:
    """Start monitoring clipboard changes."""

def stop_monitoring(self) -> None:
    """Stop monitoring clipboard changes."""

def add_callback(self, callback: Callable[[ClipboardItem], None]) -> None:
    """Add callback for clipboard changes.
    
    Args:
        callback: Function to call when clipboard changes
    """

def set_clipboard_content(self, content: str) -> None:
    """Set clipboard content programmatically.
    
    Args:
        content: Text content to set in clipboard
    """
```

---

### `ClipboardHistory`
Manages clipboard item storage and retrieval.

```python
class ClipboardHistory:
    """Manages clipboard history storage and retrieval."""
```

#### Constructor
```python
def __init__(self, config_manager: ConfigManager) -> None:
    """Initialize clipboard history.
    
    Args:
        config_manager: Configuration manager instance
    """
```

#### Methods
```python
def add_item(self, content: str, content_type: str = "text") -> Optional[ClipboardItem]:
    """Add new item to clipboard history.
    
    Args:
        content: Clipboard content
        content_type: Type of content (default: "text")
        
    Returns:
        Created ClipboardItem or None if excluded
    """

def get_items(self, limit: Optional[int] = None) -> List[ClipboardItem]:
    """Get clipboard history items.
    
    Args:
        limit: Maximum number of items to return
        
    Returns:
        List of ClipboardItem objects
    """

def clear_history(self) -> None:
    """Clear all clipboard history."""

def load_history(self) -> None:
    """Load history from persistent storage."""

def save_history(self) -> None:
    """Save history to persistent storage."""
```

---

### `ClipboardItem`
Represents a single clipboard entry.

```python
class ClipboardItem:
    """Represents a single clipboard item with metadata."""
```

#### Constructor
```python
def __init__(self, content: str, content_type: str = "text", 
             timestamp: Optional[datetime] = None) -> None:
    """Initialize clipboard item.
    
    Args:
        content: The clipboard content
        content_type: Type of content (default: "text")
        timestamp: When item was created (default: now)
    """
```

#### Properties
```python
@property
def content(self) -> str:
    """Get the clipboard content."""

@property
def content_type(self) -> str:
    """Get the content type."""

@property
def timestamp(self) -> datetime:
    """Get the creation timestamp."""

@property
def preview(self) -> str:
    """Get a preview of the content (truncated)."""
```

#### Methods
```python
def to_dict(self) -> dict:
    """Convert item to dictionary representation."""

@classmethod
def from_dict(cls, data: dict) -> 'ClipboardItem':
    """Create item from dictionary representation."""
```

---

## UI Module (`cliplet.ui`)

### `ClipboardPopup`
Main popup window for clipboard history.

```python
class ClipboardPopup(Gtk.Window):
    """Lightweight popup window that appears at cursor location."""
```

#### Constructor
```python
def __init__(self, history: ClipboardHistory, config) -> None:
    """Initialize popup window.
    
    Args:
        history: ClipboardHistory instance
        config: Configuration manager
    """
```

#### Methods
```python
def show_at_cursor(self) -> None:
    """Show popup at current cursor/mouse position."""

def refresh_items(self) -> None:
    """Refresh the clipboard items in the popup."""

def hide(self) -> bool:
    """Hide the popup window."""

def cleanup(self) -> None:
    """Clean up resources."""
```

---

### `SettingsWindow`
Settings GUI window.

```python
class SettingsWindow(Gtk.ApplicationWindow):
    """Settings window for clipboard manager."""
```

#### Constructor
```python
def __init__(self, app) -> None:
    """Initialize settings window.
    
    Args:
        app: GTK Application instance
    """
```

#### Methods
```python
def load_settings(self) -> None:
    """Load current settings into the UI."""

def save_settings(self) -> None:
    """Save settings from the UI to config."""
```

---

### `SettingsApplication`
GTK Application for settings.

```python
class SettingsApplication(Gtk.Application):
    """Settings application."""
```

#### Constructor
```python
def __init__(self, config=None) -> None:
    """Initialize settings application.
    
    Args:
        config: Optional configuration manager instance
    """
```

---

## Config Module (`cliplet.config`)

### `ConfigManager`
Manages application configuration.

```python
class ConfigManager:
    """Manages application configuration with validation."""
```

#### Constructor
```python
def __init__(self, config_file: Optional[str] = None) -> None:
    """Initialize configuration manager.
    
    Args:
        config_file: Optional path to config file
    """
```

#### Methods
```python
def get(self, key: str, default=None) -> Any:
    """Get configuration value.
    
    Args:
        key: Configuration key
        default: Default value if key not found
        
    Returns:
        Configuration value or default
    """

def set(self, key: str, value: Any) -> None:
    """Set configuration value.
    
    Args:
        key: Configuration key
        value: Value to set
    """

def save(self) -> None:
    """Save configuration to file."""

def load(self) -> None:
    """Load configuration from file."""

def reset(self) -> None:
    """Reset configuration to defaults."""

def validate(self) -> bool:
    """Validate current configuration."""

def clear_history(self) -> None:
    """Clear clipboard history data."""
```

---

### Default Configuration (`cliplet.config.defaults`)

```python
DEFAULT_CONFIG = {
    # Popup settings
    'popup_width': 400,
    'popup_height': 300,
    'popup_items_visible': 8,
    'auto_hide_delay': 30,
    
    # History settings
    'max_history_items': 25,
    'auto_cleanup_days': 7,
    
    # Privacy settings
    'excluded_apps': [
        'gnome-keyring',
        'keepassxc',
        'bitwarden'
    ],
    
    # System settings
    'log_level': 'INFO',
    'monitor_clipboard': True
}
```

---

### Path Management (`cliplet.config.paths`)

```python
def get_config_dir() -> Path:
    """Get user configuration directory."""

def get_data_dir() -> Path:
    """Get user data directory."""

def get_cache_dir() -> Path:
    """Get user cache directory."""

def get_log_file() -> Path:
    """Get log file path."""

def get_config_file() -> Path:
    """Get configuration file path."""

def get_history_file() -> Path:
    """Get history file path."""
```

---

## Utils Module (`cliplet.utils`)

### Logging (`cliplet.utils.logging`)

```python
def setup_logging(level: str = 'INFO', log_file: Optional[str] = None) -> None:
    """Setup application logging.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
    """

def get_logger(name: str) -> logging.Logger:
    """Get logger instance for module.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
```

---

### PID Management (`cliplet.utils.pid`)

```python
class PIDManager:
    """Manages process ID file for daemon."""
```

#### Constructor
```python
def __init__(self, pid_file: str) -> None:
    """Initialize PID manager.
    
    Args:
        pid_file: Path to PID file
    """
```

#### Methods
```python
def create(self) -> None:
    """Create PID file with current process ID."""

def remove(self) -> None:
    """Remove PID file."""

def is_running(self) -> bool:
    """Check if process with stored PID is running."""

def get_pid(self) -> Optional[int]:
    """Get stored process ID."""
```

---

## Command Line Interface

### `clipletd` - Daemon
```bash
clipletd [-h] [--config CONFIG] [--log-level LEVEL] [--log-file FILE] 
         [--foreground] [--pid-file FILE] [--version] [--check-config]
```

**Options:**
- `--config, -c`: Path to configuration file
- `--log-level, -l`: Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `--log-file`: Path to log file
- `--foreground, -f`: Run in foreground (don't daemonize)
- `--pid-file, -p`: Path to PID file
- `--version, -v`: Show version and exit
- `--check-config`: Validate configuration and exit

---

### `cliplet-popup` - Popup Window
```bash
cliplet-popup [-h] [--version] [--show-path]
```

**Options:**
- `--version, -v`: Show version and exit
- `--show-path`: Show full path to executable (for shortcut setup)

---

### `cliplet-settings` - Settings GUI
```bash
cliplet-settings [-h] [--config CONFIG] [--version] [--reset] 
                 [--export FILE] [--import FILE]
```

**Options:**
- `--config, -c`: Path to configuration file
- `--version, -v`: Show version and exit
- `--reset`: Reset all settings to defaults
- `--export FILE`: Export configuration to file
- `--import FILE`: Import configuration from file

---

## Event System

### Clipboard Events
```python
# Callback signature for clipboard changes
def on_clipboard_change(item: ClipboardItem) -> None:
    """Called when clipboard content changes.
    
    Args:
        item: New clipboard item
    """
    pass

# Register callback
clipboard_manager.add_callback(on_clipboard_change)
```

### UI Events
```python
# Popup window events
def on_item_selected(item: ClipboardItem) -> None:
    """Called when user selects clipboard item."""
    pass

def on_popup_shown() -> None:
    """Called when popup is displayed."""
    pass

def on_popup_hidden() -> None:
    """Called when popup is hidden."""
    pass
```

---

## Integration Examples

### Custom Clipboard Processor
```python
from cliplet.core.clipboard import ClipboardHistory, ClipboardItem
from cliplet.config import ConfigManager

class CustomProcessor:
    def __init__(self):
        self.config = ConfigManager()
        self.history = ClipboardHistory(self.config)
    
    def process_clipboard_item(self, item: ClipboardItem) -> None:
        """Process clipboard item with custom logic."""
        if len(item.content) > 100:
            # Handle long content
            self.handle_long_content(item)
        
        # Add to history
        self.history.add_item(item.content)
    
    def handle_long_content(self, item: ClipboardItem) -> None:
        """Custom handling for long clipboard content."""
        # Custom processing logic
        pass
```

### Configuration Extension
```python
from cliplet.config import ConfigManager

class ExtendedConfig(ConfigManager):
    """Extended configuration with custom options."""
    
    def __init__(self):
        super().__init__()
        self.custom_defaults = {
            'custom_feature_enabled': True,
            'custom_timeout': 30
        }
    
    def get_custom_option(self, key: str, default=None):
        """Get custom configuration option."""
        return self.get(f'custom_{key}', default)
```

---

## Security Considerations

### Safe Content Handling
```python
def sanitize_content(content: str) -> str:
    """Sanitize clipboard content for safe storage.
    
    Args:
        content: Raw clipboard content
        
    Returns:
        Sanitized content
    """
    # Remove potential security risks
    # Limit content length
    # Filter sensitive patterns
    return content[:10000]  # Max 10KB
```

### Privacy Protection
```python
def should_exclude_app(app_name: str, excluded_apps: List[str]) -> bool:
    """Check if application should be excluded from monitoring.
    
    Args:
        app_name: Name of the application
        excluded_apps: List of excluded application names
        
    Returns:
        True if app should be excluded
    """
    return any(excluded in app_name.lower() for excluded in excluded_apps)
```

---

## Performance Optimization

### Memory Management
```python
def cleanup_old_items(history: ClipboardHistory, max_age_days: int) -> None:
    """Remove old items from history to manage memory.
    
    Args:
        history: ClipboardHistory instance
        max_age_days: Maximum age in days to keep items
    """
    cutoff_date = datetime.now() - timedelta(days=max_age_days)
    # Implementation details...
```

### Efficient Monitoring
```python
def optimize_clipboard_monitoring(manager: ClipboardManager) -> None:
    """Optimize clipboard monitoring for better performance.
    
    Args:
        manager: ClipboardManager instance
    """
    # Reduce polling frequency
    # Implement debouncing
    # Use efficient change detection
```

---

## Type Definitions

### Custom Types
```python
from typing import TypedDict, Literal, Union

ConfigValue = Union[str, int, bool, List[str]]
LogLevel = Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
ContentType = Literal['text', 'image', 'file']

class ConfigDict(TypedDict):
    popup_width: int
    popup_height: int
    popup_items_visible: int
    max_history_items: int
    auto_cleanup_days: int
    excluded_apps: List[str]
    log_level: LogLevel
```

---

## Error Handling

### Custom Exceptions
```python
class ClipletError(Exception):
    """Base exception for Cliplet errors."""
    pass

class ConfigurationError(ClipletError):
    """Configuration-related errors."""
    pass

class ClipboardError(ClipletError):
    """Clipboard operation errors."""
    pass

class UIError(ClipletError):
    """User interface errors."""
    pass
```

### Error Recovery
```python
def handle_clipboard_error(error: Exception) -> None:
    """Handle clipboard operation errors gracefully.
    
    Args:
        error: Exception that occurred
    """
    logger.error(f"Clipboard error: {error}")
    # Implement recovery logic
    # Restart monitoring if needed
    # Notify user if appropriate