#!/bin/bash
# Production Installation Script for Cliplet
# Properly installs the application with all components

set -e  # Exit on any error

# Configuration
APP_NAME="cliplet"
VERSION="1.0.0"
PREFIX="${PREFIX:-$HOME/.local}"
INSTALL_USER="${INSTALL_USER:-$USER}"

# Paths
BIN_DIR="$PREFIX/bin"
SHARE_DIR="$PREFIX/share"
SYSTEMD_USER_DIR="$HOME/.config/systemd/user"
DESKTOP_DIR="$SHARE_DIR/applications"
ICONS_DIR="$SHARE_DIR/icons/hicolor"
MAN_DIR="$SHARE_DIR/man/man1"
SCRIPTS_DIR="$SHARE_DIR/cliplet/scripts"

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

# Check if running as root
check_root() {
    log_info "Installing for user: $INSTALL_USER"
}

# Check dependencies
check_dependencies() {
    log_info "Checking dependencies..."
    
    local missing_deps=()
    
    # Check Python 3
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi
    
    # Check Python modules
    python3 -c "import gi; gi.require_version('Gtk', '4.0')" 2>/dev/null || missing_deps+=("python3-gobject-base python3-gobject")
    
    # Check for libadwaita (optional but recommended for proper theming)
    if ! python3 -c "import gi; gi.require_version('Adw', '1')" 2>/dev/null; then
        log_warning "libadwaita not found - theming may not work properly"
        log_warning "Install with: sudo dnf install libadwaita-devel (Fedora/RHEL) or sudo apt install libadwaita-1-dev (Ubuntu/Debian)"
    fi
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        log_error "Install with: sudo dnf install ${missing_deps[*]} (or sudo apt install ${missing_deps[*]} on Ubuntu-based systems)"
        exit 1
    fi
    
    log_success "All dependencies satisfied"
}

# Create directories
create_directories() {
    log_info "Creating installation directories..."
    
    mkdir -p "$BIN_DIR"
    mkdir -p "$DESKTOP_DIR"
    mkdir -p "$ICONS_DIR/16x16/apps"
    mkdir -p "$ICONS_DIR/32x32/apps"
    mkdir -p "$ICONS_DIR/48x48/apps"
    mkdir -p "$ICONS_DIR/1024x1024/apps"
    mkdir -p "$ICONS_DIR/scalable/apps"
    mkdir -p "$MAN_DIR"
    mkdir -p "$SYSTEMD_USER_DIR"
    mkdir -p "$SCRIPTS_DIR"
    
    log_success "Directories created"
}

# Install Python package
install_package() {
    log_info "Installing Python package..."
    
    # Copy source files
    local src_dir="$PREFIX/lib/python3/site-packages"
    log_info "Creating directory: $src_dir"
    mkdir -p "$src_dir"
    cp -r src/cliplet "$src_dir/"
    
    # Make executables
    chmod +x bin/clipletd
    chmod +x bin/cliplet-settings
    chmod +x bin/cliplet-popup
    
    # Install executables
    cp bin/clipletd "$BIN_DIR/"
    cp bin/cliplet-settings "$BIN_DIR/"
    cp bin/cliplet-popup "$BIN_DIR/"
    
    # Update Python path in executables
    sed -i "s|sys.path.insert.*|sys.path.insert(0, '$PREFIX/lib/python3/site-packages')|" "$BIN_DIR/clipletd"
    sed -i "s|sys.path.insert.*|sys.path.insert(0, '$PREFIX/lib/python3/site-packages')|" "$BIN_DIR/cliplet-settings"
    sed -i "s|sys.path.insert.*|sys.path.insert(0, '$PREFIX/lib/python3/site-packages')|" "$BIN_DIR/cliplet-popup"
    
    log_success "Python package installed"
}

