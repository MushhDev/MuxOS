#!/bin/bash
# MuxOS Velocity 2.0 - ISO Build Script
# Pure Linux Gaming Distribution

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

# Check if running in restricted environment (noexec/nodev)
if mount | grep -q "$BUILD_DIR.*\(noexec\|nodev\)"; then
    log_warn "Detected noexec/nodev mount restrictions"
    log_info "Creating temporary directory with proper permissions..."
    
    # Create temp directory in /tmp (usually has exec permissions)
    TEMP_BUILD="/tmp/muxos-build-$$"
    mkdir -p "$TEMP_BUILD"
    
    # Update paths to use temp directory
    CHROOT_DIR="$TEMP_BUILD/chroot"
    ISO_DIR="$TEMP_BUILD/iso"
    mkdir -p "$CHROOT_DIR" "$ISO_DIR"
    
    log_info "Using temporary build directory: $TEMP_BUILD"
    
    # Update cleanup function
    cleanup() {
        umount -lf "$CHROOT_DIR/dev/pts" 2>/dev/null || true
        umount -lf "$CHROOT_DIR/dev" 2>/dev/null || true
        umount -lf "$CHROOT_DIR/proc" 2>/dev/null || true
        umount -lf "$CHROOT_DIR/sys" 2>/dev/null || true
        # Copy final ISO to original location if build succeeds
        if [ -f "$TEMP_BUILD/$ISO_NAME" ]; then
            cp "$TEMP_BUILD/$ISO_NAME" "$BUILD_DIR/"
            cp "$TEMP_BUILD/$ISO_NAME.sha256" "$BUILD_DIR/" 2>/dev/null || true
        fi
        rm -rf "$TEMP_BUILD"
    }
    trap cleanup EXIT
fi

log_info "Creating base system..."
debootstrap --arch="$ARCH" "$BASE_RELEASE" "$CHROOT_DIR" http://deb.debian.org/debian/

mount --bind /dev "$CHROOT_DIR/dev"
mount --bind /dev/pts "$CHROOT_DIR/dev/pts"
mount --bind /proc "$CHROOT_DIR/proc"
mount --bind /sys "$CHROOT_DIR/sys"

# Only set trap if not already set by restricted environment handler
if ! mount | grep -q "$BUILD_DIR.*\(noexec\|nodev\)"; then
    cleanup() {
        umount -lf "$CHROOT_DIR/dev/pts" 2>/dev/null || true
        umount -lf "$CHROOT_DIR/dev" 2>/dev/null || true
        umount -lf "$CHROOT_DIR/proc" 2>/dev/null || true
        umount -lf "$CHROOT_DIR/sys" 2>/dev/null || true
    }
    trap cleanup EXIT
fi

cat > "$CHROOT_DIR/etc/apt/sources.list" <<EOF
deb http://deb.debian.org/debian/ $BASE_RELEASE main contrib non-free non-free-firmware
deb http://deb.debian.org/debian/ $BASE_RELEASE-updates main contrib non-free non-free-firmware
deb http://security.debian.org/debian-security $BASE_RELEASE-security main contrib non-free non-free-firmware
EOF

log_info "Installing base packages..."
chroot "$CHROOT_DIR" /bin/bash <<'CHROOT'
export DEBIAN_FRONTEND=noninteractive
apt update && apt upgrade -y
apt install -y \
    linux-image-amd64 linux-headers-amd64 firmware-linux firmware-linux-nonfree \
    grub-pc-bin grub-efi-amd64-bin live-boot systemd-sysv \
    network-manager network-manager-gnome wireless-tools wpasupplicant \
    bluez blueman \
    xorg xserver-xorg-video-all openbox obconf picom tint2 \
    lightdm lightdm-gtk-greeter feh rofi dunst lxappearance \
    polkit-1 polkitd-gnome volumeicon-alsa network-manager-gnome \
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

mkdir -p "$CHROOT_DIR/usr/bin"
mkdir -p "$CHROOT_DIR/usr/share/applications"
mkdir -p "$CHROOT_DIR/usr/share/muxos"

