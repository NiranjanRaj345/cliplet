#!/usr/bin/env python3
"""Settings application for Cliplet"""

import gi
gi.require_version('Gtk', '4.0')

import sys
import logging
from pathlib import Path

from gi.repository import Gtk, Gio

from ..config import ConfigManager

logger = logging.getLogger(__name__)


class SettingsWindow(Gtk.ApplicationWindow):
    """Settings window for clipboard manager"""
    
    def __init__(self, app):
        super().__init__(application=app)
        self.config = ConfigManager()
        
        self.set_title("Cliplet Settings")
        self.set_default_size(500, 450)
        
        self.setup_ui()
        self.setup_theme()
        self.load_settings()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Apply theme class
        style_context = self.get_style_context()
        style_context.add_class('settings-window')
        
        # Add CSS styling
        css_provider = Gtk.CssProvider()
        css_data = b"""
        .settings-window {
            background: @theme_bg_color;
        }
        .settings-window .title {
            font-weight: bold;
            color: @theme_text_color;
        }
        .card {
            background: alpha(@theme_fg_color, 0.05);
            border: 1px solid @borders;
            border-radius: 8px;
            padding: 12px;
        }
        .heading {
            font-weight: bold;
            font-size: 16px;
            margin-bottom: 8px;
            color: @theme_text_color;
        }
        """
        css_provider.load_from_data(css_data)
        style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        
        # Create header bar
        header_bar = Gtk.HeaderBar()
        title_label = Gtk.Label(label="Clipboard Settings")
        title_label.add_css_class('title')
        header_bar.set_title_widget(title_label)
        
        # Add apply and close buttons
        apply_btn = Gtk.Button(label="Apply")
        apply_btn.add_css_class('suggested-action')
        apply_btn.connect('clicked', self._on_apply)
        header_bar.pack_end(apply_btn)
        
        self.set_titlebar(header_bar)
        
        # Create main content
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_child(main_box)
        
        # Create scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        main_box.append(scrolled)
        
        # Create settings content
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        content_box.set_margin_top(18)
        content_box.set_margin_bottom(18)
        content_box.set_margin_start(18)
        content_box.set_margin_end(18)
        scrolled.set_child(content_box)
        
        # Hotkey settings
        hotkey_group = self.create_hotkey_settings()
        content_box.append(hotkey_group)
        
        # Popup settings
        popup_group = self.create_popup_settings()
        content_box.append(popup_group)
        
        # History settings
        history_group = self.create_history_settings()
        content_box.append(history_group)
        
        # Privacy settings
        privacy_group = self.create_privacy_settings()
        content_box.append(privacy_group)
    
    def setup_theme(self) -> None:
        """Setup theme detection and CSS styling"""
        try:
            # Get the default style manager for proper theme detection
            from gi.repository import Adw
            Adw.init()
            style_manager = Adw.StyleManager.get_default()
            
            # Force dark theme detection
            if style_manager.get_system_supports_color_schemes():
                if style_manager.get_color_scheme() == Adw.ColorScheme.PREFER_DARK:
                    style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
                
        except ImportError:
            # Fallback if Adwaita is not available
            logger.info("Adwaita not available, using basic theme detection")
    
    def create_hotkey_settings(self):
        """Create keyboard shortcut info group"""
        group = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        
        # Group title
        title = Gtk.Label(label="Keyboard Shortcut")
        title.set_halign(Gtk.Align.START)
        title.add_css_class('heading')
        group.append(title)
        
        # Card container
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        card.add_css_class('card')
        card.set_margin_top(8)
        card.set_margin_bottom(8)
        card.set_margin_start(12)
        card.set_margin_end(12)
        group.append(card)
        
        # Info box
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        info_label = Gtk.Label(
            label="Configure keyboard shortcuts in your system settings:\n\n" +
                  "• GNOME: Settings → Keyboard → View and Customize Shortcuts\n" +
                  "• KDE: System Settings → Shortcuts\n" +
                  "• XFCE: Keyboard Settings → Application Shortcuts\n\n" +
                  "Recommended shortcuts:\n" +
                  "• Ctrl+Alt+V (most reliable)\n" +
                  "• Alt+Space\n" +
                  "• F12"
        )
        info_label.set_halign(Gtk.Align.START)
        info_label.set_wrap(True)
        info_box.append(info_label)
        
        setup_btn = Gtk.Button(label="Run Shortcut Setup")
        setup_btn.connect('clicked', self._on_setup_shortcut)
        setup_btn.set_halign(Gtk.Align.START)
        setup_btn.add_css_class('suggested-action')
        info_box.append(setup_btn)
        
        card.append(info_box)
        
        return group
    
    def _on_setup_shortcut(self, button):
        """Launch the keyboard shortcut setup script"""
        try:
            import subprocess
            import shutil
            
            # Try to find the setup script in multiple locations
            script_name = "setup-keyboard-shortcut.sh"
            script_path = None
            
            # Check if installed system-wide
            system_script = f"/usr/local/share/cliplet/scripts/{script_name}"
            if Path(system_script).exists():
                script_path = system_script
            else:
                # Look for it in the source directory (development)
                dev_script = Path(__file__).parent.parent.parent.parent / "scripts" / script_name
                if dev_script.exists():
                    script_path = str(dev_script)
            
            if script_path:
                subprocess.Popen(["/bin/bash", script_path])
                logger.info("Launched keyboard shortcut setup")
            else:
                logger.error(f"Setup script not found in expected locations")
                # Show instructions instead
                dialog = Gtk.MessageDialog(
                    transient_for=self,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK,
                    text="Setup script not found.\n\nPlease run the setup manually:\n./scripts/setup-keyboard-shortcut.sh"
                )
                dialog.present()
        except Exception as e:
            logger.error(f"Failed to launch shortcut setup: {e}")
    
    def create_popup_settings(self):
        """Create popup appearance settings"""
        group = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        
        # Group title
        title = Gtk.Label(label="Popup Appearance")
        title.set_halign(Gtk.Align.START)
        title.add_css_class('heading')
        group.append(title)
        
        # Card container
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        card.add_css_class('card')
        card.set_margin_top(8)
        card.set_margin_bottom(8)
        card.set_margin_start(12)
        card.set_margin_end(12)
        group.append(card)
        
        # Popup width
        width_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        width_label = Gtk.Label(label="Popup width")
        width_label.set_halign(Gtk.Align.START)
        width_label.set_hexpand(True)
        self.width_spin = Gtk.SpinButton()
        self.width_spin.set_range(250, 600)
        self.width_spin.set_increments(25, 50)
        width_box.append(width_label)
        width_box.append(self.width_spin)
        card.append(width_box)
        
        # Popup height
        height_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        height_label = Gtk.Label(label="Popup height")
        height_label.set_halign(Gtk.Align.START)
        height_label.set_hexpand(True)
        self.height_spin = Gtk.SpinButton()
        self.height_spin.set_range(200, 600)
        self.height_spin.set_increments(25, 50)
        height_box.append(height_label)
        height_box.append(self.height_spin)
        card.append(height_box)
        
        # Visible items
        items_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        items_label = Gtk.Label(label="Items visible in popup")
        items_label.set_halign(Gtk.Align.START)
        items_label.set_hexpand(True)
        self.items_spin = Gtk.SpinButton()
        self.items_spin.set_range(3, 15)
        self.items_spin.set_increments(1, 2)
        items_box.append(items_label)
        items_box.append(self.items_spin)
        card.append(items_box)

        # Popup modal toggle
        modal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        modal_label = Gtk.Label(label="Show popup as modal overlay")
        modal_label.set_halign(Gtk.Align.START)
        modal_label.set_hexpand(True)
        self.modal_switch = Gtk.Switch()
        modal_box.append(modal_label)
        modal_box.append(self.modal_switch)
        card.append(modal_box)

        # Theme preference toggle
        theme_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        theme_label = Gtk.Label(label="Theme preference")
        theme_label.set_halign(Gtk.Align.START)
        theme_label.set_hexpand(True)
        self.theme_combo = Gtk.ComboBoxText()
        self.theme_combo.append_text("GTK Default")
        self.theme_combo.append_text("Light")
        self.theme_combo.append_text("Dark")
        theme_box.append(theme_label)
        theme_box.append(self.theme_combo)
        card.append(theme_box)
        
        return group
    
    def create_history_settings(self):
        """Create history management settings"""
        group = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        
        # Group title
        title = Gtk.Label(label="History Management")
        title.set_halign(Gtk.Align.START)
        title.add_css_class('heading')
        group.append(title)
        
        # Card container
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        card.add_css_class('card')
        card.set_margin_top(8)
        card.set_margin_bottom(8)
        card.set_margin_start(12)
        card.set_margin_end(12)
        group.append(card)
        
        # Max history items
        max_items_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        max_items_label = Gtk.Label(label="Maximum clipboard items to keep")
        max_items_label.set_halign(Gtk.Align.START)
        max_items_label.set_hexpand(True)
        self.max_items_spin = Gtk.SpinButton()
        self.max_items_spin.set_range(5, 100)
        self.max_items_spin.set_increments(5, 10)
        max_items_box.append(max_items_label)
        max_items_box.append(self.max_items_spin)
        card.append(max_items_box)
        
        # Auto cleanup
        cleanup_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        cleanup_label = Gtk.Label(label="Auto-cleanup after (days)")
        cleanup_label.set_halign(Gtk.Align.START)
        cleanup_label.set_hexpand(True)
        self.cleanup_spin = Gtk.SpinButton()
        self.cleanup_spin.set_range(1, 30)
        self.cleanup_spin.set_increments(1, 7)
        cleanup_box.append(cleanup_label)
        cleanup_box.append(self.cleanup_spin)
        card.append(cleanup_box)
        
        # Clear history button
        clear_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        clear_label = Gtk.Label(label="Clear all clipboard history")
        clear_label.set_halign(Gtk.Align.START)
        clear_label.set_hexpand(True)
        clear_btn = Gtk.Button(label="Clear History")
        clear_btn.add_css_class('destructive-action')
        clear_btn.connect('clicked', self._on_clear_history)
        clear_box.append(clear_label)
        clear_box.append(clear_btn)
        card.append(clear_box)
        
        return group
    
    def create_privacy_settings(self):
        """Create privacy settings"""
        group = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        
        # Group title
        title = Gtk.Label(label="Privacy Controls")
        title.set_halign(Gtk.Align.START)
        title.add_css_class('heading')
        group.append(title)
        
        # Card container
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        card.add_css_class('card')
        card.set_margin_top(8)
        card.set_margin_bottom(8)
        card.set_margin_start(12)
        card.set_margin_end(12)
        group.append(card)
        
        # Excluded apps label
        excluded_label = Gtk.Label(label="Excluded applications (one per line)")
        excluded_label.set_halign(Gtk.Align.START)
        card.append(excluded_label)
        
        # Text view for excluded apps
        scrolled_text = Gtk.ScrolledWindow()
        scrolled_text.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_text.set_size_request(-1, 100)
        
        self.excluded_text = Gtk.TextView()
        self.excluded_text.set_wrap_mode(Gtk.WrapMode.WORD)
        scrolled_text.set_child(self.excluded_text)
        card.append(scrolled_text)
        
        return group
    
    def load_settings(self):
        """Load current settings into the UI"""
        # Popup settings
        self.width_spin.set_value(self.config.get('popup_width'))
        self.height_spin.set_value(self.config.get('popup_height'))
        self.items_spin.set_value(self.config.get('popup_items_visible'))
        self.modal_switch.set_active(bool(self.config.get('popup_modal', True)))
        theme_pref = self.config.get('theme', 'system')
        if theme_pref == 'system':
            self.theme_combo.set_active(0)
        elif theme_pref == 'light':
            self.theme_combo.set_active(1)
        elif theme_pref == 'dark':
            self.theme_combo.set_active(2)
        else:
            self.theme_combo.set_active(0)
        
        # History settings
        self.max_items_spin.set_value(self.config.get('max_history_items'))
        self.cleanup_spin.set_value(self.config.get('auto_cleanup_days'))
        self.items_spin.set_value(self.config.get('popup_items_visible'))
        self.width_spin.set_value(self.config.get('popup_width'))
        self.height_spin.set_value(self.config.get('popup_height'))
        self.hide_spin.set_value(self.config.get('auto_hide_delay'))
        
        # Privacy settings
        excluded_apps = self.config.get('excluded_apps')
        buffer = self.excluded_text.get_buffer()
        buffer.set_text('\n'.join(excluded_apps))
    
    def save_settings(self):
        """Save settings from the UI to config"""
        # Popup settings
        self.config.set('popup_width', int(self.width_spin.get_value()))
        self.config.set('popup_height', int(self.height_spin.get_value()))
        self.config.set('popup_items_visible', int(self.items_spin.get_value()))
        self.config.set('popup_modal', bool(self.modal_switch.get_active()))
        theme_idx = self.theme_combo.get_active()
        if theme_idx == 0:
            self.config.set('theme', 'system')
        elif theme_idx == 1:
            self.config.set('theme', 'light')
        elif theme_idx == 2:
            self.config.set('theme', 'dark')
        else:
            self.config.set('theme', 'system')
        
        # History settings
        self.config.set('max_history_items', int(self.max_items_spin.get_value()))
        self.config.set('auto_cleanup_days', int(self.cleanup_spin.get_value()))
        self.config.set('popup_items_visible', int(self.items_spin.get_value()))
        self.config.set('popup_width', int(self.width_spin.get_value()))
        self.config.set('popup_height', int(self.height_spin.get_value()))
        self.config.set('auto_hide_delay', int(self.hide_spin.get_value()))
        
        # Privacy settings
        buffer = self.excluded_text.get_buffer()
        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()
        text = buffer.get_text(start_iter, end_iter, False)
        excluded_apps = [app.strip() for app in text.split('\n') if app.strip()]
        self.config.set('excluded_apps', excluded_apps)
        
        # Save the configuration
        self.config.save()
    
    def _on_apply(self, button):
        """Handle apply button click"""
        try:
            self.save_settings()
            logger.info("Settings saved successfully")
            print("✅ Settings saved successfully!")
            self.close()
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            print(f"❌ Failed to save settings: {e}")
    
    def _on_clear_history(self, button):
        """Handle clear history button"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Clear all clipboard history?\n\nThis action cannot be undone."
        )
        
        dialog.connect('response', self._on_clear_confirm)
        dialog.present()
    
    def _on_clear_confirm(self, dialog, response):
        """Handle clear history confirmation"""
        if response == Gtk.ResponseType.YES:
            try:
                # Clear history using the config manager
                self.config.clear_history()
                logger.info("Clipboard history cleared")
                print("✅ Clipboard history cleared successfully!")
            except Exception as e:
                logger.error(f"Failed to clear history: {e}")
                print(f"❌ Failed to clear history: {e}")
        
        dialog.destroy()


class SettingsApplication(Gtk.Application):
    """Settings application"""
    
    def __init__(self, config=None):
        super().__init__(application_id="org.cliplet.settings")
        self.config = config
        self.connect('activate', self._on_activate)
    
    def _on_activate(self, app):
        """Handle application activation"""
        window = SettingsWindow(self)
        if self.config:
            window.config = self.config
        window.present()


def main():
    """Main entry point for settings app"""
    app = SettingsApplication()
    return app.run(sys.argv)


if __name__ == "__main__":
    main()