#!/bin/bash

# HoUer OS Post-Installation Script
# This script is executed by Calamares after the base system installation
# It installs and configures all HoUer OS specific components

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[HoUer OS Post-Install]${NC} $1"
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

# Update system
log "Updating system packages..."
pacman -Syu --noconfirm

# Install Enlightenment DE
log "Installing Enlightenment Desktop Environment..."
pacman -S --needed --noconfirm \
    enlightenment \
    terminology \
    efl \
    python-efl

# Install container tools
log "Installing container management tools..."
pacman -S --needed --noconfirm \
    podman \
    distrobox \
    docker \
    docker-compose

# Install development tools
log "Installing development tools..."
pacman -S --needed --noconfirm \
    python \
    python-pip \
    python-setuptools \
    python-wheel \
    python-tk \
    nodejs \
    npm \
    rust \
    cargo \
    go

# Install flatpak
log "Installing Flatpak..."
pacman -S --needed --noconfirm flatpak
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

# Install GNOME basic applications
log "Installing GNOME applications..."
pacman -S --needed --noconfirm \
    gnome-calculator \
    gnome-system-monitor \
    gnome-disk-utility \
    gnome-screenshot \
    nautilus \
    gedit \
    evince

# Install KDE basic applications
log "Installing KDE applications..."
pacman -S --needed --noconfirm \
    konsole \
    dolphin \
    kate \
    okular \
    spectacle \
    kcalc \
    ark

# Install input methods
log "Installing input methods..."
pacman -S --needed --noconfirm \
    ibus \
    ibus-hangul \
    ibus-libpinyin \
    ibus-anthy \
    ibus-unikey

# Install graphics drivers
log "Detecting graphics card..."
if lspci | grep -i nvidia > /dev/null; then
    warning "NVIDIA graphics card detected. Installing NVIDIA drivers..."
    pacman -S --needed --noconfirm \
        nvidia \
        nvidia-utils \
        lib32-nvidia-utils \
        nvidia-settings
fi

if lspci | grep -i amd > /dev/null; then
    info "AMD graphics card detected. Installing AMD drivers..."
    pacman -S --needed --noconfirm \
        xf86-video-amdgpu \
        vulkan-radeon \
        lib32-vulkan-radeon
fi

# Install Wayland and X11 support
log "Installing display server support..."
pacman -S --needed --noconfirm \
    wayland \
    xwayland \
    xorg-server \
    xorg-xinit \
    xorg-xrandr \
    xorg-xsetroot

# Install audio system
log "Installing audio system..."
pacman -S --needed --noconfirm \
    pulseaudio \
    pulseaudio-alsa \
    pavucontrol \
    alsa-utils

# Install fonts
log "Installing fonts..."
pacman -S --needed --noconfirm \
    ttf-dejavu \
    ttf-liberation \
    noto-fonts \
    noto-fonts-cjk \
    noto-fonts-emoji

# Install Wine for Windows application support
log "Installing Wine..."
pacman -S --needed --noconfirm \
    wine \
    winetricks \
    lib32-gnutls

# Install additional useful packages
log "Installing additional packages..."
pacman -S --needed --noconfirm \
    base-devel \
    git \
    wget \
    curl \
    nano \
    vim \
    htop \
    neofetch \
    firefox \
    file-roller \
    gvfs \
    gvfs-mtp \
    gvfs-gphoto2

# Enable services
log "Enabling system services..."
systemctl enable NetworkManager
systemctl enable bluetooth
systemctl enable cups

# Install AUR helper (yay) for regular user
log "Installing AUR helper (yay)..."
# Get the first regular user (not root)
REGULAR_USER=$(getent passwd | awk -F: '$3 >= 1000 && $3 < 60000 { print $1; exit }')

if [ -n "$REGULAR_USER" ]; then
    log "Installing yay for user: $REGULAR_USER"
    
    # Switch to user and install yay
    sudo -u "$REGULAR_USER" bash << 'EOFYAY'
    cd /tmp
    git clone https://aur.archlinux.org/yay.git
    cd yay
    makepkg -si --noconfirm
    cd ..
    rm -rf yay
