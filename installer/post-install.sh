#!/bin/bash

# HoUer OS Post-Installation Script
# This script is executed by Calamares after the base system installation
# It installs and configures ONLY HoUer OS specific components
# 
# Note: Basic system (base, base-devel, kernel, bootloader, users) 
#       should already be installed by Calamares

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[HoUer OS]${NC} $1"
    echo "$(date): $1" >> /var/log/houer-install.log
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    echo "$(date): ERROR: $1" >> /var/log/houer-install.log
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    echo "$(date): WARNING: $1" >> /var/log/houer-install.log
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
    echo "$(date): INFO: $1" >> /var/log/houer-install.log
}

log "Starting HoUer OS post-installation configuration..."

# Update package database
log "Updating package database..."
pacman -Sy

# Step 1: Install essential system packages first (that Calamares didn't install)
log "Step 1: Installing essential system packages..."
pacman -S --needed --noconfirm \
    base-devel \
    linux-headers \
    networkmanager \
    git \
    nano \
    wget \
    curl

# Enable NetworkManager for next boot
log "Enabling NetworkManager..."
systemctl enable NetworkManager

# Step 2: Install minimal system components
log "Step 2: Installing minimal system components..."

# Minimal X11/Wayland support for Enlightenment
log "Installing minimal display server support..."
pacman -S --needed --noconfirm \
    xorg-server \
    mesa

# Basic audio (for system notifications)
log "Installing basic audio support..."
pacman -S --needed --noconfirm \
    alsa-utils

# Note: Fonts will be installed with Korean CJK fonts later

# Essential Python for HoUer Manager
log "Installing Python for HoUer Manager..."
pacman -S --needed --noconfirm \
    python \
    python-tk

# Step 3: Install HoUer OS core components
log "Step 3: Installing HoUer OS core components..."

# Install Enlightenment Desktop Environment (HoUer OS default DE)
log "Installing Enlightenment Desktop Environment..."
pacman -S --needed --noconfirm \
    enlightenment \
    terminology \
    efl \
    python-efl

# Install container management tools (HoUer OS core feature)
log "Installing container management tools..."
pacman -S --needed --noconfirm \
    podman \
    distrobox \
    flatpak

# Add Flathub repository
log "Adding Flathub repository..."
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

# Install Korean input method (for HoUer OS)
log "Installing Korean input method..."
pacman -S --needed --noconfirm \
    ibus \
    ibus-hangul

# Configure display server support
log "Configuring display server support..."
pacman -S --needed --noconfirm \
    wayland \
    xwayland

# Install Korean fonts (CJK includes basic fonts)
log "Installing Korean fonts..."
pacman -S --needed --noconfirm \
    noto-fonts-cjk

# Enable essential services
log "Enabling essential services..."
systemctl enable NetworkManager || warning "NetworkManager already enabled or not found"

# Copy HoUer Manager
log "Installing HoUer Manager..."
if [ -d "/opt/houer-installer/Manager" ]; then
    cp -r /opt/houer-installer/Manager /opt/houer-manager
    chmod +x /opt/houer-manager/houer-manager.py
    
    # Create system-wide command
    cat > /usr/local/bin/houer-manager << 'EOF'
#!/bin/bash
cd /opt/houer-manager
python3 houer-manager.py "$@"
EOF
    chmod +x /usr/local/bin/houer-manager
    
    # Create short command alias
    ln -sf /usr/local/bin/houer-manager /usr/local/bin/houer
    
    # Create desktop entry
    cat > /usr/share/applications/houer-manager.desktop << 'EOF'
[Desktop Entry]
Name=HoUer Manager
Comment=Container Management for HoUer OS
Exec=houer-manager
Icon=/opt/houer-manager/assets/icon.png
Terminal=false
Type=Application
Categories=System;
EOF
    
    log "HoUer Manager installed successfully"
else
    warning "HoUer Manager source not found in /opt/houer-installer/Manager"
fi

# Configure Enlightenment as default session
log "Configuring Enlightenment as default session..."
# Get the first regular user
REGULAR_USER=$(getent passwd | awk -F: '$3 >= 1000 && $3 < 60000 { print $1; exit }')

if [ -n "$REGULAR_USER" ]; then
    log "Configuring session for user: $REGULAR_USER"
    USER_HOME=$(getent passwd "$REGULAR_USER" | cut -d: -f6)
    
    # Set up .xinitrc for X11 fallback
    echo "exec enlightenment_start" > "$USER_HOME/.xinitrc"
    chown "$REGULAR_USER:$REGULAR_USER" "$USER_HOME/.xinitrc"
    
    # Configure input method
    cat > "$USER_HOME/.profile" << 'EOF'
export GTK_IM_MODULE=ibus
export XMODIFIERS=@im=ibus
export QT_IM_MODULE=ibus
ibus-daemon -drx
EOF
    chown "$REGULAR_USER:$REGULAR_USER" "$USER_HOME/.profile"
else
    warning "No regular user found for session configuration"
fi

# Configure HoUer OS branding
log "Applying HoUer OS branding..."
echo "HoUer OS" > /etc/os-release.d/NAME
echo "Container-centric OS based on Arch Linux" > /etc/os-release.d/DESCRIPTION

# Create HoUer OS welcome message
cat > /etc/motd << 'EOF'
Welcome to HoUer OS!

A container-centric operating system based on Arch Linux.

Quick start:
- Run 'houer-manager' or 'houer' to manage containers
- Use 'distrobox' for Linux containers
- Enlightenment is your desktop environment

Documentation: https://github.com/your-repo/houer-os
EOF

# Final configuration
log "Performing final configuration..."

# Enable auto-login for the regular user (optional)
if [ -n "$REGULAR_USER" ]; then
    log "Setting up auto-login for $REGULAR_USER"
    systemctl enable getty@tty1.service
    
    # Create override directory and file for auto-login
    mkdir -p /etc/systemd/system/getty@tty1.service.d
    cat > /etc/systemd/system/getty@tty1.service.d/override.conf << EOF
[Service]
ExecStart=
ExecStart=-/usr/bin/agetty --autologin $REGULAR_USER --noclear %I \$TERM
EOF
fi

# Update font cache
log "Updating font cache..."
fc-cache -fv

log "HoUer OS post-installation completed successfully!"
log "System is ready for use. Reboot to start HoUer OS."

info "After reboot:"
info "- Start Enlightenment desktop environment"
info "- Run 'houer-manager' to manage containers"
info "- Check /var/log/houer-install.log for installation details" 