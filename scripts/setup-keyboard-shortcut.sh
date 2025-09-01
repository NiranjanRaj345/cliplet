#!/bin/bash
# Cliplet - Keyboard Shortcut Setup Helper
# This script helps users set up custom keyboard shortcuts

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory and determine popup script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Try to find cliplet-popup in PATH first, then fallback to project directory
if command -v cliplet-popup &> /dev/null; then
    POPUP_SCRIPT="cliplet-popup"
else
    POPUP_SCRIPT="$PROJECT_DIR/bin/cliplet-popup"
fi

echo -e "${BLUE}Cliplet - Keyboard Shortcut Setup${NC}"
echo "================================================="
echo ""

# Check if popup script exists
if [[ ! -f "$POPUP_SCRIPT" ]]; then
    echo -e "${RED}Error: Popup script not found at $POPUP_SCRIPT${NC}"
    echo "Please ensure the application is properly installed."
    exit 1
fi

# Make sure script is executable
chmod +x "$POPUP_SCRIPT"

echo -e "${GREEN}Popup script found and ready${NC}"
echo -e "${YELLOW}Script location:${NC} $POPUP_SCRIPT"
echo ""

# Detect desktop environment
echo -e "${BLUE}Desktop Environment Detection:${NC}"
if [[ "$XDG_CURRENT_DESKTOP" == *"GNOME"* ]]; then
    DE="GNOME"
    echo -e "${GREEN}GNOME detected${NC}"
elif [[ "$XDG_CURRENT_DESKTOP" == *"KDE"* ]]; then
    DE="KDE"
    echo -e "${GREEN}KDE Plasma detected${NC}"
elif [[ "$XDG_CURRENT_DESKTOP" == *"XFCE"* ]]; then
    DE="XFCE"
    echo -e "${GREEN}XFCE detected${NC}"
else
    DE="UNKNOWN"
    echo -e "${YELLOW}Unknown desktop environment: $XDG_CURRENT_DESKTOP${NC}"
fi

echo ""
echo -e "${BLUE}Setup Instructions:${NC}"
echo "======================"

case $DE in
    "GNOME")
        echo -e "${GREEN}For GNOME:${NC}"
        echo "1. Open Settings (or press Super and type 'keyboard')"
        echo "2. Go to Keyboard → View and Customize Shortcuts"
        echo "3. Scroll down and click 'Custom Shortcuts'"
        echo "4. Click the '+' button to add a new shortcut"
        echo "5. Fill in the details:"
        echo -e "   ${YELLOW}Name:${NC} Clipboard Manager"
        echo -e "   ${YELLOW}Command:${NC} $POPUP_SCRIPT"
        echo -e "   ${YELLOW}Shortcut:${NC} Press your desired key combination (e.g., Super+V)"
        echo ""
        echo -e "${BLUE}Quick access:${NC}"
        echo "   gnome-control-center keyboard"
        ;;
    "KDE")
        echo -e "${GREEN}For KDE Plasma:${NC}"
        echo "1. Open System Settings"
        echo "2. Go to Shortcuts → Custom Shortcuts"
        echo "3. Right-click → New → Global Shortcut → Command/URL"
        echo "4. Fill in the details:"
        echo -e "   ${YELLOW}Name:${NC} Clipboard Manager"
        echo -e "   ${YELLOW}Command:${NC} $POPUP_SCRIPT"
        echo "5. Set your desired trigger key combination"
        echo ""
        echo -e "${BLUE}Quick access:${NC}"
        echo "   systemsettings5 shortcuts"
        ;;
    "XFCE")
        echo -e "${GREEN}For XFCE:${NC}"
        echo "1. Open Keyboard Settings"
        echo "2. Go to 'Application Shortcuts' tab"
        echo "3. Click 'Add'"
        echo "4. Enter command: $POPUP_SCRIPT"
        echo "5. Press your desired key combination"
        echo ""
        echo -e "${BLUE}Quick access:${NC}"
        echo "   xfce4-keyboard-settings"
        ;;
    *)
        echo -e "${YELLOW}For your desktop environment:${NC}"
        echo "1. Open your system's keyboard shortcut settings"
        echo "2. Add a new custom shortcut"
        echo "3. Use this command: $POPUP_SCRIPT"
        echo "4. Set your desired key combination"
        ;;
esac

echo ""
echo -e "${BLUE}Recommended Key Combinations:${NC}"
echo "================================="
echo -e "${GREEN}Windows-like:${NC} Super+V (Windows key + V)"
echo -e "${YELLOW}Alternatives:${NC}"
echo "   • Ctrl+Alt+V  (easy to reach)"
echo "   • Ctrl+Shift+V (common clipboard shortcut)"
echo "   • F12         (function key, no conflicts)"
echo "   • Alt+Space   (quick access)"

echo ""
echo -e "${BLUE}Testing:${NC}"
echo "==========="
echo "1. First, make sure the daemon is running:"
echo "   systemctl --user start cliplet"
echo ""
echo "2. Copy some text to test:"
echo "   echo 'Test clipboard content' | xclip -selection clipboard"
echo ""
echo "3. Test the popup script directly:"
echo "   $POPUP_SCRIPT"
echo ""
echo "4. After setting up your shortcut, press the key combination!"

echo ""
echo -e "${GREEN}For detailed instructions, see:${NC}"
echo "   $PROJECT_DIR/docs/KEYBOARD_SHORTCUTS.md"

echo ""
echo -e "${BLUE}Copy this command for your shortcut settings:${NC}"
echo -e "${YELLOW}$POPUP_SCRIPT${NC}"

# Offer to copy to clipboard if xclip is available
if command -v xclip &> /dev/null; then
    echo ""
    read -p "Would you like to copy this path to clipboard? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "$POPUP_SCRIPT" | xclip -selection clipboard
        echo -e "${GREEN}Path copied to clipboard!${NC}"
    fi
fi

echo ""
echo -e "${GREEN}Happy clipboard managing!${NC}"