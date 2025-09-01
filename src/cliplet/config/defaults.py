"""Default configuration and schema definitions"""

DEFAULT_CONFIG = {
    # Popup appearance
    'popup_width': 400,
    'popup_height': 300,
    'popup_items_visible': 8,
    'popup_position': 'cursor',  # 'cursor', 'center', 'fixed'
    'popup_transparency': 0.95,
    
    # History management
    'max_history_items': 25,
    'auto_hide_delay': 10,
    'auto_cleanup_days': 7,
    'save_on_exit': True,
    
    # Privacy settings
    'excluded_apps': [],
    'exclude_passwords': True,
    'min_text_length': 1,
    'max_text_length': 10000,
    
    # Advanced settings
    'enable_logging': True,
    'log_level': 'INFO',
    'check_updates': True,
    'start_on_login': False,
    
    # UI preferences
    'theme': 'system',  # 'system', 'light', 'dark'
    'font_size': 12,
    'show_timestamps': True,
    'show_preview': True
}

CONFIG_SCHEMA = {
    'popup_width': {
        'type': int,
        'min': 200,
        'max': 800,
        'description': 'Popup window width in pixels'
    },
    'popup_height': {
        'type': int,
        'min': 150,
        'max': 600,
        'description': 'Popup window height in pixels'
    },
    'popup_items_visible': {
        'type': int,
        'min': 3,
        'max': 20,
        'description': 'Number of clipboard items visible in popup'
    },
    'popup_position': {
        'type': str,
        'choices': ['cursor', 'center', 'fixed'],
        'description': 'Where to position the popup window'
    },
    'popup_transparency': {
        'type': float,
        'min': 0.1,
        'max': 1.0,
        'description': 'Popup window transparency (0.1 = very transparent, 1.0 = opaque)'
    },
    'max_history_items': {
        'type': int,
        'min': 5,
        'max': 100,
        'description': 'Maximum number of clipboard items to keep'
    },
    'auto_hide_delay': {
        'type': int,
        'min': 3,
        'max': 60,
        'description': 'Seconds before popup auto-hides'
    },
    'auto_cleanup_days': {
        'type': int,
        'min': 1,
        'max': 365,
        'description': 'Days after which old clipboard items are removed'
    },
    'save_on_exit': {
        'type': bool,
        'description': 'Save clipboard history when daemon exits'
    },
    'excluded_apps': {
        'type': list,
        'description': 'List of application names to exclude from clipboard monitoring'
    },
    'exclude_passwords': {
        'type': bool,
        'description': 'Exclude password fields from clipboard monitoring'
    },
    'min_text_length': {
        'type': int,
        'min': 1,
        'max': 100,
        'description': 'Minimum text length to save to clipboard history'
    },
    'max_text_length': {
        'type': int,
        'min': 100,
        'max': 100000,
        'description': 'Maximum text length to save to clipboard history'
    },
    'enable_logging': {
        'type': bool,
        'description': 'Enable application logging'
    },
    'log_level': {
        'type': str,
        'choices': ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        'description': 'Logging level'
    },
    'check_updates': {
        'type': bool,
        'description': 'Check for application updates'
    },
    'start_on_login': {
        'type': bool,
        'description': 'Start daemon automatically on user login'
    },
    'theme': {
        'type': str,
        'choices': ['system', 'light', 'dark'],
        'description': 'UI theme preference'
    },
    'font_size': {
        'type': int,
        'min': 8,
        'max': 24,
        'description': 'Font size for popup text'
    },
    'show_timestamps': {
        'type': bool,
        'description': 'Show timestamps for clipboard items'
    },
    'show_preview': {
        'type': bool,
        'description': 'Show preview of clipboard item content'
    }
}