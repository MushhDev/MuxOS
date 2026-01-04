#!/bin/bash
# MuxOS Bootable USB Creator

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

if [ "$EUID" -ne 0 ]; then
    log_error "This script must be run as root"
    exit 1
fi

if [ $# -ne 2 ]; then
    echo "Usage: $0 <iso-file> <device>"
    echo "Example: $0 muxos-1.0-amd64.iso /dev/sdb"
    echo ""
    echo "Available devices:"
    lsblk -d -o NAME,SIZE,TYPE,MOUNTPOINT | grep disk
    exit 1
fi

ISO_FILE="$1"
DEVICE="$2"

if [ ! -f "$ISO_FILE" ]; then
    log_error "ISO file not found: $ISO_FILE"
    exit 1
fi

if [ ! -b "$DEVICE" ]; then
    log_error "Device not found: $DEVICE"
    exit 1
fi

log_warn "WARNING: This will ERASE ALL DATA on $DEVICE"
log_warn "Device info:"
lsblk "$DEVICE"
echo ""
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    log_info "Aborted."
    exit 0
fi

log_info "Unmounting any mounted partitions..."
umount ${DEVICE}* 2>/dev/null || true

log_info "Writing ISO to $DEVICE..."
dd if="$ISO_FILE" of="$DEVICE" bs=4M status=progress oflag=sync

log_info "Syncing..."
sync

log_info "Bootable USB created successfully!"
log_info "You can now boot from $DEVICE"
