# Development Guide

Guide for developers who want to contribute to Cliplet or understand its architecture.

## Architecture Overview

### Core Components
```
cliplet/
├── src/cliplet/
│   ├── core/           # Core functionality
│   │   ├── daemon.py   # Main daemon process
│   │   ├── clipboard.py # Clipboard monitoring & history
│   │   └── __init__.py
│   ├── ui/             # User interface
│   │   ├── popup.py    # Popup window
│   │   ├── settings.py # Settings GUI
│   │   └── __init__.py
│   ├── config/         # Configuration management
│   │   ├── config_manager.py
│   │   ├── defaults.py
│   │   ├── paths.py
│   │   └── __init__.py
│   └── utils/          # Utilities
│       ├── logging.py  # Logging setup
│       ├── pid.py      # Process management
│       └── __init__.py
```

### Design Patterns
- **Modular Architecture**: Clean separation of concerns
- **Observer Pattern**: Clipboard monitoring with callbacks
- **Singleton Pattern**: Configuration manager
- **Factory Pattern**: UI component creation

---

## Development Setup

### Prerequisites
```bash
# System dependencies
sudo dnf install python3-devel python3-gobject-base python3-gobject libadwaita-devel

# Or on Ubuntu/Debian
sudo apt install python3-dev python3-gi python3-gi-cairo gir1.2-gtk-4.0 libadwaita-1-dev
```

### Development Environment
```bash
# Clone the repository
git clone <repository-url>
cd cliplet

# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate

# Install development dependencies
pip3 install -r requirements.txt

# Install additional dev tools
pip3 install pytest pytest-cov flake8 mypy black
```

### Running from Source
```bash
# Run daemon in foreground (for debugging)
./bin/clipletd --foreground --log-level DEBUG

# Test popup
./bin/cliplet-popup

# Open settings
./bin/cliplet-settings
```

---

## Testing

### Running Tests
```bash
# Run all tests
make test

# Or manually
python3 -m pytest tests/ -v

# With coverage
make test-coverage
python3 -m pytest tests/ --cov=src/cliplet --cov-report=html
```

### Test Structure
```
tests/
├── unit/
│   ├── test_config.py
│   ├── test_clipboard.py
│   └── test_daemon.py
├── integration/
│   ├── test_ui.py
│   └── test_system.py
└── fixtures/
    └── test_data.json
```

### Writing Tests
```python
import pytest
from unittest.mock import Mock, patch
from cliplet.config import ConfigManager

def test_config_manager_default_values():
    """Test configuration manager returns correct defaults"""
    config = ConfigManager()
    assert config.get('popup_width') == 400
    assert config.get('max_history_items') == 50

@patch('cliplet.config.paths.get_config_dir')
def test_config_loading(mock_config_dir, tmp_path):
    """Test configuration loading from file"""
    mock_config_dir.return_value = tmp_path
    config_file = tmp_path / "config.json"
    config_file.write_text('{"popup_width": 500}')
    
    config = ConfigManager()
    assert config.get('popup_width') == 500
```

---

## Code Style and Standards

### Formatting
```bash
# Format code
make format

# Or manually
python3 -m black src/ tests/

# Check formatting
black --check src/ tests/
```

### Linting
```bash
# Run linters
make lint

# Or manually
python3 -m flake8 src/ tests/
python3 -m mypy src/
```

### Code Style Guidelines
- **PEP 8** compliance
- **Type hints** for all functions
- **Docstrings** for all public methods
- **Error handling** with appropriate exceptions
- **Logging** instead of print statements

```python
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class ClipboardManager:
    """Manages clipboard monitoring and history storage."""
    
    def __init__(self, config: ConfigManager) -> None:
        """Initialize clipboard manager.
        
        Args:
            config: Configuration manager instance
        """
        self.config = config
        self.history: List[ClipboardItem] = []
        logger.debug("ClipboardManager initialized")
    
    def add_item(self, content: str) -> Optional[ClipboardItem]:
        """Add new item to clipboard history.
        
        Args:
            content: Clipboard text content
            
        Returns:
            Created clipboard item or None if excluded
            
        Raises:
            ValueError: If content is empty or invalid
        """
        if not content or not content.strip():
            raise ValueError("Content cannot be empty")
            
        try:
            item = ClipboardItem(content)
            self.history.append(item)
            logger.info(f"Added clipboard item: {item.preview}")
            return item
        except Exception as e:
            logger.error(f"Failed to add clipboard item: {e}")
            return None
```

---

## Building and Packaging

### Development Build
```bash
# Build for testing
make build

# Clean build artifacts
make clean
```

### Creating Packages
```bash
# RPM package (Fedora/RHEL)
make package-rpm

# DEB package (Ubuntu/Debian)
make package-deb
```

### Release Process
1. **Update version**: Edit `VERSION` file
2. **Update changelog**: Add entry to `CHANGELOG.md`
3. **Run tests**: `make test`
4. **Build packages**: `make package-rpm package-deb`
5. **Tag release**: `git tag -a v1.0.1 -m "Release 1.0.1"`

