#!/bin/bash
# MuxOS ISO Build Script

set -Eeuo pipefail

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
source "$PROJECT_ROOT/config/muxos.conf"

# Build directories
BUILD_DIR="$PROJECT_ROOT/build"
CHROOT_DIR="$BUILD_DIR/chroot"
ISO_DIR="$BUILD_DIR/iso"
WORK_DIR="$BUILD_DIR/work"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    log_error "This script must be run as root"
    exit 1
fi

# Dependency check (SAFETY)
for bin in debootstrap mksquashfs grub-mkrescue xorriso; do
    command -v "$bin" >/dev/null || {
        log_error "Missing dependency: $bin"
        exit 1
    }
done

# Clean previous build
log_info "Cleaning previous build..."
rm -rf "$BUILD_DIR"
mkdir -p "$CHROOT_DIR" "$ISO_DIR" "$WORK_DIR"

# Create base system
log_info "Creating base system with debootstrap..."
debootstrap --arch="$ARCH" "$BASE_RELEASE" "$CHROOT_DIR" http://deb.debian.org/debian/

# Mount necessary filesystems
log_info "Mounting filesystems..."
mount --bind /dev "$CHROOT_DIR/dev"
mount --bind /dev/pts "$CHROOT_DIR/dev/pts"
mount --bind /proc "$CHROOT_DIR/proc"
mount --bind /sys "$CHROOT_DIR/sys"

cleanup() {
    log_info "Cleaning up..."
    umount -lf "$CHROOT_DIR/dev/pts" 2>/dev/null || true
    umount -lf "$CHROOT_DIR/dev" 2>/dev/null || true
    umount -lf "$CHROOT_DIR/proc" 2>/dev/null || true
    umount -lf "$CHROOT_DIR/sys" 2>/dev/null || true
}
trap cleanup EXIT

# Configure APT sources
log_info "Configuring APT sources..."
cat > "$CHROOT_DIR/etc/apt/sources.list" <<EOF
deb http://deb.debian.org/debian/ $BASE_RELEASE main contrib non-free non-free-firmware
deb http://deb.debian.org/debian/ $BASE_RELEASE-updates main contrib non-free non-free-firmware
deb http://security.debian.org/debian-security $BASE_RELEASE-security main contrib non-free non-free-firmware
EOF

# Install base packages
log_info "Installing base packages..."
chroot "$CHROOT_DIR" /bin/bash <<'CHROOT_COMMANDS'
export DEBIAN_FRONTEND=noninteractive
apt update
apt install -y \
    linux-image-amd64 \
    linux-headers-amd64 \
    firmware-linux \
    firmware-linux-nonfree \
    grub-pc-bin \
    grub-efi-amd64-bin \
    live-boot \
    systemd-sysv \
    network-manager \
    network-manager-gnome \
    wireless-tools \
    wpasupplicant \
    bluez \
    blueman
CHROOT_COMMANDS

# Install X.org and desktop environment
log_info "Installing desktop environment..."
chroot "$CHROOT_DIR" /bin/bash <<'CHROOT_COMMANDS'
export DEBIAN_FRONTEND=noninteractive
apt install -y \
    xorg \
    xserver-xorg-video-all \
    openbox \
    obconf \
    picom \
    tint2 \
    lightdm \
    lightdm-gtk-greeter \
    lightdm-gtk-greeter-settings \
    feh \
    rofi \
    dunst \
    volumeicon-alsa \
    network-manager-gnome \
    polkit-1 \
    policykit-1-gnome
CHROOT_COMMANDS

