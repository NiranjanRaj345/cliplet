# Changelog

All notable changes to the Cliplet will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-09-01

### Added
- **Core Features**
  - GTK4-based clipboard manager with modern interface
  - Background daemon for continuous clipboard monitoring
  - Popup window for quick clipboard history access
  - Settings GUI for configuration management
  
- **User Interface**
  - Dark theme support with automatic system theme detection
  - Clean, modern GTK4 interface with proper theming
  - Popup window with click-to-paste functionality
  - Settings window with comprehensive configuration options
  
- **System Integration**
  - System-level keyboard shortcut integration (removed app-level hotkeys)
  - Systemd user service for automatic startup
  - XDG directory compliance for configuration and data
  - Desktop application integration (appears in applications menu)
  
- **Configuration & Privacy**
  - Configurable clipboard history limits
  - Auto-cleanup with configurable retention periods
  - Application exclusion list for privacy
  - Persistent settings with validation
  
- **Installation & Deployment**
  - Professional installation script with dependency checking
  - Complete uninstallation script with cleanup options
  - Keyboard shortcut setup wizard
  - Production-ready file structure

### Technical Details
- **Architecture**: Modular Python package structure
- **GUI Framework**: GTK4 with Adwaita theme support
- **Service Management**: Systemd user services
- **Security**: Sandboxed execution with resource limits
- **Dependencies**: Python 3, GTK4, PyGObject, libadwaita

### Documentation
- Comprehensive README with installation instructions
- Detailed keyboard shortcut setup guide
- Complete API documentation
- Installation and configuration examples
