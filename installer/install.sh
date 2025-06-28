#!/bin/bash

# HoUer OS Installation Script
# Based on Arch Linux with Enlightenment DE

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
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   error "This script should not be run as root. Please run as a regular user with sudo privileges."
fi

# Check if we're on Arch Linux
if ! command -v pacman &> /dev/null; then
    error "This script is designed for Arch Linux. Please run on a clean Arch Linux installation."
fi

log "Starting HoUer OS installation..."

# Update system
log "Updating system packages..."
sudo pacman -Syu --noconfirm

# Install base packages
log "Installing base packages..."
sudo pacman -S --needed --noconfirm \
    base-devel \
    git \
    wget \
    curl \
    nano \
    vim \
    htop \
    neofetch \
    firefox \
    chromium

# Install Enlightenment DE
log "Installing Enlightenment Desktop Environment..."
sudo pacman -S --needed --noconfirm \
    enlightenment \
    terminology \
    efl \
    python-efl

# Install container tools
log "Installing container management tools..."
sudo pacman -S --needed --noconfirm \
    podman \
    distrobox \
    docker \
    docker-compose

# Install development tools
log "Installing development tools..."
sudo pacman -S --needed --noconfirm \
    python \
    python-pip \
    python-setuptools \
    python-wheel \
    nodejs \
    npm \
    rust \
    cargo \
    go

# Install flatpak
log "Installing Flatpak..."
sudo pacman -S --needed --noconfirm flatpak
sudo flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

# Install GNOME basic applications
log "Installing GNOME applications..."
sudo pacman -S --needed --noconfirm \
    gnome-calculator \
    gnome-system-monitor \
    gnome-disk-utility \
    gnome-screenshot \
    nautilus \
    gedit \
    evince

# Install KDE basic applications
log "Installing KDE applications..."
sudo pacman -S --needed --noconfirm \
    konsole \
    dolphin \
    kate \
    okular \
    spectacle \
    kcalc \
    ark

# Install input methods
log "Installing input methods..."
sudo pacman -S --needed --noconfirm \
    ibus \
    ibus-hangul \
    ibus-libpinyin \
    ibus-anthy \
    ibus-unikey

# Install graphics drivers
log "Detecting graphics card..."
if lspci | grep -i nvidia > /dev/null; then
    warning "NVIDIA graphics card detected. Installing NVIDIA drivers..."
    sudo pacman -S --needed --noconfirm \
        nvidia \
        nvidia-utils \
        lib32-nvidia-utils \
        nvidia-settings
fi

if lspci | grep -i amd > /dev/null; then
    info "AMD graphics card detected. Installing AMD drivers..."
    sudo pacman -S --needed --noconfirm \
        xf86-video-amdgpu \
        vulkan-radeon \
        lib32-vulkan-radeon
fi

# Install Wayland and X11 support
log "Installing display server support..."
sudo pacman -S --needed --noconfirm \
    wayland \
    xorg-server \
    xorg-xinit \
    xorg-xrandr \
    xorg-xsetroot

# Install Calamares installer
log "Installing Calamares installer..."
sudo pacman -S --needed --noconfirm calamares

# Install audio system
log "Installing audio system..."
sudo pacman -S --needed --noconfirm \
    pulseaudio \
    pulseaudio-alsa \
    pavucontrol \
    alsa-utils

# Install fonts
log "Installing fonts..."
sudo pacman -S --needed --noconfirm \
    ttf-dejavu \
    ttf-liberation \
    noto-fonts \
    noto-fonts-cjk \
    noto-fonts-emoji

# Install Wine for Windows application support
log "Installing Wine..."
sudo pacman -S --needed --noconfirm \
    wine \
    winetricks \
    lib32-gnutls

# Enable services
log "Enabling system services..."
sudo systemctl enable NetworkManager
sudo systemctl enable bluetooth
sudo systemctl enable cups
sudo systemctl enable docker

# Install AUR helper (yay)
if ! command -v yay &> /dev/null; then
    log "Installing AUR helper (yay)..."
    cd /tmp
    git clone https://aur.archlinux.org/yay.git
    cd yay
    makepkg -si --noconfirm
    cd ..
    rm -rf yay
fi

# Install soda from AUR for Windows container support
log "Installing soda for Windows container support..."
yay -S --noconfirm soda-git || warning "Failed to install soda from AUR"

# Copy HoUer Manager
log "Installing HoUer Manager..."
sudo cp -r ../Manager /opt/houer-manager
sudo chown -R root:root /opt/houer-manager
sudo chmod +x /opt/houer-manager/houer-manager.py
sudo chmod +x /opt/houer-manager/houer-manager

# Create command-line launcher
log "Creating HoUer Manager command..."
sudo cp /opt/houer-manager/houer-manager /usr/local/bin/houer-manager
sudo chmod +x /usr/local/bin/houer-manager

# Alternative shorter command
sudo ln -sf /usr/local/bin/houer-manager /usr/local/bin/houer

# Create desktop entry for HoUer Manager
log "Creating desktop entry..."
sudo tee /usr/share/applications/houer-manager.desktop > /dev/null <<EOF
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

# Create autostart entry (optional)
log "Creating autostart entry..."
sudo tee /etc/xdg/autostart/houer-manager.desktop > /dev/null <<EOF
[Desktop Entry]
Name=HoUer Manager (Background)
Comment=HoUer Manager background service
Exec=houer-manager --background
Icon=/opt/houer-manager/assets/icon.png
Terminal=false
Type=Application
Categories=System;
Hidden=true
NoDisplay=true
X-GNOME-Autostart-enabled=false
EOF

# Replace system logos
log "Replacing system logos..."
if [ -f ../LOGO.png ]; then
    sudo cp ../LOGO.png /usr/share/pixmaps/houer-logo.png
    sudo cp ../LOGO.png /boot/grub/themes/default/logo.png 2>/dev/null || true
    sudo cp ../LOGO.png /usr/share/plymouth/themes/spinner/watermark.png 2>/dev/null || true
fi

# Configure Enlightenment as default
log "Configuring Enlightenment as default desktop environment..."
echo "exec enlightenment_start" > ~/.xinitrc

# Configure Wayland session
sudo mkdir -p /usr/share/wayland-sessions
sudo tee /usr/share/wayland-sessions/enlightenment.desktop > /dev/null <<EOF
[Desktop Entry]
Name=Enlightenment
Comment=The Enlightenment Desktop Environment
Exec=enlightenment_start
Type=Application
EOF

# Set default session to Wayland
echo "export XDG_SESSION_TYPE=wayland" >> ~/.bashrc
echo "export GDK_BACKEND=wayland" >> ~/.bashrc
echo "export QT_QPA_PLATFORM=wayland" >> ~/.bashrc

log "Pre-installation setup completed successfully!"
log "Starting Calamares installer..."

# Launch Calamares
sudo calamares &

info "Calamares installer has been launched."
info "After installation, HoUer Manager will be available in your applications menu."
info "The system is configured to use Wayland by default, with X11 as fallback."
info ""
info "Post-installation steps:"
info "1. Reboot your system"
info "2. Login and start HoUer Manager"
info "3. Configure your containers"
info ""
info "Thank you for choosing HoUer OS!" 