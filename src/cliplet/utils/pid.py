"""PID file management for daemon processes"""

import os
import signal
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class PidManagerError(Exception):
    """Raised when PID management operations fail"""
    pass

class PidManager:
    """Professional PID file manager for daemon processes"""
    
    def __init__(self, pid_file: Path):
        """Initialize PID manager
        
        Args:
            pid_file: Path to PID file
        """
        self.pid_file = Path(pid_file)
        
    def create(self) -> None:
        """Create PID file with current process ID
        
        Raises:
            PidManagerError: If PID file creation fails
        """
        try:
            # Ensure directory exists
            self.pid_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if already running
            if self.is_running():
                existing_pid = self.get_pid()
                raise PidManagerError(f"Process already running with PID {existing_pid}")
            
            # Write current PID
            with open(self.pid_file, 'w') as f:
                f.write(str(os.getpid()))
            
            logger.debug(f"PID file created: {self.pid_file}")
            
        except (OSError, PermissionError) as e:
            raise PidManagerError(f"Failed to create PID file: {e}")
    
    def remove(self) -> None:
        """Remove PID file
        
        Raises:
            PidManagerError: If PID file removal fails
        """
        try:
            if self.pid_file.exists():
                self.pid_file.unlink()
                logger.debug(f"PID file removed: {self.pid_file}")
        except OSError as e:
            raise PidManagerError(f"Failed to remove PID file: {e}")
    
    def get_pid(self) -> Optional[int]:
        """Get PID from PID file
        
        Returns:
            Process ID or None if file doesn't exist or is invalid
        """
        try:
            if self.pid_file.exists():
                with open(self.pid_file, 'r') as f:
                    pid_str = f.read().strip()
                    return int(pid_str)
        except (OSError, ValueError):
            pass
        return None
    
    def is_running(self) -> bool:
        """Check if process is running
        
        Returns:
            True if process is running, False otherwise
        """
        pid = self.get_pid()
        if pid is None:
            return False
        
        try:
            # Send signal 0 to check if process exists
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            # Process doesn't exist, remove stale PID file
            try:
                self.remove()
            except PidManagerError:
                pass
            return False
    
    def stop_process(self, timeout: int = 10) -> bool:
        """Stop the process gracefully
        
        Args:
            timeout: Seconds to wait for graceful shutdown
            
        Returns:
            True if process stopped, False otherwise
        """
        pid = self.get_pid()
        if pid is None:
            return True
        
        try:
            # Send SIGTERM for graceful shutdown
            os.kill(pid, signal.SIGTERM)
            logger.info(f"Sent SIGTERM to process {pid}")
            
            # Wait for process to exit
            import time
            for _ in range(timeout):
                if not self.is_running():
                    logger.info(f"Process {pid} stopped gracefully")
                    return True
                time.sleep(1)
            
            # Force kill if still running
            if self.is_running():
                os.kill(pid, signal.SIGKILL)
                logger.warning(f"Force killed process {pid}")
                
                # Wait a bit more
                time.sleep(2)
                if not self.is_running():
                    return True
            
        except (OSError, ProcessLookupError):
            # Process already dead
            pass
        
        return not self.is_running()
    
    def reload_process(self) -> bool:
        """Send reload signal to process
        
        Returns:
            True if signal sent successfully
        """
        pid = self.get_pid()
        if pid is None:
            return False
        
        try:
            os.kill(pid, signal.SIGHUP)
            logger.info(f"Sent SIGHUP to process {pid}")
            return True
        except (OSError, ProcessLookupError):
            return False
    
    def get_status(self) -> dict:
        """Get process status information
        
        Returns:
            Dictionary with status information
        """
        pid = self.get_pid()
        status = {
            'pid_file': str(self.pid_file),
            'pid': pid,
            'running': False,
            'exists': self.pid_file.exists()
        }
        
        if pid:
            status['running'] = self.is_running()
            
            if status['running']:
                try:
                    # Get additional process info
                    import psutil
                    process = psutil.Process(pid)
                    status.update({
                        'name': process.name(),
                        'status': process.status(),
                        'memory_percent': process.memory_percent(),
                        'cpu_percent': process.cpu_percent(),
                        'create_time': process.create_time()
                    })
                except (ImportError, psutil.NoSuchProcess):
                    pass
        
        return status