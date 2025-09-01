#!/bin/bash
# Production Uninstall Script for Cliplet
# Safely removes the application and all components

set -e  # Exit on any error

# Configuration
APP_NAME="cliplet"
PREFIX="${PREFIX:-/usr/local}"

# Paths
BIN_DIR="$PREFIX/bin"
SHARE_DIR="$PREFIX/share"
SYSTEMD_USER_DIR="$HOME/.config/systemd/user"
DESKTOP_DIR="$SHARE_DIR/applications"
ICONS_DIR="$SHARE_DIR/icons/hicolor"
MAN_DIR="$SHARE_DIR/man/man1"
SRC_DIR="$PREFIX/lib/python3/site-packages/cliplet"

# User data paths
CONFIG_DIR="$HOME/.config/$APP_NAME"
DATA_DIR="$HOME/.local/share/$APP_NAME"
CACHE_DIR="$HOME/.cache/$APP_NAME"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if application is installed
check_installation() {
    log_info "Checking installation..."
    
    local found=false
    
    if [[ -x "$BIN_DIR/clipletd" ]] || [[ -x "$BIN_DIR/cliplet-settings" ]]; then
        found=true
    fi
    
    if [[ -d "$SRC_DIR" ]]; then
        found=true
    fi
    
    if [[ ! "$found" == true ]]; then
        log_warning "Cliplet does not appear to be installed"
        read -p "Continue anyway? [y/N]: " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 0
        fi
    fi
}

# Stop running services
stop_services() {
    log_info "Stopping running services..."
    
    # Stop systemd service
    if command -v systemctl &> /dev/null; then
        if systemctl --user is-active cliplet.service &>/dev/null; then
            systemctl --user stop cliplet.service
            log_success "Systemd service stopped"
        fi
        
        if systemctl --user is-enabled cliplet.service &>/dev/null; then
            systemctl --user disable cliplet.service
            log_success "Systemd service disabled"
        fi
    fi
    
    # Kill any running processes
    if pgrep -f "clipletd" &>/dev/null; then
        pkill -f "clipletd" || true
        sleep 2
        if pgrep -f "clipletd" &>/dev/null; then
            pkill -9 -f "clipletd" || true
        fi
        log_success "Running daemon processes stopped"
    fi
    
    if pgrep -f "cliplet-settings" &>/dev/null; then
        pkill -f "cliplet-settings" || true
        log_success "Running settings processes stopped"
    fi
}

# Remove installed files
remove_files() {
    log_info "Removing installed files..."
    
    # Remove executables
    rm -f "$BIN_DIR/clipletd"
    rm -f "$BIN_DIR/cliplet-settings"
    rm -f "$BIN_DIR/cliplet-popup"
    
    # Remove source directory
    rm -rf "$SRC_DIR"
    
    # Remove desktop files
    rm -f "$DESKTOP_DIR/cliplet-settings.desktop"
    
    # Remove icons
    rm -f "$ICONS_DIR/16x16/apps/cliplet.png"
    rm -f "$ICONS_DIR/32x32/apps/cliplet.png"
    rm -f "$ICONS_DIR/48x48/apps/cliplet.png"
    rm -f "$ICONS_DIR/1024x1024/apps/cliplet.png"
    rm -f "$ICONS_DIR/scalable/apps/cliplet.svg"
    
    # Remove scripts directory
    rm -rf "$SHARE_DIR/cliplet"
    
    # Remove systemd service
    rm -f "$SYSTEMD_USER_DIR/cliplet.service"
    
    # Remove man pages
    rm -f "$MAN_DIR/clipletd.1"
    rm -f "$MAN_DIR/cliplet-settings.1"
    
    log_success "Installed files removed"
}

# Handle user data
handle_user_data() {
    echo
    log_warning "User data directories found:"
    
    if [[ -d "$CONFIG_DIR" ]]; then
        echo "  Configuration: $CONFIG_DIR"
    fi
    
    if [[ -d "$DATA_DIR" ]]; then
        echo "  Data: $DATA_DIR"
    fi
    
    if [[ -d "$CACHE_DIR" ]]; then
        echo "  Cache: $CACHE_DIR"
    fi
    
    echo
    read -p "Remove user data? [y/N]: " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$CONFIG_DIR"
        rm -rf "$DATA_DIR"
        rm -rf "$CACHE_DIR"
        log_success "User data removed"
    else
        log_info "User data preserved"
        echo "To remove manually later:"
        [[ -d "$CONFIG_DIR" ]] && echo "  rm -rf '$CONFIG_DIR'"
        [[ -d "$DATA_DIR" ]] && echo "  rm -rf '$DATA_DIR'"
        [[ -d "$CACHE_DIR" ]] && echo "  rm -rf '$CACHE_DIR'"
    fi
}

# Update system caches
update_caches() {
    log_info "Updating system caches..."
    
    # Update desktop database
    if command -v update-desktop-database &> /dev/null; then
        update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
    fi
    
    # Update icon cache
    if command -v gtk-update-icon-cache &> /dev/null; then
        gtk-update-icon-cache -f -t "$SHARE_DIR/icons/hicolor" 2>/dev/null || true
    fi
    
    # Update man database
    if command -v mandb &> /dev/null; then
        mandb -q 2>/dev/null || true
    fi
    
    # Reload systemd
    if command -v systemctl &> /dev/null; then
        systemctl --user daemon-reload 2>/dev/null || true
    fi
    
    log_success "System caches updated"
}

# Verify removal
verify_removal() {
    log_info "Verifying removal..."
    
    local remaining=()
    
    [[ -x "$BIN_DIR/clipletd" ]] && remaining+=("$BIN_DIR/clipletd")
    [[ -x "$BIN_DIR/cliplet-settings" ]] && remaining+=("$BIN_DIR/cliplet-settings")
    [[ -x "$BIN_DIR/cliplet-popup" ]] && remaining+=("$BIN_DIR/cliplet-popup")
    [[ -d "$SRC_DIR" ]] && remaining+=("$SRC_DIR")
    [[ -f "$SYSTEMD_USER_DIR/cliplet.service" ]] && remaining+=("systemd service")
    
    if [[ ${#remaining[@]} -gt 0 ]]; then
        log_warning "Some files may still remain:"
        printf '  %s\n' "${remaining[@]}"
    else
        log_success "Removal verified - no installation files found"
    fi
}

# Main uninstall function
main() {
    echo "===================================="
    echo "Cliplet Uninstaller"
    echo "===================================="
    echo
    
    log_warning "This will remove Cliplet from your system."
    read -p "Are you sure you want to continue? [y/N]: " -n 1 -r
    echo
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Uninstall cancelled"
        exit 0
    fi
    
    check_installation
    stop_services
    remove_files
    handle_user_data
    update_caches
    verify_removal
    
    echo
    log_success "Uninstall completed successfully!"
    echo
    echo "Cliplet has been removed from your system."
    echo
}

# Run main function
main "$@"