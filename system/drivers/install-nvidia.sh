#!/bin/bash
# NVIDIA Driver Installation Script for MuxOS

set -e

echo "MuxOS NVIDIA Driver Installer"
echo "=============================="

# Check if NVIDIA GPU is present
if ! lspci | grep -i nvidia > /dev/null; then
    echo "Error: No NVIDIA GPU detected!"
    exit 1
fi

echo "NVIDIA GPU detected. Installing drivers..."

# Add non-free repositories
echo "Adding non-free repositories..."
sed -i 's/main$/main contrib non-free non-free-firmware/' /etc/apt/sources.list

# Update package list
apt update

# Install NVIDIA drivers
echo "Installing NVIDIA drivers..."
apt install -y \
    nvidia-driver \
    nvidia-settings \
    nvidia-vulkan-icd \
    nvidia-cuda-toolkit \
    libgl1-nvidia-glvnd-glx \
    libglx-nvidia0 \
    libnvidia-cfg1 \
    libnvidia-encode1 \
    libnvidia-fbc1 \
    libnvidia-ml1

# Install 32-bit libraries for gaming
echo "Installing 32-bit libraries..."
dpkg --add-architecture i386
apt update
apt install -y \
    nvidia-driver-libs:i386 \
    libgl1-nvidia-glvnd-glx:i386 \
    libnvidia-encode1:i386

# Configure NVIDIA settings for gaming
echo "Configuring NVIDIA for gaming..."
mkdir -p /etc/X11/xorg.conf.d/

cat > /etc/X11/xorg.conf.d/20-nvidia.conf <<EOF
Section "Device"
    Identifier     "NVIDIA Card"
    Driver         "nvidia"
    VendorName     "NVIDIA Corporation"
    Option         "NoLogo" "true"
    Option         "TripleBuffer" "true"
    Option         "Coolbits" "28"
    Option         "RegistryDwords" "PowerMizerEnable=0x1; PerfLevelSrc=0x2222; PowerMizerDefault=0x3; PowerMizerDefaultAC=0x3"
EndSection

Section "Screen"
    Identifier     "Screen0"
    Device         "NVIDIA Card"
    Option         "metamodes" "nvidia-auto-select +0+0 {ForceFullCompositionPipeline=On}"
    Option         "AllowIndirectGLXProtocol" "off"
EndSection
EOF

# Enable NVIDIA persistence mode
systemctl enable nvidia-persistenced

# Create modprobe configuration
cat > /etc/modprobe.d/nvidia.conf <<EOF
options nvidia NVreg_PreserveVideoMemoryAllocations=1
options nvidia NVreg_TemporaryFilePath=/var/tmp
EOF

# Update initramfs
update-initramfs -u

echo ""
echo "NVIDIA drivers installed successfully!"
echo "Please reboot your system for changes to take effect."
echo ""
echo "After reboot, you can:"
echo "  - Run 'nvidia-smi' to check driver status"
echo "  - Run 'nvidia-settings' to configure GPU settings"
echo "  - Enable overclocking with 'nvidia-settings' (Coolbits enabled)"