---

## 🧩 Adding New Features

### Feature Development Workflow
1. **Create feature branch**: `git checkout -b feature/new-feature`
2. **Implement feature** with tests
3. **Update documentation**
4. **Test thoroughly**
5. **Submit pull request**

### Example: Adding New UI Component
```python
# src/cliplet/ui/new_component.py
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class NewComponent(Gtk.Window):
    """New UI component for Cliplet."""
    
    def __init__(self, config) -> None:
        """Initialize component."""
        super().__init__()
        self.config = config
        self.setup_ui()
        logger.debug("NewComponent initialized")
    
    def setup_ui(self) -> None:
        """Setup user interface."""
        # Implementation here
        pass
```

### Adding Configuration Options
```python
# src/cliplet/config/defaults.py
DEFAULT_CONFIG = {
    # Existing options...
    'new_feature_enabled': True,
    'new_feature_option': 'default_value',
}
```

---

## 🐛 Debugging

### Debug Mode
```bash
# Run with debug logging
./bin/clipletd --foreground --log-level DEBUG

# Enable GTK debugging
GTK_DEBUG=interactive ./bin/cliplet-popup
```

### Common Debug Scenarios

#### Clipboard Issues
```python
# Add debug logging to clipboard monitoring
def _on_clipboard_changed(self, clipboard):
    logger.debug("Clipboard changed signal received")
    clipboard.read_text_async(None, self._on_clipboard_text_ready)
```

#### UI Issues
```python
# Debug UI events
def _on_key_pressed(self, controller, keyval, keycode, state):
    logger.debug(f"Key pressed: {keyval} (code: {keycode})")
    # Handle key press...
```

#### Performance Profiling
```python
import cProfile
import pstats

def profile_function():
    """Profile a specific function."""
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Function to profile
    result = some_expensive_function()
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative').print_stats(10)
    return result
```

---

## API Documentation

### Core Classes

#### `ClipboardDaemon`
Main daemon process that coordinates all components.

```python
class ClipboardDaemon:
    def __init__(self, config_path: Optional[str] = None)
    def start(self) -> None
    def stop(self) -> None
    def reload_config(self) -> None
```

#### `ClipboardManager`
Handles clipboard monitoring and history storage.

```python
class ClipboardManager:
    def __init__(self, history: ClipboardHistory, config)
    def start_monitoring(self) -> None
    def stop_monitoring(self) -> None
    def add_callback(self, callback: Callable) -> None
```

#### `ClipboardHistory`
Manages clipboard item storage and retrieval.

```python
class ClipboardHistory:
    def __init__(self, config_manager: ConfigManager)
    def add_item(self, content: str) -> Optional[ClipboardItem]
    def get_items(self, limit: Optional[int] = None) -> List[ClipboardItem]
    def clear_history(self) -> None
```

---

## Plugin System (Future)

### Plugin Architecture Design
```python
# Future plugin interface
class ClipletPlugin:
    """Base class for Cliplet plugins."""
    
    def __init__(self, config: ConfigManager) -> None:
        self.config = config
    
    def on_clipboard_change(self, item: ClipboardItem) -> None:
        """Called when clipboard changes."""
        pass
    
    def on_item_selected(self, item: ClipboardItem) -> None:
        """Called when user selects item."""
        pass
```

---

## Deployment

### System Integration
```bash
# Install for development
sudo make install

# Create systemd service
systemctl --user enable cliplet.service
systemctl --user start cliplet.service
```

### Production Deployment
```bash
# Package installation
sudo ./scripts/install.sh

# Verify installation
clipletd --version
systemctl --user status cliplet.service
```

---

## 🤝 Contributing Guidelines

### Pull Request Process
1. **Fork** the repository
2. **Create feature branch** from main
3. **Implement changes** with tests
4. **Update documentation**
5. **Ensure all tests pass**
6. **Submit pull request**

### Code Review Checklist
- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Error handling implemented
- [ ] Logging added appropriately
- [ ] Performance implications considered

### Commit Message Format
```
type(scope): short description

Longer description if needed

Fixes #123
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

---

## Developer Resources

### Useful Links
- **GTK4 Documentation**: https://docs.gtk.org/gtk4/
- **PyGObject Tutorial**: https://pygobject.readthedocs.io/
- **Python Type Hints**: https://docs.python.org/3/library/typing.html

### Development Tools
- **GTK Inspector**: `GTK_DEBUG=interactive ./bin/cliplet-popup`
- **Python Debugger**: Use `pdb` or IDE debugger
- **Memory Profiling**: `memory_profiler` package
- **Performance**: `cProfile` and `py-spy`

### Getting Help
- **GitHub Issues**: Report bugs and request features
- **Development Chat**: [Community channels]
- **Documentation**: This guide and inline code docs