# Copy all Python applications
cp "$PROJECT_ROOT/apps/control-panel/muxos-control-center.py" "$CHROOT_DIR/usr/bin/muxos-control-center"
cp "$PROJECT_ROOT/apps/control-panel/muxos-control-panel.py" "$CHROOT_DIR/usr/bin/muxos-control-panel" 2>/dev/null || true
cp "$PROJECT_ROOT/apps/system-monitor/muxos-monitor.py" "$CHROOT_DIR/usr/bin/muxos-monitor"
cp "$PROJECT_ROOT/apps/system-monitor/muxos-hardware-detector.py" "$CHROOT_DIR/usr/bin/muxos-hardware-detector"
cp "$PROJECT_ROOT/apps/system-monitor/muxos-enhanced-monitor.py" "$CHROOT_DIR/usr/bin/muxos-enhanced-monitor"
cp "$PROJECT_ROOT/apps/security/muxos-security-center.py" "$CHROOT_DIR/usr/bin/muxos-security-center"
cp "$PROJECT_ROOT/apps/storage/muxos-disk-manager.py" "$CHROOT_DIR/usr/bin/muxos-disk-manager"
cp "$PROJECT_ROOT/apps/gaming/muxos-game-center.py" "$CHROOT_DIR/usr/bin/muxos-game-center"
cp "$PROJECT_ROOT/apps/updater/muxos-updater.py" "$CHROOT_DIR/usr/bin/muxos-updater"
cp "$PROJECT_ROOT/apps/utilities/muxos-task-manager.py" "$CHROOT_DIR/usr/bin/muxos-task-manager"
cp "$PROJECT_ROOT/apps/utilities/muxos-screenshot.py" "$CHROOT_DIR/usr/bin/muxos-screenshot"
cp "$PROJECT_ROOT/apps/utilities/muxos-notes.py" "$CHROOT_DIR/usr/bin/muxos-notes"
cp "$PROJECT_ROOT/apps/utilities/muxos-calculator.py" "$CHROOT_DIR/usr/bin/muxos-calculator"
cp "$PROJECT_ROOT/apps/welcome/muxos-welcome.py" "$CHROOT_DIR/usr/bin/muxos-welcome"

chmod +x "$CHROOT_DIR/usr/bin/muxos-"*

# Copy desktop entries
cp "$PROJECT_ROOT/apps/desktop-entries/"*.desktop "$CHROOT_DIR/usr/share/applications/"
cp "$PROJECT_ROOT/apps/control-panel/"*.desktop "$CHROOT_DIR/usr/share/applications/" 2>/dev/null || true
cp "$PROJECT_ROOT/apps/system-monitor/"*.desktop "$CHROOT_DIR/usr/share/applications/" 2>/dev/null || true
cp "$PROJECT_ROOT/apps/updater/"*.desktop "$CHROOT_DIR/usr/share/applications/" 2>/dev/null || true

# Copy system files
mkdir -p "$CHROOT_DIR/usr/share/muxos/optimizations"
mkdir -p "$CHROOT_DIR/usr/share/muxos/drivers"
mkdir -p "$CHROOT_DIR/usr/share/muxos/security"
mkdir -p "$CHROOT_DIR/usr/share/muxos"
mkdir -p "$CHROOT_DIR/etc"

mkdir -p "$CHROOT_DIR/usr/lib/muxos"
mkdir -p "$CHROOT_DIR/usr/share/polkit-1/actions"

cp "$PROJECT_ROOT/system/optimizations/"*.sh "$CHROOT_DIR/usr/share/muxos/optimizations/"
cp "$PROJECT_ROOT/system/drivers/"*.sh "$CHROOT_DIR/usr/share/muxos/drivers/"
cp "$PROJECT_ROOT/system/security/"*.sh "$CHROOT_DIR/usr/share/muxos/security/"

cp "$PROJECT_ROOT/config/muxos.conf" "$CHROOT_DIR/etc/muxos.conf"
cp "$PROJECT_ROOT/config/muxos.conf" "$CHROOT_DIR/usr/share/muxos/muxos.conf"

cp "$PROJECT_ROOT/system/setup/muxos-firstboot-helper.py" "$CHROOT_DIR/usr/lib/muxos/muxos-firstboot-helper.py"
chmod +x "$CHROOT_DIR/usr/lib/muxos/muxos-firstboot-helper.py"

cp "$PROJECT_ROOT/system/security/muxos-security-helper.py" "$CHROOT_DIR/usr/lib/muxos/muxos-security-helper.py"
chmod +x "$CHROOT_DIR/usr/lib/muxos/muxos-security-helper.py"

