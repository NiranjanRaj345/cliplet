# Cliplet - Modern Clipboard Manager for Linux

[![Version](https://img.shields.io/badge/version-1.0.1-blue.svg)](https://github.com/cliplet/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Linux-blue.svg)](https://www.linux.org/)

**A clean, modern clipboard manager with Windows-style functionality for Linux desktops**

## Features

### **Core Functionality**
- **Background Daemon** - Runs silently with minimal resource usage (<100MB RAM)
- **Instant Access** - Quick popup with customizable keyboard shortcuts
- **Smart History** - Intelligent clipboard history with previews
- **Modern UI** - Clean, borderless popup interface
- **Easy Setup** - Interactive installation and configuration

### **User Experience**
- **Windows-like Feel** - Familiar clipboard access patterns
- **Click to Paste** - Simple click-to-use interface
- **Auto-hide** - Popup disappears when you click elsewhere
- **Cursor Positioning** - Appears near your mouse cursor
- **Lightweight** - Minimal system impact

### **Technical Excellence**
- **GTK4 Native** - Modern Linux desktop integration
- **Systemd Service** - Proper daemon management
- **XDG Compliant** - Follows Linux directory standards
- **Professional Logging** - Comprehensive error tracking
- **Secure Operation** - Limited permissions and sandboxing

---

## Quick Start

### 1. Setup Keyboard Shortcuts (Interactive)
```bash
git clone https://github.com/NiranjanRaj345/cliplet.git
cd cliplet

# Start with keyboard shortcut setup
./scripts/setup-keyboard-shortcut.sh
```

### 2. Install for Current User (Recommended)
```bash
# Install the application (no sudo needed)
./scripts/install.sh
```

### 3. Start Using
```bash
# Start the daemon
systemctl --user start cliplet

# Test your keyboard shortcut!
# Default suggestion: Super+V (Windows key + V)
```

---

## Project Structure

```
cliplet/
├── bin/                              # Executables
│   ├── clipletd                      # Main daemon
│   ├── cliplet-settings              # Settings GUI
│   └── cliplet-popup                 # Manual popup trigger
├── scripts/                          # Easy-to-use scripts
│   ├── setup-keyboard-shortcut.sh    # Interactive setup
│   ├── install.sh                    # System installation
│   └── uninstall.sh                  # Complete removal
├── src/cliplet/                      # Source code
│   ├── core/                         # Core functionality
│   ├── ui/                           # User interface
│   ├── config/                       # Configuration management
│   └── utils/                        # Utilities
├── docs/                             # Documentation
│   ├── README.md                     # Documentation index
│   ├── KEYBOARD_SHORTCUTS.md        # Detailed setup guide
│   ├── CONFIGURATION.md             # Configuration guide
│   ├── TROUBLESHOOTING.md           # Problem solving
│   ├── DEVELOPMENT.md               # Development guide
│   └── API.md                       # API reference
├── etc/systemd/user/                 # Service files
│   └── cliplet.service              # Systemd service
├── share/applications/               # Desktop integration
│   └── cliplet-settings.desktop     # Settings app launcher
└── share/icons/hicolor/              # Application icons
    ├── 16x16/apps/cliplet.png        # Small icon
    ├── 32x32/apps/cliplet.png        # Medium icon
    ├── 48x48/apps/cliplet.png        # Standard icon
    ├── 1024x1024/apps/cliplet.png    # High resolution
    └── scalable/apps/cliplet.svg     # Vector icon
```

---

## System Requirements

### Minimum
- **OS**: Any modern Linux distribution
- **Python**: 3.9+
- **GTK**: 4.0+
- **Memory**: 64MB RAM
- **Disk**: 50MB storage

### Recommended
- **OS**: Ubuntu 22.04+, Fedora 38+, or equivalent
- **Python**: 3.11+
- **GTK**: 4.8+
- **Memory**: 128MB RAM
- **Disk**: 100MB storage

### Dependencies
```bash
# Required packages (auto-installed)
sudo dnf install python3 python3-gobject-base gtk4

# All dependencies are included above
# Note: Global hotkeys are handled by desktop environment keyboard shortcuts
```

---

## Usage

### Service Management
```bash
# Start daemon
systemctl --user start cliplet

# Enable autostart
systemctl --user enable cliplet

# Check status
systemctl --user status cliplet

# View logs
journalctl --user -u cliplet -f

# Stop daemon
systemctl --user stop cliplet
```

### Keyboard Shortcut Setup
```bash
# Interactive setup helper (recommended)
./scripts/setup-keyboard-shortcut.sh

# Get popup script path for manual setup
./bin/cliplet-popup --show-path

# Test popup directly
./bin/cliplet-popup
```

**Quick Setup:**
1. Run `./scripts/setup-keyboard-shortcut.sh`
2. Follow interactive instructions for your desktop environment
3. Test your new keyboard shortcut!

### Command Line Tools
```bash
# Start daemon with debug output
clipletd --log-level DEBUG --foreground

# Check configuration
clipletd --check-config

# Configure settings
cliplet-settings

# Show popup manually
cliplet-popup
```

### Configuration
```bash
# Configuration file
~/.config/cliplet/config.json

# Data directory
~/.local/share/cliplet/

# Log files
~/.local/share/cliplet/logs/

# Runtime files
~/.cache/cliplet/runtime/
```

---

## Performance

### Resource Usage
- **Memory**: ~50-100MB RAM (depending on history size)
- **CPU**: <1% during normal operation
- **Storage**: ~10-50MB (configurable history retention)

### Monitoring
```bash
# Check daemon status
ps aux | grep clipletd

# Memory usage
pmap $(pgrep clipletd)

# System resource limits
systemctl --user show cliplet | grep -E "(Memory|CPU)"
```

---

## Administration

### Installation Management
```bash
# Verify installation
clipletd --version
cliplet-settings --version

# Complete removal
./scripts/uninstall.sh
```

### Configuration Backup
```bash
# Backup configuration
cp -r ~/.config/cliplet /backup/location/

# Backup data
cp -r ~/.local/share/cliplet /backup/location/

# Restore configuration
cp -r /backup/location/cliplet ~/.config/
```

### Troubleshooting
```bash
# Test daemon startup
clipletd --foreground --log-level DEBUG

# Check dependencies
python3 -c "import gi; gi.require_version('Gtk', '4.0'); print('GTK4 OK')"

# Validate configuration
clipletd --check-config

# Reset to defaults
cliplet-settings --reset
```

---

## Desktop Environment Support

### Fully Tested
- **GNOME** - Native integration
- **KDE Plasma** - Full functionality
- **XFCE** - Complete support
- **MATE** - Fully compatible

### Compatible
- **Cinnamon** - Works well
- **i3/Sway** - Manual setup required
- **LXDE/LXQt** - Basic functionality

---

## Documentation

### User Guides
- [`docs/README.md`](docs/README.md) - Complete documentation
- [`docs/KEYBOARD_SHORTCUTS.md`](docs/KEYBOARD_SHORTCUTS.md) - Detailed keyboard setup
- [`docs/CONFIGURATION.md`](docs/CONFIGURATION.md) - Configuration guide
- [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) - Problem solving
- [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) - Development guide
- [`docs/API.md`](docs/API.md) - API reference

### Quick References
- **Installation**: Run `./scripts/setup-keyboard-shortcut.sh` then `./scripts/install.sh`
- **Testing**: Use `./bin/cliplet-popup` to test functionality (after starting daemon)
- **Uninstall**: Run `./scripts/uninstall.sh` for complete removal
- **Documentation**: See [`docs/`](docs/) for complete guides

### Testing Instructions
```bash
# 1. Test installation requirements (no sudo needed)
./scripts/install.sh --help

# 2. Setup keyboard shortcuts
./scripts/setup-keyboard-shortcut.sh

# 3. Install for current user (no sudo needed)
./scripts/install.sh

# 4. Start daemon and test
systemctl --user start cliplet
./bin/cliplet-popup    # Test popup functionality
```

---

## Security & Privacy

### Security Features
- **Sandboxing** - Limited system access
- **Resource Limits** - Memory and CPU constraints
- **Secure Storage** - Protected configuration files

### Privacy Protection
- **Local Storage** - All data stays on your system
- **No Network** - No internet connections required
- **User Control** - Full control over data retention

---

## Why Cliplet?

### Simple & Clean
- No complicated setup or configuration
- Clean, modern interface
- Works out of the box

### Reliable & Fast
- Minimal resource usage
- Quick access to clipboard history
- Stable background operation

### Professional Quality
- Proper Linux service integration
- Comprehensive logging and monitoring
- Production-ready architecture

---

## Support

### Getting Help
- **Documentation** - Check [`docs/README.md`](docs/README.md) for detailed usage
- **Issues** - Report bugs and feature requests on GitHub
- **Community** - Join discussions and get help from other users

### Contributing
- **Bug Reports** - Help us improve by reporting issues
- **Feature Requests** - Suggest new functionality
- **Code Contributions** - Submit pull requests for improvements

---

## License

MIT License - Open source with enterprise compatibility

---

**Cliplet v1.0.1**

*Modern clipboard management for Linux*

**Ready to try? Start with: `./scripts/setup-keyboard-shortcut.sh`**