#!/bin/bash
# MuxOS Gaming Optimizations Script

set -e

echo "Applying MuxOS gaming optimizations..."

# CPU Governor - Performance mode
echo "Setting CPU governor to performance..."
for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    if [ -f "$cpu" ]; then
        echo performance > "$cpu"
    fi
done

# Disable CPU frequency scaling for consistent performance
for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_max_freq; do
    if [ -f "$cpu" ]; then
        cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq > "$cpu" 2>/dev/null || true
    fi
done

# I/O Scheduler optimization for SSDs
echo "Optimizing I/O schedulers..."
for disk in /sys/block/sd*/queue/scheduler; do
    if [ -f "$disk" ]; then
        echo mq-deadline > "$disk" 2>/dev/null || echo kyber > "$disk" 2>/dev/null || true
    fi
done

for disk in /sys/block/nvme*/queue/scheduler; do
    if [ -f "$disk" ]; then
        echo none > "$disk" 2>/dev/null || true
    fi
done

# Kernel parameters for gaming
echo "Applying kernel parameters..."

# VM tweaks for gaming
sysctl -w vm.swappiness=10
sysctl -w vm.vfs_cache_pressure=50
sysctl -w vm.dirty_ratio=10
sysctl -w vm.dirty_background_ratio=5

# Network optimizations
sysctl -w net.core.netdev_max_backlog=16384
sysctl -w net.core.somaxconn=8192
sysctl -w net.ipv4.tcp_fastopen=3
sysctl -w net.ipv4.tcp_mtu_probing=1

# Increase file descriptor limits
sysctl -w fs.file-max=2097152

# Disable transparent huge pages defrag (can cause stuttering)
echo madvise > /sys/kernel/mm/transparent_hugepage/defrag

# GPU optimizations
echo "Applying GPU optimizations..."

# NVIDIA specific
if lspci | grep -i nvidia > /dev/null; then
    echo "NVIDIA GPU detected"
    # Set power management to prefer maximum performance
    if command -v nvidia-smi &> /dev/null; then
        nvidia-smi -pm 1
        nvidia-smi -pl 0  # Remove power limit
    fi
fi

# AMD specific
if lspci | grep -i amd | grep -i vga > /dev/null; then
    echo "AMD GPU detected"
    # Set power profile to high performance
    for card in /sys/class/drm/card*/device/power_dpm_force_performance_level; do
        if [ -f "$card" ]; then
            echo high > "$card" 2>/dev/null || true
        fi
    done
fi

# Audio latency optimization
echo "Optimizing audio..."
if command -v pulseaudio &> /dev/null; then
    # Set PulseAudio for low latency
    sed -i 's/; default-fragments = .*/default-fragments = 2/' /etc/pulse/daemon.conf 2>/dev/null || true
    sed -i 's/; default-fragment-size-msec = .*/default-fragment-size-msec = 5/' /etc/pulse/daemon.conf 2>/dev/null || true
fi

# Process priority optimization
echo "Setting up process priorities..."

# Real-time priority for audio
if command -v rtkit-daemon &> /dev/null; then
    systemctl enable rtkit-daemon 2>/dev/null || true
fi

# GameMode configuration
if [ -f /usr/share/gamemode/gamemode.ini ]; then
    cat > /etc/gamemode.ini <<EOF
[general]
renice=10
ioprio=0
inhibit_screensaver=1

[gpu]
apply_gpu_optimisations=accept_responsibility
gpu_device=0

[custom]
start=notify-send "GameMode started"
end=notify-send "GameMode ended"
EOF
fi

# Wine/Proton optimizations
echo "Configuring Wine/Proton..."
mkdir -p /etc/sysctl.d/
cat > /etc/sysctl.d/99-gaming.conf <<EOF
# Gaming optimizations
vm.max_map_count=2147483642
fs.file-max=2097152
kernel.sched_autogroup_enabled=0
EOF

sysctl -p /etc/sysctl.d/99-gaming.conf

# Esync/Fsync limits
cat > /etc/security/limits.d/99-gaming.conf <<EOF
*               soft    nofile          1048576
*               hard    nofile          1048576
EOF

# Disable unnecessary services for gaming
echo "Disabling unnecessary services..."
SERVICES_TO_DISABLE=(
    "bluetooth.service"
    "cups.service"
    "avahi-daemon.service"
)

for service in "${SERVICES_TO_DISABLE[@]}"; do
    systemctl disable "$service" 2>/dev/null || true
done

# Enable important gaming services
SERVICES_TO_ENABLE=(
    "gamemode.service"
)

for service in "${SERVICES_TO_ENABLE[@]}"; do
    systemctl enable "$service" 2>/dev/null || true
done

echo "Gaming optimizations applied successfully!"
echo "Reboot recommended for all changes to take effect."
