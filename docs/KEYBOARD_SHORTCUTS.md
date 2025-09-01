# Manual Keyboard Shortcut Setup Guide

## Overview

The Cliplet provides a dedicated popup script that can be easily configured with any custom keyboard shortcut through your system's keyboard settings. This method is more reliable than global hotkeys and allows you to use any key combination you prefer.

## Quick Setup

### **Step 1: Get the Script Path**
```bash
cd /path/to/cliplet
./bin/cliplet-popup --show-path
```

This will output something like:
```
Executable path: /home/username/cliplet/bin/cliplet-popup
Use this path in your keyboard shortcut settings:
Command: /home/username/cliplet/bin/cliplet-popup
```

### **Step 2: Set Up Keyboard Shortcut**

#### **For GNOME Desktop:**

1. **Open Settings**
   ```bash
   gnome-control-center keyboard
   ```
   Or: `Settings` → `Keyboard` → `View and Customize Shortcuts`

2. **Create Custom Shortcut**
   - Click "Custom Shortcuts" at the bottom
   - Click the "+" button to add new shortcut
   - **Name**: `Clipboard Manager`
   - **Command**: `/full/path/to/cliplet-popup` (use the path from Step 1)
   - **Shortcut**: Press your desired key combination (e.g., `Super+V`, `Ctrl+Alt+V`, `F12`)

#### **For KDE Plasma:**

1. **Open System Settings**
   ```bash
   systemsettings5 shortcuts
   ```

2. **Create Custom Shortcut**
   - Go to `Shortcuts` → `Custom Shortcuts`
   - Right-click → `New` → `Global Shortcut` → `Command/URL`
   - **Name**: `Clipboard Manager`
   - **Command**: `/full/path/to/cliplet-popup`
   - Set your desired trigger key combination

#### **For XFCE:**

1. **Open Keyboard Settings**
   ```bash
   xfce4-keyboard-settings
   ```

2. **Add Application Shortcut**
   - Go to `Application Shortcuts` tab
   - Click "Add"
   - **Command**: `/full/path/to/cliplet-popup`
   - Press your desired key combination

## Recommended Key Combinations

### **Windows-like Experience:**
- `Super+V` (Windows key + V) - Matches Windows clipboard manager

### **Alternative Options:**
- `Ctrl+Alt+V` - Easy to reach, universal
- `Ctrl+Shift+V` - Common clipboard shortcut
- `Alt+Space` - Quick access
- `F12` - Function key (won't conflict with applications)
- `Ctrl+Alt+C` - Clipboard mnemonic

## Advanced Configuration

### **Using Absolute Path After Installation**

If you install the clipboard manager system-wide, you can use:
```bash
/usr/local/bin/cliplet-popup
```

Or if installed in your home directory:
```bash
$HOME/.local/bin/cliplet-popup
```

### **Testing Your Shortcut**

1. **Test the script directly:**
   ```bash
   /path/to/cliplet-popup
   ```

2. **Verify the daemon is running:**
   ```bash
   systemctl --user status cliplet
   ```

3. **Test with sample clipboard content:**
   ```bash
   echo "Test content" | xclip -selection clipboard
   # Now press your keyboard shortcut
   ```

## Desktop Environment Specific Instructions

### **GNOME Desktop**

**Method 1: GUI Settings**
1. `Super` key → type "keyboard" → `Keyboard Settings`
2. `View and Customize Shortcuts` → `Custom Shortcuts`
3. Click `+` → Add name and command → Set shortcut

**Method 2: Command Line**
```bash
# Add custom keybinding
gsettings set org.gnome.settings-daemon.plugins.media-keys custom-keybindings "['/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/']"

# Configure the binding
gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/ name 'Clipboard Manager'
gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/ command '/path/to/cliplet-popup'
gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/ binding '<Super>v'
```

### **KDE Plasma**

```bash
# Using kwriteconfig5 (replace /path/to/script with actual path)
kwriteconfig5 --file kglobalshortcutsrc --group cliplet-popup --key _k_friendly_name "Clipboard Manager"
kwriteconfig5 --file kglobalshortcutsrc --group cliplet-popup --key _launch "Meta+V,none,Clipboard Manager"
```

### **XFCE4**

```bash
# Add to xfconf
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Super>v" -n -t string -s "/path/to/cliplet-popup"
```

## Troubleshooting

### **Shortcut Not Working**

1. **Check if daemon is running:**
   ```bash
   ps aux | grep clipletd
   systemctl --user status cliplet
   ```

2. **Test script manually:**
   ```bash
   /path/to/cliplet-popup
   ```

3. **Check script permissions:**
   ```bash
   ls -la /path/to/cliplet-popup
   # Should show executable permissions (x)
   ```

4. **Verify GTK4 is available:**
   ```bash
   python3 -c "import gi; gi.require_version('Gtk', '4.0'); print('GTK4 OK')"
   ```

### **Popup Appears But Is Empty**

1. **Copy some text first:**
   ```bash
   echo "Test clipboard content" | xclip -selection clipboard
   ```

2. **Check clipboard history:**
   ```bash
   xclip -selection clipboard -o
   ```

### **Key Combination Conflicts**

1. **Check existing shortcuts:**
   ```bash
   # GNOME
   gsettings list-recursively org.gnome.desktop.wm.keybindings
   
   # KDE
   kreadconfig5 --file kglobalshortcutsrc
   ```

2. **Choose alternative combination** or **disable conflicting shortcut**

## Setup Script

Create this helper script for easy setup:

```bash
#!/bin/bash
# save as setup-shortcut.sh

SCRIPT_PATH=$(realpath "./bin/cliplet-popup")

echo "Setting up keyboard shortcut for Cliplet"
echo "Script path: $SCRIPT_PATH"
echo ""
echo "Detected desktop environment:"

if [ "$XDG_CURRENT_DESKTOP" = "GNOME" ]; then
    echo "GNOME detected"
    echo "Open: Settings → Keyboard → View and Customize Shortcuts → Custom Shortcuts"
    echo "Command: $SCRIPT_PATH"
elif [ "$XDG_CURRENT_DESKTOP" = "KDE" ]; then
    echo "KDE detected"
    echo "Open: System Settings → Shortcuts → Custom Shortcuts"
    echo "Command: $SCRIPT_PATH"
elif [ "$XDG_CURRENT_DESKTOP" = "XFCE" ]; then
    echo "XFCE detected"
    echo "Open: Settings → Keyboard → Application Shortcuts"
    echo "Command: $SCRIPT_PATH"
else
    echo "Unknown desktop environment"
    echo "Use your system's keyboard shortcut settings"
    echo "Command: $SCRIPT_PATH"
fi

echo ""
echo "Recommended shortcuts: Super+V, Ctrl+Alt+V, F12"
```

## Benefits of Manual Setup

- **More Reliable** - No dependency on global hotkey libraries
- **Customizable** - Use any key combination you prefer
- **System Integration** - Works with your desktop environment's native shortcut system
- **No Conflicts** - Easy to resolve conflicts through system settings
- **Cache-Free** - Bypasses any hotkey caching issues
- **User Control** - Full control over shortcut behavior

---

**Windows-Style Clipboard Management for Linux**