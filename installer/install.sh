#!/bin/bash

# HoUer OS Live Environment Setup Script
# This script prepares the Arch Linux live environment for HoUer OS installation
# The actual installation is handled by Calamares

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

# Check if we're in a live environment
if ! grep -q "archiso" /proc/cmdline 2>/dev/null; then
    warning "This script is designed to run in an Arch Linux live environment."
    warning "Are you sure you want to continue? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        info "Installation cancelled."
        exit 0
    fi
fi

# Check if running as root (required in live environment)
if [[ $EUID -ne 0 ]]; then
   error "This script must be run as root in the live environment."
fi

# Check internet connection
if ! ping -c 1 archlinux.org &> /dev/null; then
    error "No internet connection. Please connect to the internet and try again."
fi

log "Starting HoUer OS live environment setup..."

# Update package database
log "Updating package database..."
pacman -Sy

# Install essential tools for installation
log "Installing essential tools..."
pacman -S --needed --noconfirm \
    gparted \
    gptfdisk \
    btrfs-progs \
    dosfstools \
    git \
    wget \
    curl \
    nano \
    vim

# Install Calamares installer
log "Installing Calamares installer..."
pacman -S --needed --noconfirm calamares

# Create HoUer OS installation directory
log "Preparing HoUer OS installation files..."
mkdir -p /opt/houer-installer
cp -r . /opt/houer-installer/

# Create Calamares configuration for HoUer OS
log "Configuring Calamares for HoUer OS..."
mkdir -p /etc/calamares

# Create custom Calamares settings
cat > /etc/calamares/settings.conf << 'EOF'
modules-search: [ local ]
instances:
- id: before
  module: shellprocess
  config: shellprocess_before.conf
- id: after  
  module: shellprocess
  config: shellprocess_after.conf

sequence:
- show:
  - welcome
  - locale
  - keyboard
  - partition
  - users
  - summary
- exec:
  - partition
  - mount
  - unpackfs
  - machineid
  - fstab
  - locale
  - keyboard
  - localecfg
  - users
  - displaymanager
  - networkcfg
  - hwclock
  - services-systemd
  - shellprocess@before
  - bootloader
  - shellprocess@after
  - umount
- show:
  - finished

branding: houer
prompt-install: true
dont-chroot: false
oem-setup: false
disable-cancel: false
disable-cancel-during-exec: false
hide-back-and-next-during-exec: false
quit-at-end: false
EOF

# Create HoUer OS branding
mkdir -p /etc/calamares/branding/houer
cat > /etc/calamares/branding/houer/branding.desc << 'EOF'
componentName:  houer
welcomeStyleCalamares:   false
welcomeExpandingLogo:   true
windowExpanding:    true
windowSize: 1024px,768px
windowPlacement: center
productName:         HoUer OS
productUrl:          https://github.com/your-repo/houer-os
productLogo:         "logo.png"
productIcon:         "logo.png"
version:             1.0
versionedName:       HoUer OS
shortVersionedName:  HoUer OS
bootloaderEntryName: HoUer OS
productWelcome:      "Welcome to the HoUer OS installer."
EOF

# Copy logo if available
if [ -f "/opt/houer-installer/LOGO.png" ]; then
    cp /opt/houer-installer/LOGO.png /etc/calamares/branding/houer/logo.png
fi

# Configure packages to be installed by Calamares
log "Configuring base packages for Calamares..."
cat > /etc/calamares/modules/packages.conf << 'EOF'
backend: pacman

operations:
  - install:
    - base-devel
    - linux-headers
    - networkmanager
    - bluetooth
    - bluez-utils
    - cups
    # Essential desktop applications
    - firefox
    - nautilus
    - gedit
    - gnome-calculator
    - gnome-terminal
    - gnome-system-monitor
    - gnome-screenshot
    - evince
    - file-roller
    # KDE applications
    - konsole
    - dolphin
    - kate
    - ark
    - spectacle
    - kcalc
    - okular
    # System tools
    - git
    - wget
    - curl
    - nano
    - vim
    - htop
    - neofetch
    - gvfs
    - gvfs-mtp
    # Graphics and display
    - xorg-server
    - xorg-xinit
    - xorg-xrandr
    - mesa
    # Fonts
    - ttf-dejavu
    - ttf-liberation
    - noto-fonts
    - noto-fonts-emoji
    # Audio
    - alsa-utils
    # Wine for Windows app support
    - wine
    - winetricks
    # Development tools
    - python-pip
    - python-setuptools
    - python-wheel

# Detect and add graphics drivers
echo "# Graphics drivers (auto-detected)" >> /etc/calamares/modules/packages.conf
if lspci | grep -i nvidia > /dev/null; then
    log "NVIDIA graphics detected, adding NVIDIA drivers to package list..."
    cat >> /etc/calamares/modules/packages.conf << 'EOF'
    # NVIDIA Graphics
    - nvidia
    - nvidia-utils
    - nvidia-settings
EOF
fi

if lspci | grep -i amd > /dev/null; then
    log "AMD graphics detected, adding AMD drivers to package list..."
    cat >> /etc/calamares/modules/packages.conf << 'EOF'
    # AMD Graphics  
    - xf86-video-amdgpu
    - vulkan-radeon
EOF
fi
EOF

# Update Calamares settings to include packages module
cat > /etc/calamares/settings.conf << 'EOF'
modules-search: [ local ]
instances:
- id: before
  module: shellprocess
  config: shellprocess_before.conf
- id: after  
  module: shellprocess
  config: shellprocess_after.conf

sequence:
- show:
  - welcome
  - locale
  - keyboard
  - partition
  - users
  - summary
- exec:
  - partition
  - mount
  - unpackfs
  - machineid
  - fstab
  - locale
  - keyboard
  - localecfg
  - users
  - displaymanager
  - networkcfg
  - hwclock
  - services-systemd
  - packages
  - shellprocess@before
  - bootloader
  - shellprocess@after
  - umount
- show:
  - finished

branding: houer
prompt-install: true
dont-chroot: false
oem-setup: false
disable-cancel: false
disable-cancel-during-exec: false
hide-back-and-next-during-exec: false
quit-at-end: false
EOF

# Create post-installation script
cat > /etc/calamares/modules/shellprocess_after.conf << 'EOF'
dontChroot: false
timeout: 999
script:
    - command: "/opt/houer-installer/installer/post-install.sh"
      timeout: 300
EOF

log "Live environment setup completed successfully!"
log ""
info "HoUer OS is ready for installation!"
info ""
info "Next steps:"
info "1. Run: sudo calamares"
info "2. Follow the installation wizard"
info "3. The installer will automatically configure HoUer OS"
info ""
info "Starting Calamares installer..."

# Launch Calamares
calamares &

info "Calamares installer has been launched."
info "Please follow the installation wizard to install HoUer OS." 