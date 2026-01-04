# MuxOS Installation Guide

This guide will help you install MuxOS on your computer.

## Prerequisites

- USB drive (8GB or larger)
- Computer with x86_64 processor
- At least 10GB free disk space
- Internet connection (for updates and drivers)

## Installation Methods

### Method 1: Create Bootable USB (Recommended)

#### On Linux:

1. Download the MuxOS ISO file
2. Insert your USB drive
3. Identify your USB device:
   ```bash
   lsblk
   ```
4. Create bootable USB (replace `/dev/sdX` with your device):
   ```bash
   sudo dd if=muxos-1.0-amd64.iso of=/dev/sdX bs=4M status=progress oflag=sync
   ```

#### On Windows:

1. Download [Rufus](https://rufus.ie/)
2. Insert your USB drive
3. Open Rufus
4. Select the MuxOS ISO file
5. Select your USB drive
6. Click "START"

### Method 2: Test in Virtual Machine

Before installing on real hardware, you can test MuxOS in a VM:

#### Using VirtualBox:
1. Create new VM (Type: Linux, Version: Debian 64-bit)
2. Allocate at least 2GB RAM and 2 CPU cores
3. Create virtual hard disk (20GB+)
4. Mount MuxOS ISO as optical drive
5. Enable 3D acceleration in Display settings
6. Start VM

#### Using QEMU/KVM:
```bash
qemu-system-x86_64 -enable-kvm -m 4G -smp 4 -cdrom muxos-1.0-amd64.iso -boot d
```

## Booting from USB

1. Insert the bootable USB drive
2. Restart your computer
3. Enter BIOS/UEFI settings (usually F2, F12, DEL, or ESC during boot)
4. Change boot order to boot from USB first
5. Save and exit BIOS
6. Computer will boot into MuxOS

## Live Mode

When you boot from USB, MuxOS runs in "Live Mode":
- Test all features without installing
- All changes are temporary
- Perfect for hardware compatibility testing

### Default Credentials (Live Mode):
- Username: `muxos`
- Password: `muxos`

## Installing to Hard Drive

### Automatic Installation (Recommended):

1. Boot into MuxOS Live Mode
2. Open terminal (Win+Enter)
3. Run installer:
   ```bash
   sudo muxos-installer
   ```
4. Follow the on-screen instructions

### Manual Installation:

1. Boot into MuxOS Live Mode
2. Open GParted or terminal to partition your disk
3. Create partitions:
   - EFI partition (512MB, FAT32) - for UEFI systems
   - Root partition (remaining space, ext4)
   - Optional: Swap partition (2GB)

4. Mount partitions:
   ```bash
   sudo mount /dev/sdXY /mnt
   sudo mkdir -p /mnt/boot/efi
   sudo mount /dev/sdX1 /mnt/boot/efi  # EFI partition
   ```

5. Install base system:
   ```bash
   sudo rsync -av --exclude=/proc --exclude=/sys --exclude=/dev --exclude=/run / /mnt/
   ```

6. Install GRUB:
   ```bash
   sudo grub-install --target=x86_64-efi --efi-directory=/mnt/boot/efi --bootloader-id=MuxOS /dev/sdX
   sudo chroot /mnt update-grub
   ```

7. Reboot:
   ```bash
   sudo reboot
   ```

## Post-Installation Setup

### 1. Update System
```bash
sudo apt update
sudo apt upgrade
```

### 2. Install Graphics Drivers

#### NVIDIA:
```bash
sudo /usr/share/muxos/drivers/install-nvidia.sh
```

#### AMD:
```bash
sudo /usr/share/muxos/drivers/install-amd.sh
```

#### Intel:
Drivers are pre-installed, no action needed.

### 3. Install Gaming Platforms

#### Steam:
```bash
sudo apt install steam
```

#### Lutris:
```bash
sudo apt install lutris
```

### 4. Apply Gaming Optimizations
```bash
sudo /usr/share/muxos/optimizations/gaming-tweaks.sh
```

### 5. Check Hardware Detection
```bash
sudo /usr/share/muxos/drivers/detect-hardware.sh
```

## Troubleshooting

### System won't boot
- Try "Safe Mode" from GRUB menu
- Disable Secure Boot in BIOS
- Check boot order in BIOS

### No display after boot
- Boot in Safe Mode (nomodeset)
- Install proper graphics drivers
- Check monitor connection

### No network connection
- Check if NetworkManager is running: `systemctl status NetworkManager`
- Restart NetworkManager: `sudo systemctl restart NetworkManager`
- Check network settings in Control Panel

### No sound
- Check volume: `alsamixer`
- Restart PulseAudio: `pulseaudio -k && pulseaudio --start`
- Open Volume Control from system tray

### Low performance in games
- Install proper GPU drivers
- Run gaming optimizations script
- Enable GameMode for games
- Check CPU governor: should be "performance"

## Keyboard Shortcuts

- **Win + Enter**: Open Terminal
- **Win + E**: Open File Manager
- **Win + R**: Application Launcher
- **Win + L**: Lock Screen
- **Win + Left/Right**: Snap window to side
- **Alt + F4**: Close window
- **Ctrl + Alt + Left/Right**: Switch desktop

## Getting Help

- Check documentation in `/usr/share/doc/muxos/`
- Run hardware detection: `muxos-detect-hardware`
- Open Control Panel for system settings
- Check logs: `journalctl -xe`

## Uninstallation

To remove MuxOS and restore your previous system:
1. Boot from another OS or live USB
2. Delete MuxOS partitions using GParted
3. Reinstall bootloader for your other OS
4. Resize remaining partitions as needed
