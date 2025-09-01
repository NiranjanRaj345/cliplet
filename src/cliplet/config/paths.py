"""Path management for configuration and data directories"""

import os
from pathlib import Path
from typing import Union

def get_config_dir() -> Path:
    """Get the configuration directory for the application"""
    config_home = os.environ.get('XDG_CONFIG_HOME')
    if config_home:
        return Path(config_home) / 'cliplet'
    else:
        return Path.home() / '.config' / 'cliplet'

def get_data_dir() -> Path:
    """Get the data directory for the application"""
    data_home = os.environ.get('XDG_DATA_HOME')
    if data_home:
        return Path(data_home) / 'cliplet'
    else:
        return Path.home() / '.local' / 'share' / 'cliplet'

def get_cache_dir() -> Path:
    """Get the cache directory for the application"""
    cache_home = os.environ.get('XDG_CACHE_HOME')
    if cache_home:
        return Path(cache_home) / 'cliplet'
    else:
        return Path.home() / '.cache' / 'cliplet'

def get_log_dir() -> Path:
    """Get the log directory for the application"""
    return get_data_dir() / 'logs'

def get_runtime_dir() -> Path:
    """Get the runtime directory for PID files and sockets"""
    runtime_dir = os.environ.get('XDG_RUNTIME_DIR')
    if runtime_dir:
        return Path(runtime_dir) / 'cliplet'
    else:
        return get_cache_dir() / 'runtime'

def ensure_directories() -> None:
    """Ensure all required directories exist"""
    directories = [
        get_config_dir(),
        get_data_dir(),
        get_cache_dir(),
        get_log_dir(),
        get_runtime_dir()
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

def get_config_file() -> Path:
    """Get the main configuration file path"""
    return get_config_dir() / 'config.json'

def get_history_file() -> Path:
    """Get the clipboard history file path"""
    return get_data_dir() / 'history.json'

def get_log_file() -> Path:
    """Get the main log file path"""
    return get_log_dir() / 'clipboard-manager.log'

def get_pid_file() -> Path:
    """Get the daemon PID file path"""
    return get_runtime_dir() / 'daemon.pid'