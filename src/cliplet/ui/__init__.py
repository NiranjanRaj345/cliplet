"""User interface modules for Cliplet"""

# Import on demand to avoid circular dependencies
def get_clipboard_popup():
    """Get ClipboardPopup class"""
    from .popup import ClipboardPopup
    return ClipboardPopup

def get_settings_application():
    """Get SettingsApplication class"""
    from .settings import SettingsApplication
    return SettingsApplication

__all__ = ['get_clipboard_popup', 'get_settings_application']