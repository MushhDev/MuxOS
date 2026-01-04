#!/bin/bash
# AMD Driver Installation Script for MuxOS

set -e

echo "MuxOS AMD Driver Installer"
echo "=========================="

# Check if AMD GPU is present
if ! lspci | grep -i amd | grep -i vga > /dev/null; then
    echo "Error: No AMD GPU detected!"
    exit 1
fi

echo "AMD GPU detected. Installing drivers..."

# Update package list
apt update

# Install Mesa drivers (open-source AMD drivers)
echo "Installing Mesa drivers..."
apt install -y \
    mesa-vulkan-drivers \
    mesa-vulkan-drivers:i386 \
    libgl1-mesa-dri \
    libgl1-mesa-dri:i386 \
    libglx-mesa0 \
    libglx-mesa0:i386 \
    mesa-va-drivers \
    mesa-vdpau-drivers \
    libdrm-amdgpu1 \
    xserver-xorg-video-amdgpu

# Install additional AMD tools
echo "Installing AMD tools..."
apt install -y \
    radeontop \
    clinfo \
    vulkan-tools

# Install firmware
echo "Installing AMD firmware..."
apt install -y \
    firmware-amd-graphics \
    firmware-linux-nonfree

# Configure AMD settings for gaming
echo "Configuring AMD for gaming..."
mkdir -p /etc/X11/xorg.conf.d/

cat > /etc/X11/xorg.conf.d/20-amdgpu.conf <<EOF
Section "Device"
    Identifier "AMD Graphics"
    Driver "amdgpu"
    Option "TearFree" "true"
    Option "DRI" "3"
    Option "VariableRefresh" "true"
EndSection
EOF

# Set performance profile
cat > /etc/udev/rules.d/30-amdgpu-pm.rules <<EOF
KERNEL=="card0", SUBSYSTEM=="drm", DRIVERS=="amdgpu", ATTR{device/power_dpm_force_performance_level}="high"
EOF

# Create modprobe configuration for optimal gaming
cat > /etc/modprobe.d/amdgpu.conf <<EOF
options amdgpu ppfeaturemask=0xffffffff
options amdgpu gpu_recovery=1
EOF

# Update initramfs
update-initramfs -u

echo ""
echo "AMD drivers installed successfully!"
echo "Please reboot your system for changes to take effect."
echo ""
echo "After reboot, you can:"
echo "  - Run 'radeontop' to monitor GPU usage"
echo "  - Run 'vulkaninfo' to check Vulkan support"
echo "  - Check GPU info with 'lspci -k | grep -A 3 VGA'"