# Install applications
log_info "Installing applications..."
chroot "$CHROOT_DIR" /bin/bash <<'CHROOT_COMMANDS'
export DEBIAN_FRONTEND=noninteractive
apt install -y \
    pcmanfm \
    xfce4-terminal \
    firefox-esr \
    mousepad \
    gpicview \
    xarchiver \
    mpv \
    evince \
    synaptic \
    arandr \
    vlc \
    libreoffice \
    thunderbird \
    transmission-gtk \
    gimp \
    keepassxc \
    gnupg \
    unattended-upgrades \
    apparmor \
    apparmor-utils \
    pulseaudio \
    pavucontrol \
    alsa-utils \
    python3 \
    python3-gi \
    python3-gi-cairo \
    gir1.2-gtk-3.0 \
    python3-psutil \
    htop \
    neofetch \
    git \
    wget \
    curl \
    unzip \
    zip \
    p7zip-full \
    locales \
    fonts-noto \
    fonts-noto-color-emoji \
    fonts-noto-cjk \
    udisks2 \
    gvfs \
    gvfs-backends \
    udiskie \
    exfatprogs \
    ntfs-3g
CHROOT_COMMANDS

# Install gaming packages
log_info "Installing gaming packages..."
chroot "$CHROOT_DIR" /bin/bash <<'CHROOT_COMMANDS'
export DEBIAN_FRONTEND=noninteractive
dpkg --add-architecture i386
apt update
apt install -y \
    gamemode \
    lib32gcc-s1 \
    lib32stdc++6 \
    mesa-vulkan-drivers \
    mesa-vulkan-drivers:i386 \
    libgl1-mesa-dri:i386 \
    vulkan-tools \
    wine \
    wine32 \
    wine64 \
    winetricks
CHROOT_COMMANDS

# Copy MuxOS files
log_info "Copying MuxOS configuration files..."

mkdir -p "$CHROOT_DIR/etc/xdg/openbox"
cp "$PROJECT_ROOT/desktop/openbox/rc.xml" "$CHROOT_DIR/etc/xdg/openbox/"
cp "$PROJECT_ROOT/desktop/openbox/autostart" "$CHROOT_DIR/etc/xdg/openbox/"
chmod +x "$CHROOT_DIR/etc/xdg/openbox/autostart"

mkdir -p "$CHROOT_DIR/etc/xdg/picom"
cp "$PROJECT_ROOT/desktop/picom/picom.conf" "$CHROOT_DIR/etc/xdg/picom/"

mkdir -p "$CHROOT_DIR/etc/xdg/tint2"
cp "$PROJECT_ROOT/desktop/tint2/tint2rc" "$CHROOT_DIR/etc/xdg/tint2/"

mkdir -p "$CHROOT_DIR/etc/lightdm"
cp "$PROJECT_ROOT/desktop/lightdm/lightdm-gtk-greeter.conf" "$CHROOT_DIR/etc/lightdm/"

mkdir -p "$CHROOT_DIR/usr/share/muxos/optimizations"
cp "$PROJECT_ROOT/system/optimizations/gaming-tweaks.sh" "$CHROOT_DIR/usr/share/muxos/optimizations/"
chmod +x "$CHROOT_DIR/usr/share/muxos/optimizations/gaming-tweaks.sh"

mkdir -p "$CHROOT_DIR/usr/share/muxos"
cp "$PROJECT_ROOT/config/muxos.conf" "$CHROOT_DIR/etc/muxos.conf" 2>/dev/null || true
cp "$PROJECT_ROOT/config/muxos.conf" "$CHROOT_DIR/usr/share/muxos/muxos.conf" 2>/dev/null || true

mkdir -p "$CHROOT_DIR/usr/share/muxos/drivers"
cp "$PROJECT_ROOT/system/drivers/"*.sh "$CHROOT_DIR/usr/share/muxos/drivers/"
chmod +x "$CHROOT_DIR/usr/share/muxos/drivers/"*.sh

