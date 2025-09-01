# Configuration Guide

Complete guide to configuring Cliplet for your needs.

## Configuration Files

### Primary Configuration
- **Location**: `~/.config/cliplet/config.json`
- **Format**: JSON
- **Auto-created**: Yes (on first run)

### Data Files
- **History**: `~/.local/share/cliplet/history.json`
- **Logs**: `~/.local/share/cliplet/logs/cliplet.log`
- **Cache**: `~/.cache/cliplet/`

---

## Configuration Options

### GUI Configuration (Recommended)
```bash
# Open settings GUI
cliplet-settings

# Or run from project directory
./bin/cliplet-settings
```

### Manual Configuration
Edit `~/.config/cliplet/config.json`:

```json
{
  "popup_width": 400,
  "popup_height": 300,
  "popup_items_visible": 8,
  "max_history_items": 50,
  "auto_cleanup_days": 7,
  "auto_hide_delay": 10,
  "excluded_apps": [
    "gnome-keyring",
    "keepassxc",
    "bitwarden"
  ],
  "log_level": "INFO",
  "monitor_clipboard": true
}
```

---

## Interface Settings

### Popup Window
| Setting | Description | Default | Range |
|---------|-------------|---------|-------|
| `popup_width` | Popup window width (pixels) | 400 | 250-600 |
| `popup_height` | Popup window height (pixels) | 300 | 200-600 |
| `popup_items_visible` | Number of items shown | 8 | 3-15 |
| `auto_hide_delay` | Auto-hide timeout (seconds) | 10 | 1-60 |

**Example:**
```json
{
  "popup_width": 500,
  "popup_height": 400,
  "popup_items_visible": 10,
  "auto_hide_delay": 15
}
```

### Theme Settings
Cliplet automatically detects your system theme (light/dark) when libadwaita is installed.

**Manual theme override** (if needed):
```bash
# Force dark theme
export GTK_THEME=Adwaita:dark

# Force light theme  
export GTK_THEME=Adwaita:light
```

---

## History Management

### History Settings
| Setting | Description | Default | Range |
|---------|-------------|---------|-------|
| `max_history_items` | Maximum items to keep | 50 | 10-100 |
| `auto_cleanup_days` | Days before auto-deletion | 7 | 1-30 |

### Manual History Operations
```bash
# Clear all history via GUI
cliplet-settings  # Use "Clear History" button

# Clear via command line
cliplet-settings --reset

# Export configuration
cliplet-settings --export ~/cliplet-backup.json

# Import configuration
cliplet-settings --import ~/cliplet-backup.json
```

---

## Privacy Controls

### Application Exclusions
Prevent clipboard monitoring for sensitive applications:

```json
{
  "excluded_apps": [
    "gnome-keyring",
    "keepassxc", 
    "bitwarden",
    "1password",
    "lastpass",
    "gnome-terminal",
    "konsole"
  ]
}
```

### Common Excluded Applications
- **Password Managers**: `keepassxc`, `bitwarden`, `1password`, `lastpass`
- **Secure Terminals**: Add terminal apps if handling sensitive data
- **Banking Apps**: Add financial applications
- **Development**: Add IDEs when working with API keys

---

## Keyboard Shortcuts

### System Integration
Cliplet uses **system-level keyboard shortcuts** (not app-level hotkeys).

### Setup Process
```bash
# Interactive setup wizard
./scripts/setup-keyboard-shortcut.sh
```

### Manual Setup
1. **Get popup command path**:
   ```bash
   ./bin/cliplet-popup --show-path
   ```

2. **Configure in system settings**:
   - **GNOME**: Settings → Keyboard → View and Customize Shortcuts
   - **KDE**: System Settings → Shortcuts
   - **XFCE**: Keyboard Settings → Application Shortcuts

3. **Recommended key combinations**:
   - `Ctrl+Alt+V` (most reliable)
   - `Super+V`
   - `Alt+Space`
   - `F12`

### Desktop Environment Specific

#### GNOME
```bash
# Command line setup
gsettings set org.gnome.settings-daemon.plugins.media-keys custom-keybindings \
  "['/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/cliplet/']"

gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/cliplet/ \
  name 'Cliplet Popup'

gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/cliplet/ \
  command '/usr/local/bin/cliplet-popup'

gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/cliplet/ \
  binding '<Ctrl><Alt>v'
```

