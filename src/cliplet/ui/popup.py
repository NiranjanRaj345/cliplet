"""Clipboard popup window implementation"""

import logging
import os
import shutil
import subprocess
from typing import Optional

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
from gi.repository import Gtk, Gdk, GLib

# Optional gtk-layer-shell (for Wayland proper positioning/keep-above)
try:
    gi.require_version('GtkLayerShell', '0.1')
    from gi.repository import GtkLayerShell  # type: ignore
    _HAS_LAYER_SHELL = True
except Exception:
    _HAS_LAYER_SHELL = False

from ..core.clipboard import ClipboardHistory, ClipboardItem

logger = logging.getLogger(__name__)

class ClipboardPopup(Gtk.Window):
    """Lightweight popup window that appears at cursor location"""
    
    def __init__(self, history: ClipboardHistory, config):
        super().__init__()
        self.history = history
        self.config = config
        self.hide_timer: Optional[int] = None
        self.layer_shell_ready: bool = False
        
        self.setup_window()
        self.setup_ui()
        self.setup_signals()
        self.setup_theme()
        
        logger.debug("Clipboard popup initialized")
    
    def setup_window(self) -> None:
        """Setup window properties for popup"""
        self.set_decorated(False)  # No title bar
        self.set_resizable(False)
        # Modal or windowed popup based on config
        self.is_modal = bool(self.config.get('popup_modal', True))
        if self.is_modal:
            self.set_modal(True)
        else:
            self.set_modal(False)
        # Hide instead of destroying when closed
        try:
            self.set_hide_on_close(True)
        except Exception:
            pass
        self.set_default_size(
            self.config.get('popup_width', 400),
            self.config.get('popup_height', 300)
        )
        
        # GTK4 doesn't have set_type_hint, use transient_for instead
        # This will be set when showing the popup
        
        # Add CSS for styling will be done in setup_theme()
    
    def setup_theme(self) -> None:
        """Setup theme detection and CSS styling"""
        try:
            # Get the default style manager for proper theme detection
            gi.require_version('Adw', '1')
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
        
        self._setup_css()
    
    def _setup_css(self) -> None:
        """Setup CSS styling for the popup"""
        css_provider = Gtk.CssProvider()
        css_data = b"""
        .popup-window {
            border: 1px solid @borders;
            border-radius: 8px;
            background: @theme_bg_color;
            box-shadow: 0 4px 12px alpha(black, 0.3);
        }
        .clipboard-item {
            padding: 8px 12px;
            border-bottom: 1px solid alpha(@borders, 0.5);
            transition: background-color 0.2s ease;
        }
        .clipboard-item:hover {
            background: alpha(@theme_selected_bg_color, 0.1);
        }
        .clipboard-item:last-child {
            border-bottom: none;
        }
        .clipboard-preview {
            font-size: 14px;
            color: @theme_text_color;
            font-weight: 500;
        }
        .clipboard-timestamp {
            font-size: 11px;
            color: alpha(@theme_text_color, 0.7);
            margin-top: 2px;
        }
        .popup-header {
            background: @theme_bg_color;
            border-bottom: 1px solid @borders;
            padding: 8px 12px;
            border-radius: 8px 8px 0 0;
        }
        .popup-title {
            font-weight: 600;
            color: @theme_text_color;
        }
        .close-button {
            min-width: 24px;
            min-height: 24px;
            padding: 0;
            border-radius: 12px;
        }
        """
        
        try:
            css_provider.load_from_data(css_data)
            style_context = self.get_style_context()
            style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            style_context.add_class('popup-window')
        except Exception as e:
            logger.error(f"Failed to load CSS: {e}")
    
    def setup_ui(self) -> None:
        """Setup the popup UI"""
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_child(main_box)
        
        # Header
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        header.get_style_context().add_class('popup-header')
        
        title_label = Gtk.Label(label="📋 Clipboard History")
        title_label.set_halign(Gtk.Align.START)
        title_label.get_style_context().add_class('popup-title')
        header.append(title_label)
        
        # Spacer
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        header.append(spacer)
        
        # Only show close button if not modal
        if not getattr(self, "is_modal", True):
            close_btn = Gtk.Button(label="×")
            close_btn.connect('clicked', lambda x: self.hide())
            close_btn.set_halign(Gtk.Align.END)
            close_btn.get_style_context().add_class('close-button')
            header.append(close_btn)
        
        main_box.append(header)
        
        # Scrolled window for clipboard items
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        scrolled.set_min_content_height(200)
        main_box.append(scrolled)
        
        # List box for clipboard items
        self.list_box = Gtk.ListBox()
        self.list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        self.list_box.connect('row-activated', self._on_item_clicked)
        scrolled.set_child(self.list_box)
    
    def setup_signals(self) -> None:
        """Setup signal handlers"""
        # Key press events
        key_controller = Gtk.EventControllerKey()
        key_controller.connect('key-pressed', self._on_key_pressed)
        self.add_controller(key_controller)
        
        # Hide on focus loss if modal
        if getattr(self, "is_modal", True):
            focus_controller = Gtk.EventControllerFocus()
            focus_controller.connect('leave', self._on_focus_out)
            self.add_controller(focus_controller)
    
    def show_at_cursor(self) -> None:
        """Show popup directly under the cursor, or as close as possible."""
        try:
            logger.debug("Preparing to show popup at cursor")
            display = Gdk.Display.get_default()
            seat = display.get_default_seat()
            device = seat.get_pointer()
            x, y = None, None
    
            # Try to get cursor position from pointer device (Wayland/Xorg)
            try:
                surface = device.get_surface_at_position()
                if surface and hasattr(surface, 'get_root_coords'):
                    x, y = surface.get_root_coords(0, 0)
            except Exception as e:
                logger.debug(f"Failed to get cursor position: {e}")
    
            # Fallback: center of primary monitor
            if x is None or y is None:
                monitors = display.get_monitors()
                if monitors and monitors.get_n_items() > 0:
                    geometry = monitors.get_item(0).get_geometry()
                    x = geometry.width // 2
                    y = geometry.height // 2
                else:
                    x, y = 400, 300
    
            # Set window size
            popup_width = self.config.get('popup_width', 400)
            popup_height = self.config.get('popup_height', 300)
            self.set_default_size(popup_width, popup_height)
    
            # Adjust position to keep popup on screen
            if display.get_monitors().get_n_items() > 0:
                monitor = display.get_monitors().get_item(0)
                geometry = monitor.get_geometry()
                if x + popup_width > geometry.x + geometry.width:
                    x = geometry.x + geometry.width - popup_width - 20
                if y + popup_height > geometry.y + geometry.height:
                    y = geometry.y + geometry.height - popup_height - 20
                x = max(geometry.x + 20, x)
                y = max(geometry.y + 20, y)
    
            # Move window to calculated position
            try:
                self.move(x, y)
            except Exception as e:
                logger.debug(f"Failed to move popup: {e}")
    
            # Prime clipboard so first item appears even if daemon just started
            self._prime_current_clipboard()
            self.refresh_items()
            logger.debug("Presenting popup window")
            self.present()
            try:
                self.set_keep_above(True)
            except Exception:
                pass
            try:
                self.grab_focus()
            except Exception as e:
                logger.debug(f"grab_focus failed: {e}")
            self._reset_hide_timer()
            logger.debug(f"Popup shown. Visible={self.get_visible()}")
        except Exception as e:
            logger.error(f"Failed to show popup at cursor: {e}")

    def _maybe_setup_layer_shell(self) -> bool:
        """Initialize gtk-layer-shell on Wayland for proper positioning/keep-above."""
        if self.layer_shell_ready:
            return True
        if not _HAS_LAYER_SHELL or not os.environ.get("WAYLAND_DISPLAY"):
            return False
        try:
            GtkLayerShell.init_for_window(self)
            # Top layer; no reserved space; keyboard focus to interact
            GtkLayerShell.set_layer(self, GtkLayerShell.Layer.TOP)
            GtkLayerShell.set_keyboard_interactivity(self, True)
            try:
                GtkLayerShell.set_exclusive_zone(self, 0)
            except Exception:
                pass

            # Prefer monitor under pointer if available; fallback to primary
            display = Gdk.Display.get_default()
            monitor_set = False
            try:
                seat = display.get_default_seat()
                device = seat.get_pointer()
                surface = device.get_surface_at_position()
                if surface and hasattr(display, "get_monitor_at_surface"):
                    monitor = display.get_monitor_at_surface(surface)
                    if monitor:
                        GtkLayerShell.set_monitor(self, monitor)
                        monitor_set = True
            except Exception as e:
                logger.debug(f"Pointer monitor detection failed: {e}")

            if not monitor_set:
                monitors = display.get_monitors()
                if monitors and monitors.get_n_items() > 0:
                    GtkLayerShell.set_monitor(self, monitors.get_item(0))

            self.layer_shell_ready = True
            return True
        except Exception as e:
            logger.debug(f"Layer shell init failed: {e}")
            return False

    def _apply_layer_shell_position(self) -> None:
        """Center the popup on the active monitor using layer-shell margins."""
        if not self.layer_shell_ready:
            return
        try:
            # Reset anchors
            for edge in (GtkLayerShell.Edge.TOP, GtkLayerShell.Edge.BOTTOM, GtkLayerShell.Edge.LEFT, GtkLayerShell.Edge.RIGHT):
                GtkLayerShell.set_anchor(self, edge, False)

            # Desired size
            w = int(self.config.get('popup_width', 400))
            h = int(self.config.get('popup_height', 300))

            # Get geometry for pointer monitor if possible; otherwise primary
            display = Gdk.Display.get_default()
            geometry = None
            try:
                seat = display.get_default_seat()
                device = seat.get_pointer()
                surface = device.get_surface_at_position()
                if surface and hasattr(display, "get_monitor_at_surface"):
                    mon = display.get_monitor_at_surface(surface)
                    if mon:
                        geometry = mon.get_geometry()
            except Exception as e:
                logger.debug(f"Layer-shell geometry (pointer) failed: {e}")

            if geometry is None:
                monitors = display.get_monitors()
                if monitors and monitors.get_n_items() > 0:
                    geometry = monitors.get_item(0).get_geometry()

            if geometry:
                left = max(0, (geometry.width - w) // 2)
                top = max(0, (geometry.height - h) // 2)
            else:
                left, top = 200, 150

            GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, True)
            GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.LEFT, True)
            GtkLayerShell.set_margin(self, GtkLayerShell.Edge.LEFT, left)
            GtkLayerShell.set_margin(self, GtkLayerShell.Edge.TOP, top)
        except Exception as e:
            logger.debug(f"Layer shell position failed: {e}")

    def _position_at_cursor(self) -> None:
        """Position popup near cursor but ensure it's fully visible"""
        display = Gdk.Display.get_default()
        
        try:
            # Get cursor position
            seat = display.get_default_seat()
            device = seat.get_pointer()
            
            # Try to get cursor position from pointer device
            surface = device.get_surface_at_position()
            if surface and hasattr(surface, 'get_root_coords'):
                x, y = surface.get_root_coords(0, 0)
            else:
                # Fallback: center of primary monitor
                monitor = display.get_monitors().get_item(0)
                if monitor:
                    geometry = monitor.get_geometry()
                    x = geometry.width // 2
                    y = geometry.height // 2
                else:
                    x, y = 400, 300  # Default position
            
            # Get popup dimensions
            popup_width = self.config.get('popup_width', 400)
            popup_height = self.config.get('popup_height', 300)
            
            # Adjust position to keep popup on screen
            if display.get_monitors().get_n_items() > 0:
                monitor = display.get_monitors().get_item(0)
                geometry = monitor.get_geometry()
                
                # Ensure popup fits on screen
                if x + popup_width > geometry.x + geometry.width:
                    x = geometry.x + geometry.width - popup_width - 20
                if y + popup_height > geometry.y + geometry.height:
                    y = geometry.y + geometry.height - popup_height - 20
                
                # Ensure minimum position
                x = max(geometry.x + 20, x)
                y = max(geometry.y + 20, y)
            
            # Set window size
            self.set_default_size(popup_width, popup_height)
            
        except Exception as e:
            logger.error(f"Error positioning popup: {e}")
    
    def refresh_items(self) -> None:
        """Refresh the clipboard items in the popup"""
        try:
            # Always reload latest history from disk (daemon may have updated it)
            try:
                self.history.load_history()
            except Exception as e:
                logger.debug(f"History reload failed: {e}")

            # Clear existing items
            child = self.list_box.get_first_child()
            while child:
                next_child = child.get_next_sibling()
                self.list_box.remove(child)
                child = next_child
            
            # Add current items (limited for popup)
            max_items = self.config.get('popup_items_visible', 8)
            items = self.history.get_items(max_items)
            
            for i, item in enumerate(items):
                row = self._create_item_row(item, i)
                self.list_box.append(row)
            
            # Show empty message if no items
            if not items:
                empty_row = self._create_empty_row()
                self.list_box.append(empty_row)
                
            logger.debug(f"Refreshed popup with {len(items)} items")
            
        except Exception as e:
            logger.error(f"Error refreshing popup items: {e}")

    def _prime_current_clipboard(self) -> None:
        """Read current clipboard and ensure it's in history (async)."""
        try:
            clipboard = Gdk.Display.get_default().get_clipboard()
            clipboard.read_text_async(None, self._on_prime_text_ready)
        except Exception as e:
            logger.debug(f"Prime clipboard read failed: {e}")

    def _on_prime_text_ready(self, clipboard, result) -> None:
        """Handle async clipboard read and update history/UI."""
        try:
            content = clipboard.read_text_finish(result)
            if content:
                item = self.history.add_item(content, "text")
                if item:
                    GLib.idle_add(self.refresh_items)
        except Exception as e:
            logger.debug(f"Prime clipboard finish failed: {e}")
    
    def _create_item_row(self, item: ClipboardItem, index: int) -> Gtk.ListBoxRow:
        """Create a row widget for a clipboard item"""
        row = Gtk.ListBoxRow()
        row.clipboard_item = item
        row.get_style_context().add_class('clipboard-item')
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        box.set_margin_top(4)
        box.set_margin_bottom(4)
        box.set_margin_start(8)
        box.set_margin_end(8)
        
        # Preview label
        preview_label = Gtk.Label()
        preview_label.set_text(item.preview)
        preview_label.set_halign(Gtk.Align.START)
        preview_label.set_wrap(True)
        preview_label.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        preview_label.set_max_width_chars(50)
        preview_label.set_ellipsize(3)  # ELLIPSIZE_END
        preview_label.get_style_context().add_class('clipboard-preview')
        box.append(preview_label)
        
        # Timestamp label
        time_label = Gtk.Label()
        time_label.set_text(item.timestamp.strftime("%H:%M:%S"))
        time_label.set_halign(Gtk.Align.START)
        time_label.get_style_context().add_class('clipboard-timestamp')
        box.append(time_label)
        
        row.set_child(box)
        return row
    
    def _create_empty_row(self) -> Gtk.ListBoxRow:
        """Create a row for empty clipboard state"""
        row = Gtk.ListBoxRow()
        row.set_selectable(False)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        icon_label = Gtk.Label(label="📋")
        icon_label.set_halign(Gtk.Align.CENTER)
        box.append(icon_label)
        
        empty_label = Gtk.Label(label="No clipboard history")
        empty_label.set_halign(Gtk.Align.CENTER)
        empty_label.get_style_context().add_class('clipboard-timestamp')
        box.append(empty_label)
        
        row.set_child(box)
        return row
    
    def _on_item_clicked(self, list_box, row) -> None:
        """Handle clipboard item click - copy then attempt paste and close"""
        try:
            if hasattr(row, 'clipboard_item'):
                item = row.clipboard_item

                # Copy to clipboard
                self._set_clipboard_text(item.content)

                logger.debug(f"Selected clipboard item: {item.preview}")

                # Hide immediately after copy if modal
                if getattr(self, "is_modal", True):
                    self.hide()
                # Attempt paste shortly after setting clipboard, then close
                GLib.timeout_add(80, self._paste_and_close)
        except Exception as e:
            logger.error(f"Error handling item click: {e}")
    
    def _on_focus_out(self, controller) -> None:
        """Hide popup when focus is lost"""
        # Small delay to allow click to register
        GLib.timeout_add(100, self.hide)
    
    def _on_key_pressed(self, controller, keyval, keycode, state) -> bool:
        """Handle key press events"""
        if keyval == Gdk.KEY_Escape:
            self.hide()
            return True
        return False
    
    def _reset_hide_timer(self) -> None:
        """Reset the auto-hide timer (re-enabled)."""
        if self.hide_timer:
            GLib.source_remove(self.hide_timer)
        # Use 15s fallback for modal, else config value
        if getattr(self, "is_modal", True):
            delay = 15
        else:
            try:
                delay = int(self.config.get('auto_hide_delay', 30))
            except Exception:
                delay = 30
            delay = max(3, min(delay, 300))
        self.hide_timer = GLib.timeout_add_seconds(delay, self.hide)
    
    def hide(self) -> bool:
        """Hide the popup window"""
        import traceback
        try:
            if self.hide_timer:
                GLib.source_remove(self.hide_timer)
                self.hide_timer = None

            logger.debug("Popup hide called. Stack:\n" + "".join(traceback.format_stack()))
            super().hide()
            logger.debug("Popup hidden")

        except Exception as e:
            logger.error(f"Error hiding popup: {e}")

        return False  # Remove timer if called from GLib.timeout_add

    def _set_clipboard_text(self, text: str) -> None:
        """Set clipboard text using GTK4 ContentProvider with CLI fallbacks."""
        try:
            # GTK4 way: ContentProvider
            try:
                fmt = Gdk.ContentFormat.new_mime_type("text/plain;charset=utf-8")
            except Exception:
                # Fallback to plain text if charset not accepted
                fmt = Gdk.ContentFormat.new_mime_type("text/plain")
            provider = Gdk.ContentProvider.new_for_bytes(fmt, GLib.Bytes.new(text.encode("utf-8")))
            clipboard = Gdk.Display.get_default().get_clipboard()
            clipboard.set(provider)
            logger.debug("Clipboard set via Gdk.ContentProvider")
            return
        except Exception as e:
            logger.debug(f"Gdk clipboard set failed: {e}")

        # CLI fallbacks
        try:
            if shutil.which("wl-copy"):
                subprocess.run(["wl-copy"], input=text.encode("utf-8"), check=False)
                logger.debug("Clipboard set via wl-copy")
                return
            if shutil.which("xclip"):
                subprocess.run(["xclip", "-selection", "clipboard"], input=text.encode("utf-8"), check=False)
                logger.debug("Clipboard set via xclip")
                return
        except Exception as e:
            logger.debug(f"CLI clipboard fallback failed: {e}")

        logger.error("Failed to set clipboard text via all methods")

    def _paste_and_close(self) -> bool:
        """Try to paste into the active application if possible, then close.
        On Wayland/Xorg, return focus first (by hiding), then emit Ctrl+V with a slight delay.
        """
        is_wayland = bool(os.environ.get("WAYLAND_DISPLAY"))

        # Hide first to give focus back
        try:
            self.hide()
        except Exception:
            pass

        try:
            if is_wayland and shutil.which("wtype"):
                subprocess.Popen(["bash", "-lc", "sleep 0.12; wtype -M ctrl v -m ctrl"], start_new_session=True)
                logger.debug("Scheduled paste via wtype after hide")
            elif shutil.which("xdotool"):
                subprocess.Popen(["bash", "-lc", "sleep 0.08; xdotool key --clearmodifiers ctrl+v"], start_new_session=True)
                logger.debug("Scheduled paste via xdotool after hide")
            else:
                logger.info("No paste tool available (wtype for Wayland or xdotool for Xorg)")
        except Exception as e:
            logger.debug(f"Paste scheduling failed: {e}")

        return False  # one-shot timer

    def cleanup(self) -> None:
        """Clean up resources"""
        if self.hide_timer:
            GLib.source_remove(self.hide_timer)
            self.hide_timer = None