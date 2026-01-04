#!/bin/bash
# MuxOS Complete Hardware Detection System
# Detects all hardware components: WiFi, Bluetooth, Audio, Microphones, Display, CPU, RAM, Storage, USB, Sensors

echo "MuxOS Hardware Detection System"
echo "================================"
echo ""

# Function to print section headers
print_section() {
    echo ""
    echo "=== $1 ==="
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# CPU Detection
print_section "CPU Information"
if command_exists lscpu; then
    echo "✓ CPU detected:"
    lscpu | grep -E "(Model name|CPU\(s\)|Thread|Core|Architecture)" | sed 's/^/  /'
else
    echo "✗ lscpu not available"
fi

# Memory Detection
print_section "Memory Information"
if command_exists free; then
    echo "✓ Memory detected:"
    free -h | sed 's/^/  /'
elif [ -f /proc/meminfo ]; then
    echo "✓ Memory detected (from /proc/meminfo):"
    grep -E "(MemTotal|MemAvailable|SwapTotal)" /proc/meminfo | sed 's/^/  /'
else
    echo "✗ Memory information not available"
fi

# Graphics Card Detection
print_section "Graphics Cards"
if command_exists lspci; then
    echo "✓ Graphics cards detected:"
    lspci | grep -i vga | sed 's/^/  /'
    
    # Check loaded drivers
    echo ""
    echo "  Loaded graphics drivers:"
    lsmod | grep -E "(nvidia|amdgpu|i915|nouveau)" | sed 's/^/    /'
else
    echo "✗ lspci not available"
fi

# Display/Monitor Detection
print_section "Display Information"
if command_exists xrandr; then
    echo "✓ Displays detected:"
    xrandr --query | grep -E "(connected|disconnected)" | sed 's/^/  /'
elif [ -d /sys/class/drm ]; then
    echo "✓ DRM connectors detected:"
    ls /sys/class/drm/ | grep -E "card.*-" | sed 's/^/  /'
else
    echo "✗ Display information not available"
fi

# Audio Devices Detection
print_section "Audio Devices"
if command_exists aplay; then
    echo "✓ Playback devices detected:"
    aplay -l | sed 's/^/  /'
fi

if command_exists arecord; then
    echo ""
    echo "✓ Capture devices (microphones) detected:"
    arecord -l | sed 's/^/  /'
fi

if [ -d /proc/asound ]; then
    echo ""
    echo "✓ ALSA sound cards:"
    cat /proc/asound/cards | sed 's/^/  /'
fi

# Network Interfaces Detection
print_section "Network Interfaces"
if command_exists ip; then
    echo "✓ Network interfaces detected:"
    ip link show | grep -E "^[0-9]" | sed 's/^/  /'
    
    echo ""
    echo "  Wireless interfaces:"
    iw dev 2>/dev/null | grep Interface | sed 's/^/    /'
elif command_exists ifconfig; then
    echo "✓ Network interfaces detected:"
    ifconfig | grep -E "^[a-z]" | cut -d: -f1 | sed 's/^/  /'
else
    echo "✗ Network interface information not available"
fi

# WiFi Detection
print_section "WiFi Information"
if command_exists iwlist; then
    echo "✓ WiFi capabilities detected:"
    iwlist scan 2>/dev/null | head -10 | sed 's/^/  /'
elif command_exists nmcli; then
    echo "✓ WiFi devices (via NetworkManager):"
    nmcli device status | grep wifi | sed 's/^/  /'
elif [ -f /proc/net/wireless ]; then
    echo "✓ Wireless interfaces detected:"
    cat /proc/net/wireless | sed 's/^/  /'
else
    echo "✗ WiFi information not available"
fi

# Bluetooth Detection
print_section "Bluetooth Information"
if command_exists bluetoothctl; then
    echo "✓ Bluetooth service available"
    echo "  Bluetooth devices:"
    bluetoothctl devices 2>/dev/null | sed 's/^/    /' || echo "    No devices paired"
elif command_exists hciconfig; then
    echo "✓ Bluetooth interfaces:"
    hciconfig -a 2>/dev/null | sed 's/^/  /'
elif [ -d /sys/class/bluetooth ]; then
    echo "✓ Bluetooth adapters detected:"
    ls /sys/class/bluetooth/ | sed 's/^/  /'
else
    echo "✗ Bluetooth not available"
fi

# Storage Detection
print_section "Storage Devices"
if command_exists lsblk; then
    echo "✓ Block devices detected:"
    lsblk -o NAME,SIZE,TYPE,MOUNTPOINT | sed 's/^/  /'
elif [ -d /sys/block ]; then
    echo "✓ Block devices detected (from /sys/block):"
    ls /sys/block/ | sed 's/^/  /'
fi

if command_exists df; then
    echo ""
    echo "✓ Mounted filesystems:"
    df -h | sed 's/^/  /'
fi

# USB Devices Detection
print_section "USB Devices"
if command_exists lsusb; then
    echo "✓ USB devices detected:"
    lsusb | sed 's/^/  /'
elif [ -d /sys/bus/usb/devices ]; then
    echo "✓ USB devices detected (from /sys):"
    ls /sys/bus/usb/devices/ | sed 's/^/  /'
else
    echo "✗ USB information not available"
fi

# Input Devices Detection
print_section "Input Devices"
if [ -d /proc/bus/input/devices ]; then
    echo "✓ Input devices detected:"
    grep -E "(Name|Phys)" /proc/bus/input/devices | grep -v "N: Name" | sed 's/^/  /'
elif command_exists xinput; then
    echo "✓ X11 input devices:"
    xinput list | sed 's/^/  /'
else
    echo "✗ Input device information not available"
fi

# Temperature and Sensors
print_section "Temperature Sensors"
if command_exists sensors; then
    echo "✓ Sensor readings:"
    sensors | sed 's/^/  /'
elif [ -d /sys/class/thermal ]; then
    echo "✓ Thermal zones detected:"
    for zone in /sys/class/thermal/thermal_zone*; do
        if [ -f "$zone/temp" ]; then
            temp=$(cat "$zone/temp" 2>/dev/null)
            temp_c=$((temp / 1000))
            echo "  $(basename "$zone"): ${temp_c}°C"
        fi
    done
else
    echo "✗ Temperature sensors not available"
fi

# Battery Information
print_section "Battery Information"
if [ -d /sys/class/power_supply ]; then
    echo "✓ Power supply devices:"
    for supply in /sys/class/power_supply/*; do
        if [ -f "$supply/status" ]; then
            name=$(basename "$supply")
            status=$(cat "$supply/status" 2>/dev/null)
            echo "  $name: $status"
            
            if [ -f "$supply/capacity" ]; then
                capacity=$(cat "$supply/capacity" 2>/dev/null)
                echo "    Capacity: ${capacity}%"
            fi
        fi
    done
else
    echo "✗ Battery information not available"
fi

# PCI Devices Summary
print_section "PCI Devices Summary"
if command_exists lspci; then
    echo "✓ PCI devices by category:"
    echo "  Graphics: $(lspci | grep -ci vga)"
    echo "  Network: $(lspci | grep -ci network)"
    echo "  Audio: $(lspci | grep -ci audio)"
    echo "  USB: $(lspci | grep -ci usb)"
    echo "  Storage: $(lspci | grep -ci sata)"
    echo "  Total PCI devices: $(lspci | wc -l)"
fi

# System Information Summary
print_section "System Summary"
echo "✓ System information:"
if [ -f /etc/os-release ]; then
    echo "  OS: $(grep PRETTY_NAME /etc/os-release | cut -d'"' -f2)"
fi
echo "  Kernel: $(uname -r)"
echo "  Architecture: $(uname -m)"
echo "  Uptime: $(uptime -p 2>/dev/null || uptime)"

if command_exists lsb_release; then
    echo "  Distribution: $(lsb_release -d | cut -f2)"
fi

echo ""
echo "Hardware detection complete!"
echo "================================"