mkdir -p "$CHROOT_DIR/usr/bin"
cp "$PROJECT_ROOT/apps/control-panel/muxos-control-panel-v2.py" "$CHROOT_DIR/usr/bin/muxos-control-panel" 2>/dev/null || \
cp "$PROJECT_ROOT/apps/control-panel/muxos-control-panel.py" "$CHROOT_DIR/usr/bin/muxos-control-panel"
cp "$PROJECT_ROOT/apps/system-monitor/muxos-monitor.py" "$CHROOT_DIR/usr/bin/muxos-monitor"
cp "$PROJECT_ROOT/apps/system-monitor/muxos-hardware-detector.py" "$CHROOT_DIR/usr/bin/muxos-hardware-detector" 2>/dev/null || true
cp "$PROJECT_ROOT/apps/system-monitor/muxos-enhanced-monitor.py" "$CHROOT_DIR/usr/bin/muxos-enhanced-monitor" 2>/dev/null || true
cp "$PROJECT_ROOT/apps/security/muxos-security-center.py" "$CHROOT_DIR/usr/bin/muxos-security-center" 2>/dev/null || true
cp "$PROJECT_ROOT/apps/storage/muxos-disk-manager.py" "$CHROOT_DIR/usr/bin/muxos-disk-manager" 2>/dev/null || true
cp "$PROJECT_ROOT/apps/gaming/muxos-game-center.py" "$CHROOT_DIR/usr/bin/muxos-game-center" 2>/dev/null || true
cp "$PROJECT_ROOT/apps/updater/muxos-updater.py" "$CHROOT_DIR/usr/bin/muxos-updater" 2>/dev/null || true
cp "$PROJECT_ROOT/apps/utilities/muxos-task-manager.py" "$CHROOT_DIR/usr/bin/muxos-task-manager" 2>/dev/null || true
cp "$PROJECT_ROOT/apps/utilities/muxos-screenshot.py" "$CHROOT_DIR/usr/bin/muxos-screenshot" 2>/dev/null || true
cp "$PROJECT_ROOT/apps/utilities/muxos-notes.py" "$CHROOT_DIR/usr/bin/muxos-notes" 2>/dev/null || true
cp "$PROJECT_ROOT/apps/utilities/muxos-calculator.py" "$CHROOT_DIR/usr/bin/muxos-calculator" 2>/dev/null || true
cp "$PROJECT_ROOT/apps/welcome/muxos-welcome.py" "$CHROOT_DIR/usr/bin/muxos-welcome" 2>/dev/null || true
chmod +x "$CHROOT_DIR/usr/bin/muxos-"*

mkdir -p "$CHROOT_DIR/usr/share/applications"
cp "$PROJECT_ROOT/apps/desktop-entries/"*.desktop "$CHROOT_DIR/usr/share/applications/" 2>/dev/null || true
cp "$PROJECT_ROOT/apps/control-panel/"*.desktop "$CHROOT_DIR/usr/share/applications/" 2>/dev/null || true
cp "$PROJECT_ROOT/apps/system-monitor/"*.desktop "$CHROOT_DIR/usr/share/applications/" 2>/dev/null || true
cp "$PROJECT_ROOT/apps/updater/"*.desktop "$CHROOT_DIR/usr/share/applications/" 2>/dev/null || true

mkdir -p "$CHROOT_DIR/usr/lib/muxos"
cp "$PROJECT_ROOT/system/setup/muxos-firstboot-helper.py" "$CHROOT_DIR/usr/lib/muxos/muxos-firstboot-helper.py" 2>/dev/null || true
chmod +x "$CHROOT_DIR/usr/lib/muxos/muxos-firstboot-helper.py" 2>/dev/null || true

mkdir -p "$CHROOT_DIR/usr/share/polkit-1/actions"
cp "$PROJECT_ROOT/system/polkit/com.muxos.firstboot.policy" "$CHROOT_DIR/usr/share/polkit-1/actions/" 2>/dev/null || true
cp "$PROJECT_ROOT/system/polkit/com.muxos.security.policy" "$CHROOT_DIR/usr/share/polkit-1/actions/" 2>/dev/null || true
cp "$PROJECT_ROOT/system/polkit/com.muxos.updater.policy" "$CHROOT_DIR/usr/share/polkit-1/actions/" 2>/dev/null || true