cp "$PROJECT_ROOT/system/updater/muxos-update-helper.py" "$CHROOT_DIR/usr/lib/muxos/muxos-update-helper.py"
chmod +x "$CHROOT_DIR/usr/lib/muxos/muxos-update-helper.py"

cp "$PROJECT_ROOT/system/polkit/com.muxos.firstboot.policy" "$CHROOT_DIR/usr/share/polkit-1/actions/com.muxos.firstboot.policy"
cp "$PROJECT_ROOT/system/polkit/com.muxos.security.policy" "$CHROOT_DIR/usr/share/polkit-1/actions/com.muxos.security.policy"
cp "$PROJECT_ROOT/system/polkit/com.muxos.updater.policy" "$CHROOT_DIR/usr/share/polkit-1/actions/com.muxos.updater.policy"
chmod +x "$CHROOT_DIR/usr/share/muxos/"*/*.sh

# Copy desktop configuration
mkdir -p "$CHROOT_DIR/etc/xdg/openbox"
cp "$PROJECT_ROOT/desktop/openbox/rc.xml" "$CHROOT_DIR/etc/xdg/openbox/"
cp "$PROJECT_ROOT/desktop/openbox/autostart" "$CHROOT_DIR/etc/xdg/openbox/"
chmod +x "$CHROOT_DIR/etc/xdg/openbox/autostart"

mkdir -p "$CHROOT_DIR/etc/xdg/picom"
cp "$PROJECT_ROOT/desktop/picom/picom.conf" "$CHROOT_DIR/etc/xdg/picom/"

mkdir -p "$CHROOT_DIR/etc/xdg/tint2"
cp "$PROJECT_ROOT/desktop/tint2/tint2rc" "$CHROOT_DIR/etc/xdg/tint2/"

mkdir -p "$CHROOT_DIR/etc/xdg/rofi"
cp "$PROJECT_ROOT/desktop/rofi/config.rasi" "$CHROOT_DIR/etc/xdg/rofi/"

mkdir -p "$CHROOT_DIR/etc/xdg/dunst"
cp "$PROJECT_ROOT/desktop/dunst/dunstrc" "$CHROOT_DIR/etc/xdg/dunst/"

cp "$PROJECT_ROOT/desktop/lightdm/lightdm-gtk-greeter.conf" "$CHROOT_DIR/etc/lightdm/"

# Copy GTK theme
mkdir -p "$CHROOT_DIR/usr/share/themes/MuxOS-Velocity"
cp -r "$PROJECT_ROOT/desktop/themes/MuxOS-Velocity/"* "$CHROOT_DIR/usr/share/themes/MuxOS-Velocity/"

# Copy systemd services
cp "$PROJECT_ROOT/system/services/"*.service "$CHROOT_DIR/etc/systemd/system/"

log_info "Configuring system..."
chroot "$CHROOT_DIR" /bin/bash <<CHROOT
systemctl enable lightdm NetworkManager polkit
useradd -m -s /bin/bash -G sudo,audio,video,plugdev,netdev,polkitd $DEFAULT_USER
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
insmod all_video
set gfxmode=auto
terminal_output gfxterm

menuentry "MuxOS - Live" {
    linux /live/vmlinuz boot=live quiet splash
    initrd /live/initrd
}
menuentry "MuxOS - Safe Mode" {
    linux /live/vmlinuz boot=live nomodeset
    initrd /live/initrd
}
EOF

log_info "Building ISO..."
# Use TEMP_BUILD path if in restricted environment
if [ -n "$TEMP_BUILD" ]; then
    cd "$TEMP_BUILD"
    grub-mkrescue -o "$TEMP_BUILD/$ISO_NAME" "$ISO_DIR"
    sha256sum "$ISO_NAME" > "$ISO_NAME.sha256"
    cd "$BUILD_DIR"
else
    cd "$BUILD_DIR"
    grub-mkrescue -o "$BUILD_DIR/$ISO_NAME" "$ISO_DIR"
    sha256sum "$ISO_NAME" > "$ISO_NAME.sha256"
fi

log_info "Build complete!"
log_info "ISO: $BUILD_DIR/$ISO_NAME"
log_info "SHA256: $(cat $ISO_NAME.sha256)"
