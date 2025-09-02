# Cliplet Usage Guide

## Installation

1. Run `bash cliplet/scripts/install.sh` to install Cliplet and dependencies.
2. Enable autostart: `systemctl --user enable cliplet`
3. Start the daemon: `systemctl --user start cliplet`
4. Configure keyboard shortcuts using `cliplet/scripts/setup-keyboard-shortcut.sh`.

## Features

- Clipboard history popup (modal or windowed)
- Autopaste support (Wayland/Xorg)
- Systemd user service for autostart
- Configurable UI and theme
- Privacy controls and history management

## Usage

- Press your configured shortcut to open the popup.
- Select an item to copy and autopaste.
- Use settings (`cliplet-settings`) to adjust popup mode, theme, and history options.

## Uninstallation

Run `bash cliplet/scripts/uninstall.sh` to remove Cliplet, dependencies, and user data.

## Troubleshooting

- Ensure systemd user services are enabled.
- Check dependencies: `xdotool`, `wtype` (Wayland).
- For issues, restart the daemon: `systemctl --user restart cliplet`
- Review logs in `~/.config/cliplet/` for errors.

## Documentation

See additional guides in the `docs/` folder for advanced configuration and developer notes.