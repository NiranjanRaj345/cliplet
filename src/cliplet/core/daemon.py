"""Main clipboard daemon implementation"""

import logging
import signal
import sys
from typing import Optional

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib

from ..config import ConfigManager
from ..utils.logging import get_logger
from .clipboard import ClipboardHistory, ClipboardMonitor
from ..ui.popup import ClipboardPopup

logger = get_logger(__name__)

class ClipboardDaemon:
    """Main lightweight background daemon"""
    
    def __init__(self, config: Optional[ConfigManager] = None):
        """Initialize the clipboard daemon
        
        Args:
            config: Optional configuration manager instance
        """
        self.config = config or ConfigManager()
        self.history: Optional[ClipboardHistory] = None
        self.monitor: Optional[ClipboardMonitor] = None
        self.popup: Optional[ClipboardPopup] = None
        self.main_loop: Optional[GLib.MainLoop] = None
        self.running = False
        
        self._initialize_components()
        self._setup_signal_handlers()
        
        logger.info("Clipboard daemon initialized")
    
    def _initialize_components(self) -> None:
        """Initialize all daemon components"""
        try:
            # Initialize clipboard history
            self.history = ClipboardHistory(self.config)
            logger.debug(f"Loaded {len(self.history.items)} clipboard items")
            
            # Initialize clipboard monitor
            self.monitor = ClipboardMonitor(self.history, self.config)
            self.monitor.add_callback(self._on_clipboard_changed)
            logger.info("All daemon components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize daemon components: {e}")
            raise
    
    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down gracefully...")
            self.stop()
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGHUP, lambda s, f: self.reload_config())
    
    def start(self) -> None:
        """Start the daemon components"""
        try:
            if self.running:
                logger.warning("Daemon is already running")
                return
            
            # Start clipboard monitoring
            if self.monitor:
                self.monitor.start_monitoring()
            
            self.running = True
            
            logger.info("Clipboard daemon started successfully")
            logger.info(f"History: {len(self.history.items)} items loaded")
            
        except Exception as e:
            logger.error(f"Failed to start daemon: {e}")
            raise
    
    def stop(self) -> None:
        """Stop the daemon and cleanup resources"""
        try:
            if not self.running:
                return
            
            self.running = False
            
            # Stop clipboard monitoring
            if self.monitor:
                self.monitor.stop_monitoring()
                
            # Hide popup if visible
            if self.popup:
                self.popup.cleanup()
                self.popup = None
            
            # Stop main loop
            if self.main_loop and self.main_loop.is_running():
                self.main_loop.quit()
            
            logger.info("Clipboard daemon stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping daemon: {e}")
    
    def run(self) -> None:
        """Run the daemon main loop"""
        try:
            self.start()
            
            # Create and run main loop
            self.main_loop = GLib.MainLoop()
            
            logger.info("Starting daemon main loop...")
            self.main_loop.run()
            
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Error in daemon main loop: {e}")
            raise
        finally:
            self.stop()
    
    def show_popup(self) -> None:
        """Show the clipboard popup"""
        try:
            # Create popup window if it doesn't exist
            if not self.popup:
                self.popup = ClipboardPopup(self.history, self.config)
            
            # Show popup at cursor location
            self.popup.show_at_cursor()
            
            logger.debug("Clipboard popup shown")
            
        except Exception as e:
            logger.error(f"Failed to show popup: {e}")
    
    def reload_config(self) -> None:
        """Reload configuration and update components"""
        try:
            logger.info("Reloading configuration...")
            self.config.load()
            
            # Update history max items
            if self.history:
                self.history.max_items = self.config.get('max_history_items', 25)
            
            logger.info("Configuration reloaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to reload configuration: {e}")
    
    def _on_clipboard_changed(self, item) -> None:
        """Handle clipboard change notification"""
        logger.debug(f"Clipboard changed: {item.preview}")
        
        # Could add additional processing here
        # For example, sending notifications, filtering, etc.
    
    def get_status(self) -> dict:
        """Get daemon status information
        
        Returns:
            dict: Status information
        """
        return {
            'running': self.running,
            'history_items': len(self.history.items) if self.history else 0,
            'monitoring': self.monitor.monitoring if self.monitor else False,
            'config_loaded': self.config.is_loaded() if self.config else False
        }
    
    def clear_history(self) -> None:
        """Clear clipboard history"""
        if self.history:
            self.history.clear_history()
            logger.info("Clipboard history cleared")
    
    def get_history_items(self, limit: Optional[int] = None) -> list:
        """Get clipboard history items
        
        Args:
            limit: Maximum number of items to return
            
        Returns:
            list: List of clipboard items
        """
        if self.history:
            return [item.to_dict() for item in self.history.get_items(limit)]
        return []


class DaemonError(Exception):
    """Custom exception for daemon errors"""
    pass


def main():
    """Main entry point for the daemon"""
    try:
        # Initialize configuration and logging
        config = ConfigManager()
        
        # Create and run daemon
        daemon = ClipboardDaemon(config)
        daemon.run()
        
    except KeyboardInterrupt:
        logger.info("Daemon interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal daemon error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()