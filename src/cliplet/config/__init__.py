"""Configuration management for Cliplet"""

from .config_manager import ConfigManager
from .paths import get_config_dir, get_data_dir, get_log_dir, get_log_file, get_pid_file, get_history_file, ensure_directories
from .defaults import DEFAULT_CONFIG, CONFIG_SCHEMA

__all__ = ['ConfigManager', 'get_config_dir', 'get_data_dir', 'get_log_dir', 'get_log_file', 'get_pid_file', 'get_history_file', 'ensure_directories', 'DEFAULT_CONFIG', 'CONFIG_SCHEMA']