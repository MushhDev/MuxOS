# Building MuxOS

This guide explains how to build a bootable MuxOS ISO from source.

## Prerequisites

You need a Linux system (Ubuntu/Debian recommended) with:

```bash
sudo apt update
sudo apt install -y \
    debootstrap \
    squashfs-tools \
    xorriso \
    grub-pc-bin \
    grub-efi-amd64-bin \
    mtools \
    git \
    build-essential \
    wget \
    curl \
    dos2unix
```

## Build Process

1. **Clone the repository**:
```bash
git clone <repository-url>
cd MuxOS
```

2. **Run the build script**:
```bash
chmod +x scripts/build-iso.sh

sudo ./scripts/build-iso.sh
```

3. **Find your ISO**:
The ISO will be created in `build/muxos.iso`

## Build Steps Explained

The build process:
1. Creates a minimal Debian/Ubuntu base system
2. Installs custom kernel and drivers
3. Configures the desktop environment
4. Installs default applications
5. Applies gaming optimizations
6. Generates bootable ISO with GRUB

## Customization

Edit `config/muxos.conf` to customize:
- Default packages
- Desktop theme
- System settings
- Performance tweaks

## Troubleshooting

**Build fails**: Ensure you have enough disk space (20GB+) and are running as root/sudo

**Missing dependencies**: Run the prerequisites installation command again

**ISO won't boot**: Verify BIOS/UEFI settings and secure boot configuration