#### KDE
```bash
# Using kwriteconfig5
kwriteconfig5 --file kglobalshortcutsrc --group cliplet-popup --key _launch 'Ctrl+Alt+V,none,Show Cliplet Popup'
```

---

## Advanced Configuration

### Logging
| Level | Description | When to Use |
|-------|-------------|-------------|
| `DEBUG` | Detailed debugging info | Development/troubleshooting |
| `INFO` | General information | Normal operation (default) |
| `WARNING` | Warning messages | Production |
| `ERROR` | Error messages only | Minimal logging |
| `CRITICAL` | Critical errors only | Emergency situations |

```json
{
  "log_level": "INFO",
  "log_file": "~/.local/share/cliplet/logs/cliplet.log"
}
```

### Performance Tuning
```json
{
  "monitor_clipboard": true,
  "check_interval": 1.0,
  "max_content_length": 10000,
  "enable_notifications": false
}
```

### Service Configuration
Edit systemd service: `~/.config/systemd/user/cliplet.service`

```ini
[Unit]
Description=Cliplet Daemon
After=graphical-session.target

[Service]
Type=simple
ExecStart=/usr/local/bin/clipletd
Restart=on-failure
RestartSec=5

# Resource limits
MemoryMax=200M
CPUQuota=50%

# Environment
Environment=DISPLAY=:0

[Install]
WantedBy=default.target
```

---

## Configuration Templates

### Minimal Setup (Low Resource)
```json
{
  "popup_width": 350,
  "popup_height": 250,
  "popup_items_visible": 5,
  "max_history_items": 20,
  "auto_cleanup_days": 3,
  "auto_hide_delay": 5,
  "log_level": "WARNING"
}
```

### Power User Setup
```json
{
  "popup_width": 500,
  "popup_height": 400,
  "popup_items_visible": 12,
  "max_history_items": 100,
  "auto_cleanup_days": 14,
  "auto_hide_delay": 20,
  "excluded_apps": [
    "gnome-keyring",
    "keepassxc",
    "bitwarden",
    "1password",
    "gnome-terminal",
    "code",
    "pycharm"
  ],
  "log_level": "DEBUG"
}
```

### Privacy-Focused Setup
```json
{
  "max_history_items": 10,
  "auto_cleanup_days": 1,
  "excluded_apps": [
    "gnome-keyring",
    "keepassxc",
    "bitwarden",
    "1password",
    "lastpass",
    "firefox",
    "chromium",
    "chrome",
    "gnome-terminal",
    "konsole",
    "terminator"
  ]
}
```

---

## Migration and Backup

### Backup Configuration
```bash
# Export current settings
cliplet-settings --export ~/cliplet-backup-$(date +%Y%m%d).json

# Manual backup
cp ~/.config/cliplet/config.json ~/cliplet-config-backup.json
cp ~/.local/share/cliplet/history.json ~/cliplet-history-backup.json
```

### Restore Configuration
```bash
# Import settings
cliplet-settings --import ~/cliplet-backup.json

# Manual restore
cp ~/cliplet-config-backup.json ~/.config/cliplet/config.json
systemctl --user restart cliplet.service
```

### Migration Between Systems
```bash
# On old system
tar czf cliplet-backup.tar.gz -C ~ .config/cliplet .local/share/cliplet

# On new system (after installation)
tar xzf cliplet-backup.tar.gz -C ~
systemctl --user restart cliplet.service
```

---

## Validation and Testing

### Validate Configuration
```bash
# Check configuration validity
clipletd --check-config

# Test popup
cliplet-popup

# Check service status
systemctl --user status cliplet.service
```

### Test Shortcuts
1. Set up keyboard shortcut
2. Copy some text
3. Press shortcut key
4. Verify popup appears with copied text
5. Click item to paste

---

## Configuration Troubleshooting

### Reset to Defaults
```bash
# GUI reset
cliplet-settings --reset

# Manual reset
rm ~/.config/cliplet/config.json
systemctl --user restart cliplet.service
```

### Common Issues
- **Settings not saving**: Check file permissions
- **Shortcuts not working**: Verify system shortcut configuration
- **Popup not themed**: Install libadwaita-devel
- **High memory usage**: Reduce `max_history_items`

See [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md) for detailed issue resolution.