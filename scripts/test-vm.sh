#!/bin/bash
# Test MuxOS in QEMU/KVM

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ISO_FILE="$PROJECT_ROOT/build/muxos-1.0-amd64.iso"

if [ ! -f "$ISO_FILE" ]; then
    echo "Error: ISO file not found at $ISO_FILE"
    echo "Please run build-iso.sh first"
    exit 1
fi

echo "Testing MuxOS in QEMU..."
echo "ISO: $ISO_FILE"
echo ""

# Check if KVM is available
if [ -e /dev/kvm ]; then
    KVM_OPTS="-enable-kvm -cpu host"
    echo "KVM acceleration: enabled"
else
    KVM_OPTS=""
    echo "KVM acceleration: disabled (slower)"
fi

qemu-system-x86_64 \
    $KVM_OPTS \
    -m 4G \
    -smp 4 \
    -cdrom "$ISO_FILE" \
    -boot d \
    -vga virtio \
    -display sdl,gl=on \
    -device virtio-net-pci,netdev=net0 \
    -netdev user,id=net0 \
    -device intel-hda \
    -device hda-duplex \
    -usb \
    -device usb-tablet