# Install desktop files
install_desktop_files() {
    log_info "Installing desktop files..."
    
    # Create desktop entry for settings
    cat > "$DESKTOP_DIR/cliplet-settings.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Cliplet Settings
Comment=Configure clipboard manager settings
Icon=cliplet
Exec=cliplet-settings
Categories=Settings;Utility;
Keywords=clipboard;settings;preferences;
StartupNotify=true
EOF
    
    # Install icons
    if [[ -d "share/icons/hicolor" ]]; then
        log_info "Installing application icons..."
        cp -r share/icons/hicolor/* "$ICONS_DIR/"
        
        # Update icon cache if available
        if command -v gtk-update-icon-cache &> /dev/null; then
            gtk-update-icon-cache -q "$SHARE_DIR/icons/hicolor" 2>/dev/null || true
        fi
        
        log_success "Icons installed and cache updated"
    else
        log_warning "Icon directory not found, skipping icon installation"
    fi
    
    # Install setup script for system access
    if [[ -f "scripts/setup-keyboard-shortcut.sh" ]]; then
        cp scripts/setup-keyboard-shortcut.sh "$SCRIPTS_DIR/"
        chmod +x "$SCRIPTS_DIR/setup-keyboard-shortcut.sh"
    fi
    
    log_success "Desktop files installed"
}

# Install systemd service
install_systemd_service() {
    log_info "Installing systemd user service..."
    
    cp etc/systemd/user/cliplet.service "$SYSTEMD_USER_DIR/"
    
    # Update ExecStart path
    sed -i "s|/usr/local/bin/clipletd|$BIN_DIR/clipletd|" \
        "$SYSTEMD_USER_DIR/cliplet.service"
    
    # Reload systemd
    if command -v systemctl &> /dev/null; then
        systemctl --user daemon-reload 2>/dev/null || true
    fi
    
    log_success "Systemd service installed"
}

# Install man pages
install_man_pages() {
    log_info "Installing man pages..."
    
    if [[ -d "share/man/man1" ]]; then
        cp share/man/man1/*.1 "$MAN_DIR/"
        
        # Update man database
        if command -v mandb &> /dev/null; then
            mandb -q 2>/dev/null || true
        fi
        
        log_success "Man pages installed"
    else
        log_warning "Man pages not found, skipping"
    fi
}

# Setup autostart
setup_autostart() {
    read -p "Enable autostart on login? [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v systemctl &> /dev/null; then
            systemctl --user enable cliplet.service
            log_success "Autostart enabled"
        else
            log_warning "systemctl not available, manual autostart setup required"
        fi
    fi
}

# Create configuration directories
setup_config() {
    log_info "Setting up configuration directories..."
    
    local config_dir="$HOME/.config/$APP_NAME"
    local data_dir="$HOME/.local/share/$APP_NAME"
    
    mkdir -p "$config_dir"
    mkdir -p "$data_dir/logs"
    
    log_success "Configuration directories created"
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."
    
    local errors=0
    
    # Check executables
    if [[ ! -x "$BIN_DIR/clipletd" ]]; then
        log_error "Daemon executable not found or not executable"
        ((errors++))
    fi
    
    if [[ ! -x "$BIN_DIR/cliplet-settings" ]]; then
        log_error "Settings executable not found or not executable"
        ((errors++))
    fi
    
    if [[ ! -x "$BIN_DIR/cliplet-popup" ]]; then
        log_error "Popup executable not found or not executable"
        ((errors++))
    fi
    
    # Check Python modules
    if ! "$BIN_DIR/clipletd" --version &>/dev/null; then
        log_error "Daemon executable test failed"
        ((errors++))
    fi
    
    if ! "$BIN_DIR/cliplet-settings" --version &>/dev/null; then
        log_error "Settings executable test failed"
        ((errors++))
    fi
    
    if ! "$BIN_DIR/cliplet-popup" --version &>/dev/null; then
        log_error "Popup executable test failed"
        ((errors++))
    fi
    
    if [[ $errors -gt 0 ]]; then
        log_error "Installation verification failed with $errors errors"
        exit 1
    fi
    
    log_success "Installation verified successfully"
}

# Main installation function
main() {
    echo "=================================="
    echo "Cliplet Installer"
    echo "Version: $VERSION"
    echo "=================================="
    echo
    
    # Change to project root directory
    cd "$(dirname "$0")/.."
    
    check_root
    check_dependencies
    create_directories
    install_package
    install_desktop_files
    install_systemd_service
    install_man_pages
    setup_config
    verify_installation
    setup_autostart
    
    echo
    log_success "Installation completed successfully!"
    echo
    echo "Next steps:"
    echo "  1. Start the daemon: systemctl --user start cliplet"
    echo "  2. Run setup-keyboard-shortcut.sh to configure system shortcuts"
    echo "  3. Configure settings: cliplet-settings"
    echo
    echo "For more information, see: man clipletd"
}

# Run main function
main "$@"