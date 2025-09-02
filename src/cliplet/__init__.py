"""
Cliplet - Windows-style clipboard manager for Linux

A lightweight, Windows-like clipboard manager that runs as a background daemon
and provides a popup overlay for clipboard history management.

Author: Cliplet Team
License: GPL-3.0
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Cliplet Team"
__license__ = "GPL-3.0"
__description__ = "Windows-style clipboard manager for Linux"

# Package metadata
PACKAGE_NAME = "cliplet"
DAEMON_NAME = "clipletd"
SETTINGS_NAME = "cliplet-settings"

# Default configuration
DEFAULT_CONFIG = {
    'hotkey': '<Super>v',
    'max_history_items': 25,
    'popup_width': 400,
    'popup_height': 300,
    'popup_items_visible': 8,
    'auto_hide_delay': 30,
    'auto_cleanup_days': 7,
    'excluded_apps': []
}

# Installation paths
INSTALL_PATHS = {
    'bin': '/usr/local/bin',
    'share': '/usr/local/share',
    'config': '~/.config/cliplet',
    'data': '~/.local/share/cliplet',
    'systemd': '~/.config/systemd/user'
}