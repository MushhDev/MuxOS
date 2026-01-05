#!/bin/bash
# MuxOS ISO Build Script v2 - Fixed for Debian 12/13

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
source "$PROJECT_ROOT/config/muxos.conf"

BUILD_DIR="$PROJECT_ROOT/build"
CHROOT_DIR="$BUILD_DIR/chroot"
ISO_DIR="$BUILD_DIR/iso"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

[ "$EUID" -ne 0 ] && { log_error "Run as root"; exit 1; }

log_info "Cleaning previous build..."
rm -rf "$BUILD_DIR"
mkdir -p "$CHROOT_DIR" "$ISO_DIR"

log_info "Creating base system..."
debootstrap --arch="$ARCH" "$BASE_RELEASE" "$CHROOT_DIR" http://deb.debian.org/debian/

mount --bind /dev "$CHROOT_DIR/dev"
mount --bind /dev/pts "$CHROOT_DIR/dev/pts"
mount --bind /proc "$CHROOT_DIR/proc"
mount --bind /sys "$CHROOT_DIR/sys"

cleanup() {
    umount -lf "$CHROOT_DIR/dev/pts" 2>/dev/null || true
    umount -lf "$CHROOT_DIR/dev" 2>/dev/null || true
    umount -lf "$CHROOT_DIR/proc" 2>/dev/null || true
    umount -lf "$CHROOT_DIR/sys" 2>/dev/null || true
}
trap cleanup EXIT

cat > "$CHROOT_DIR/etc/apt/sources.list" <<EOF
deb http://deb.debian.org/debian $BASE_RELEASE main contrib non-free non-free-firmware
deb http://deb.debian.org/debian $BASE_RELEASE-updates main contrib non-free non-free-firmware
deb http://security.debian.org/debian-security $BASE_RELEASE-security main contrib non-free non-free-firmware
EOF

log_info "Installing base packages..."
chroot "$CHROOT_DIR" /bin/bash <<'CHROOT'
export DEBIAN_FRONTEND=noninteractive
apt update
apt upgrade -y

apt install -y \
    linux-image-amd64 linux-headers-amd64 firmware-linux firmware-linux-nonfree \
    grub-pc-bin grub-efi-amd64-bin live-boot systemd-sysv \
    network-manager network-manager-gnome wireless-tools wpasupplicant \
    bluez blueman \
    xorg xserver-xorg-video-all openbox obconf picom tint2 \
    lightdm lightdm-gtk-greeter feh rofi dunst lxappearance \
    polkit policykit-1-gnome volumeicon-alsa \
    locales fonts-noto fonts-noto-color-emoji fonts-noto-cjk \
    udisks2 gvfs gvfs-backends udiskie exfatprogs ntfs-3g
CHROOT

log_info "Installing applications..."
chroot "$CHROOT_DIR" /bin/bash <<'CHROOT'
export DEBIAN_FRONTEND=noninteractive
apt install -y \
    pcmanfm xfce4-terminal firefox-esr mousepad gpicview xarchiver mpv \
    evince synaptic arandr vlc libreoffice thunderbird transmission-gtk gimp \
    keepassxc gnupg unattended-upgrades apparmor apparmor-utils \
    pulseaudio pavucontrol alsa-utils \
    python3 python3-gi python3-gi-cairo gir1.2-gtk-3.0 python3-psutil \
    htop neofetch git wget curl unzip zip p7zip-full scrot xclip \
    gnome-disk-utility baobab gparted \
    ufw fail2ban rkhunter chkrootkit aide auditd \
    libnotify-bin notify-osd
CHROOT

log_info "Installing gaming packages..."
chroot "$CHROOT_DIR" /bin/bash <<'CHROOT'
export DEBIAN_FRONTEND=noninteractive
dpkg --add-architecture i386
apt update
apt install -y \
    gamemode lib32gcc-s1 lib32stdc++6 \
    mesa-vulkan-drivers mesa-vulkan-drivers:i386 \
    libgl1-mesa-dri:i386 vulkan-tools \
    wine wine32 wine64 winetricks
CHROOT

log_info "Copying MuxOS applications..."

mkdir -p "$CHROOT_DIR/usr/bin" \
         "$CHROOT_DIR/usr/share/applications" \
         "$CHROOT_DIR/usr/share/muxos" \
         "$CHROOT_DIR/usr/lib/muxos" \
         "$CHROOT_DIR/usr/share/polkit-1/actions"

cp "$PROJECT_ROOT/apps/"**/*.py "$CHROOT_DIR/usr/bin/" 2>/dev/null || true
chmod +x "$CHROOT_DIR/usr/bin/muxos-"*

cp "$PROJECT_ROOT/apps/"**/*.desktop "$CHROOT_DIR/usr/share/applications/" 2>/dev/null || true

cp "$PROJECT_ROOT/system/polkit/"*.policy "$CHROOT_DIR/usr/share/polkit-1/actions/" 2>/dev/null || true

log_info "Configuring system..."
chroot "$CHROOT_DIR" /bin/bash <<CHROOT
systemctl enable lightdm NetworkManager
useradd -m -s /bin/bash -G sudo,audio,video,plugdev,netdev $DEFAULT_USER
echo "$DEFAULT_USER:muxos" | chpasswd
echo "root:muxos" | chpasswd
CHROOT

echo "$DEFAULT_HOSTNAME" > "$CHROOT_DIR/etc/hostname"

log_info "Applying security hardening..."
chroot "$CHROOT_DIR" /bin/bash <<'CHROOT'
ufw --force enable
ufw default deny incoming
ufw default allow outgoing
CHROOT

log_info "Cleaning up..."
chroot "$CHROOT_DIR" apt clean
rm -rf "$CHROOT_DIR/var/lib/apt/lists/"* "$CHROOT_DIR/tmp/"*

log_info "Creating squashfs..."
mkdir -p "$ISO_DIR/live"
mksquashfs "$CHROOT_DIR" "$ISO_DIR/live/filesystem.squashfs" -comp xz -b 1M

cp "$CHROOT_DIR/boot/vmlinuz-"* "$ISO_DIR/live/vmlinuz"
cp "$CHROOT_DIR/boot/initrd.img-"* "$ISO_DIR/live/initrd"

log_info "Creating GRUB..."
mkdir -p "$ISO_DIR/boot/grub"
cat > "$ISO_DIR/boot/grub/grub.cfg" <<EOF
set timeout=5
set default=0

menuentry "MuxOS Live" {
    linux /live/vmlinuz boot=live quiet splash
    initrd /live/initrd
}
EOF

log_info "Building ISO..."
grub-mkrescue -o "$BUILD_DIR/$ISO_NAME" "$ISO_DIR"

cd "$BUILD_DIR"
sha256sum "$ISO_NAME" > "$ISO_NAME.sha256"

log_info "Build complete!"
log_info "ISO: $BUILD_DIR/$ISO_NAME"