cp "$PROJECT_ROOT/system/security/muxos-security-helper.py" "$CHROOT_DIR/usr/lib/muxos/" 2>/dev/null || true
chmod +x "$CHROOT_DIR/usr/lib/muxos/muxos-security-helper.py" 2>/dev/null || true

cp "$PROJECT_ROOT/system/updater/muxos-update-helper.py" "$CHROOT_DIR/usr/lib/muxos/" 2>/dev/null || true
chmod +x "$CHROOT_DIR/usr/lib/muxos/muxos-update-helper.py" 2>/dev/null || true

mkdir -p "$CHROOT_DIR/etc/systemd/system"
cp "$PROJECT_ROOT/system/services/muxos-gamemode.service" "$CHROOT_DIR/etc/systemd/system/"

# Enable services (LIVE SAFE)
ln -sf /lib/systemd/system/lightdm.service \
    "$CHROOT_DIR/etc/systemd/system/display-manager.service"
ln -sf /lib/systemd/system/NetworkManager.service \
    "$CHROOT_DIR/etc/systemd/system/multi-user.target.wants/NetworkManager.service"

# Hostname
echo "$DEFAULT_HOSTNAME" > "$CHROOT_DIR/etc/hostname"

# Create user (kept as original)
chroot "$CHROOT_DIR" /bin/bash <<EOF
useradd -m -s /bin/bash -G sudo,audio,video,plugdev,netdev $DEFAULT_USER
echo "$DEFAULT_USER:muxos" | chpasswd
echo "root:muxos" | chpasswd
EOF

# Cleanup chroot
log_info "Cleaning up chroot..."
chroot "$CHROOT_DIR" apt clean
rm -rf "$CHROOT_DIR/var/lib/apt/lists/"*
rm -rf "$CHROOT_DIR/tmp/"*

# Create squashfs
log_info "Creating squashfs filesystem..."
mkdir -p "$ISO_DIR/live"
mksquashfs "$CHROOT_DIR" "$ISO_DIR/live/filesystem.squashfs" -comp xz -b 1M -noappend

# Kernel & initrd (FIX)
VMLINUX=$(ls "$CHROOT_DIR"/boot/vmlinuz-* | tail -n1)
INITRD=$(ls "$CHROOT_DIR"/boot/initrd.img-* | tail -n1)
cp "$VMLINUX" "$ISO_DIR/live/vmlinuz"
cp "$INITRD" "$ISO_DIR/live/initrd"

# GRUB
log_info "Creating GRUB configuration..."
mkdir -p "$ISO_DIR/boot/grub"
cat > "$ISO_DIR/boot/grub/grub.cfg" <<EOF
set timeout=5
set default=0

menuentry "MuxOS - Live" {
    linux /live/vmlinuz boot=live quiet splash
    initrd /live/initrd
}

menuentry "MuxOS - Live (Safe Mode)" {
    linux /live/vmlinuz boot=live nomodeset
    initrd /live/initrd
}
EOF

# Create ISO
log_info "Creating bootable ISO..."
grub-mkrescue -o "$BUILD_DIR/$ISO_NAME" "$ISO_DIR" --compress=xz

# Checksum
log_info "Calculating checksum..."
cd "$BUILD_DIR"
sha256sum "$ISO_NAME" > "$ISO_NAME.sha256"

log_info "Build complete!"
log_info "ISO location: $BUILD_DIR/$ISO_NAME"
log_info "SHA256: $(cat $ISO_NAME.sha256)"
log_info ""
log_info "To create a bootable USB:"
log_info "  sudo dd if=$BUILD_DIR/$ISO_NAME of=/dev/sdX bs=4M status=progress"
log_info "  (Replace /dev/sdX with your USB device)"
