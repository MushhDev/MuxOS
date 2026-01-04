#!/bin/bash
# Hardware Detection and Driver Installation Script

echo "MuxOS Hardware Detection"
echo "========================"
echo ""

# Detect GPU
echo "Graphics Card:"
if lspci | grep -i nvidia > /dev/null; then
    echo "  ✓ NVIDIA GPU detected"
    lspci | grep -i nvidia | grep -i vga
    echo "  Run: sudo /usr/share/muxos/drivers/install-nvidia.sh"
elif lspci | grep -i amd | grep -i vga > /dev/null; then
    echo "  ✓ AMD GPU detected"
    lspci | grep -i amd | grep -i vga
    echo "  Run: sudo /usr/share/muxos/drivers/install-amd.sh"
elif lspci | grep -i intel | grep -i vga > /dev/null; then
    echo "  ✓ Intel GPU detected (drivers included)"
    lspci | grep -i intel | grep -i vga
else
    echo "  ✗ No supported GPU detected"
fi

echo ""

# Detect Network Card
echo "Network Card:"
if lspci | grep -i network > /dev/null; then
    echo "  ✓ Network card detected"
    lspci | grep -i network
else
    echo "  ✗ No network card detected"
fi

echo ""

# Detect Audio
echo "Audio Device:"
if lspci | grep -i audio > /dev/null; then
    echo "  ✓ Audio device detected"
    lspci | grep -i audio
else
    echo "  ✗ No audio device detected"
fi

echo ""

# Detect USB Controllers
echo "USB Controllers:"
if lspci | grep -i usb > /dev/null; then
    echo "  ✓ USB controllers detected"
    lspci | grep -i usb | head -3
else
    echo "  ✗ No USB controllers detected"
fi

echo ""

# Check loaded kernel modules
echo "Loaded Graphics Drivers:"
if lsmod | grep -i nvidia > /dev/null; then
    echo "  ✓ NVIDIA driver loaded"
fi
if lsmod | grep -i amdgpu > /dev/null; then
    echo "  ✓ AMDGPU driver loaded"
fi
if lsmod | grep -i i915 > /dev/null; then
    echo "  ✓ Intel i915 driver loaded"
fi
if lsmod | grep -i nouveau > /dev/null; then
    echo "  ⚠ Nouveau (open-source NVIDIA) driver loaded"
    echo "    Consider installing proprietary NVIDIA drivers for better gaming performance"
fi

echo ""
echo "Hardware detection complete!"