EOFYAY

    # Install soda for Windows container support
    log "Installing soda for Windows container support..."
    sudo -u "$REGULAR_USER" yay -S --noconfirm soda-git || warning "Failed to install soda from AUR"
else
    warning "No regular user found, skipping AUR helper installation"
fi

# Copy HoUer Manager
log "Installing HoUer Manager..."
if [ -d "/opt/houer-installer/Manager" ]; then
    cp -r /opt/houer-installer/Manager /opt/houer-manager
    chown -R root:root /opt/houer-manager
    chmod +x /opt/houer-manager/houer-manager.py
    chmod +x /opt/houer-manager/houer-manager
    
    # Create command-line launcher
    log "Creating HoUer Manager command..."
    cp /opt/houer-manager/houer-manager /usr/local/bin/houer-manager
    chmod +x /usr/local/bin/houer-manager
    
    # Alternative shorter command
    ln -sf /usr/local/bin/houer-manager /usr/local/bin/houer
    
    # Create desktop entry for HoUer Manager
    log "Creating desktop entry..."
    tee /usr/share/applications/houer-manager.desktop > /dev/null <<EOF
[Desktop Entry]
Name=HoUer Manager
GenericName=Container Manager
Comment=Container Management for HoUer OS
Exec=houer-manager
Icon=/opt/houer-manager/assets/icon.png
Terminal=false
Type=Application
Categories=System;Settings;
StartupNotify=true
Keywords=container;docker;podman;distrobox;virtualization;
EOF
else
    warning "HoUer Manager not found in installer directory"
fi

# Replace system logos
log "Installing HoUer OS logos..."
if [ -f "/opt/houer-installer/LOGO.png" ]; then
    cp /opt/houer-installer/LOGO.png /usr/share/pixmaps/houer-logo.png
    # Note: Boot logos will be set during bootloader configuration
fi

# Configure Enlightenment as default
log "Configuring Enlightenment as default desktop environment..."
if [ -n "$REGULAR_USER" ]; then
    echo "exec enlightenment_start" > /home/"$REGULAR_USER"/.xinitrc
    chown "$REGULAR_USER:$REGULAR_USER" /home/"$REGULAR_USER"/.xinitrc
fi

# Configure Wayland session
mkdir -p /usr/share/wayland-sessions
tee /usr/share/wayland-sessions/enlightenment.desktop > /dev/null <<EOF
[Desktop Entry]
Name=Enlightenment
Comment=The Enlightenment Desktop Environment
Exec=enlightenment_start
Type=Application
EOF

# Set default session to Wayland for user
if [ -n "$REGULAR_USER" ]; then
    echo "export XDG_SESSION_TYPE=wayland" >> /home/"$REGULAR_USER"/.bashrc
    echo "export GDK_BACKEND=wayland" >> /home/"$REGULAR_USER"/.bashrc
    echo "export QT_QPA_PLATFORM=wayland" >> /home/"$REGULAR_USER"/.bashrc
    chown "$REGULAR_USER:$REGULAR_USER" /home/"$REGULAR_USER"/.bashrc
fi

# Set up display manager to use Wayland by default
log "Configuring display manager..."
if systemctl is-enabled gdm &>/dev/null; then
    # Enable Wayland for GDM
    sed -i 's/#WaylandEnable=false/WaylandEnable=true/' /etc/gdm/custom.conf
elif systemctl is-enabled sddm &>/dev/null; then
    # Configure SDDM for Wayland
    mkdir -p /etc/sddm.conf.d
    echo "[General]" > /etc/sddm.conf.d/wayland.conf
    echo "DisplayServer=wayland" >> /etc/sddm.conf.d/wayland.conf
fi

# Create welcome message
log "Creating welcome message..."
tee /etc/motd > /dev/null <<EOF
Welcome to HoUer OS!

Container-centric operating system based on Arch Linux

Quick start:
  houer-manager    - Start the container manager
  houer           - Short command for container manager

Documentation: https://github.com/your-repo/houer-os
Support: https://github.com/your-repo/houer-os/issues

EOF

# Clean up
log "Cleaning up..."
rm -rf /opt/houer-installer

log "HoUer OS post-installation completed successfully!"
log "System is ready for use. Please reboot to start using HoUer OS." 