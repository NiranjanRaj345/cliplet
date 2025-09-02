# Troubleshooting Guide

This guide helps you resolve common issues with Cliplet.

## Common Issues

### Installation Issues

#### **Issue: Permission denied during installation**
```bash
Permission denied: /usr/local/bin/clipletd
```
**Solution:**
```bash
# Use sudo for system-wide installation
sudo ./scripts/install.sh
```

#### **Issue: Missing dependencies**
```bash
ImportError: cannot import name 'Gtk' from 'gi'
```
**Solutions:**
```bash
# Fedora/RHEL/CentOS
sudo dnf install python3-gobject-base python3-gobject libadwaita-devel

# Ubuntu/Debian
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 libadwaita-1-dev

# Arch Linux
sudo pacman -S python-gobject gtk4 libadwaita
```

---

### Runtime Issues

#### **Issue: Daemon won't start**
```bash
Failed to start cliplet.service
```
**Solutions:**
1. Check service status:
   ```bash
   systemctl --user status cliplet.service
   ```

2. Check logs:
   ```bash
   journalctl --user -u cliplet.service -f
   ```

3. Try starting in foreground to see errors:
   ```bash
   ./bin/clipletd --foreground
   ```

#### **Issue: Popup doesn't appear with keyboard shortcut**
**Solutions:**
1. Verify keyboard shortcut is configured:
   ```bash
   ./scripts/setup-keyboard-shortcut.sh
   ```

2. Test popup manually:
   ```bash
   ./bin/cliplet-popup
   ```

3. Check if daemon is running:
   ```bash
   ps aux | grep clipletd
   ```

#### **Issue: Dark theme not working**
**Solutions:**
1. Install libadwaita:
   ```bash
   # Fedora
   sudo dnf install libadwaita-devel
   
   # Ubuntu
   sudo apt install libadwaita-1-dev
   ```

2. Check system theme setting:
   ```bash
   gsettings get org.gnome.desktop.interface color-scheme
   ```

---

### Configuration Issues

#### **Issue: Settings not saving**
**Solutions:**
1. Check config directory permissions:
   ```bash
   ls -la ~/.config/cliplet/
   ```

2. Reset configuration:
   ```bash
   ./bin/cliplet-settings --reset
   ```

3. Check for config file corruption:
   ```bash
   cat ~/.config/cliplet/config.json
   ```

#### **Issue: Clipboard history not working**
**Solutions:**
1. Check clipboard monitoring:
   ```bash
   # Copy something to clipboard, then check logs
   tail -f ~/.local/share/cliplet/logs/cliplet.log
   ```

2. Verify data directory:
   ```bash
   ls -la ~/.local/share/cliplet/
   ```

---

## Diagnostic Commands

### System Information
```bash
# Check GTK version
pkg-config --modversion gtk4

# Check Python modules
python3 -c "import gi; gi.require_version('Gtk', '4.0'); print('GTK4 OK')"
python3 -c "import gi; gi.require_version('Adw', '1'); print('Adwaita OK')"

# Check service status
systemctl --user is-active cliplet.service
systemctl --user is-enabled cliplet.service
```

### Log Locations
- **Service logs**: `journalctl --user -u cliplet.service`
- **Application logs**: `~/.local/share/cliplet/logs/cliplet.log`
- **Configuration**: `~/.config/cliplet/config.json`
- **Data**: `~/.local/share/cliplet/history.json`

---

## Reset and Recovery

### Complete Reset
```bash
# Stop service
systemctl --user stop cliplet.service

# Reset configuration
./bin/cliplet-settings --reset

# Clear all data
rm -rf ~/.config/cliplet/
rm -rf ~/.local/share/cliplet/
rm -rf ~/.cache/cliplet/

# Restart service
systemctl --user start cliplet.service
```

### Reinstallation
```bash
# Complete uninstall
sudo ./scripts/uninstall.sh

# Clean installation
sudo ./scripts/install.sh

# Reconfigure shortcuts
./scripts/setup-keyboard-shortcut.sh
```

---

## Getting Help

### Bug Reports
When reporting bugs, please include:
1. **System information**:
   ```bash
   uname -a
   lsb_release -a  # or cat /etc/os-release
   python3 --version
   ```

2. **Error logs**:
   ```bash
   journalctl --user -u cliplet.service --since="1 hour ago"
   ```

3. **Configuration**:
   ```bash
   cat ~/.config/cliplet/config.json
   ```

### Community Support
- **GitHub Issues**: [Project Issues Page]
- **Documentation**: Check `docs/` folder
- **Examples**: See `README.md` for common usage patterns

---

## Performance Tips

### Optimize Memory Usage
```bash
# Reduce history size in settings
./bin/cliplet-settings

# Or edit config directly
vim ~/.config/cliplet/config.json
# Set "max_history_items": 25
```

### Reduce CPU Usage
- Set longer auto-cleanup periods
- Exclude resource-heavy applications
- Adjust popup display timeout

---

## Security Considerations

### Privacy Settings
- Configure excluded applications for sensitive data
- Set appropriate history retention periods
- Consider disabling clipboard monitoring for specific applications

### File Permissions
```bash
# Verify secure permissions
ls -la ~/.config/cliplet/
ls -la ~/.local/share/cliplet/

# Should be user-readable only (600)
chmod 600 ~/.config/cliplet/config.json
chmod 600 ~/.local/share/cliplet/history.json