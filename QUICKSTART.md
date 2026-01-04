# MuxOS Quick Start Guide

Get MuxOS up and running in minutes!

## 🚀 For Users

### 1. Download MuxOS
Download the latest ISO from the releases page.

### 2. Create Bootable USB

**Windows:**
- Download [Rufus](https://rufus.ie/)
- Select MuxOS ISO
- Click START

**Linux:**
```bash
sudo dd if=muxos-1.0-amd64.iso of=/dev/sdX bs=4M status=progress
```

### 3. Boot and Install
1. Boot from USB
2. Test in Live Mode (optional)
3. Run installer when ready
4. Reboot and enjoy!

**Default credentials (Live Mode):**
- Username: `muxos`
- Password: `muxos`

### 4. Post-Installation

**Install GPU drivers:**
```bash
# NVIDIA
sudo /usr/share/muxos/drivers/install-nvidia.sh

# AMD (already installed)
sudo /usr/share/muxos/drivers/install-amd.sh
```

**Install Steam:**
```bash
sudo apt install steam
```

**Apply gaming optimizations:**
```bash
sudo /usr/share/muxos/optimizations/gaming-tweaks.sh
```

## 🛠️ For Developers

### Build MuxOS from Source

**Prerequisites (Ubuntu/Debian):**
```bash
sudo apt install -y \
    debootstrap \
    squashfs-tools \
    xorriso \
    grub-pc-bin \
    grub-efi-amd64-bin \
    mtools \
    git \
    build-essential
```

**Build ISO:**
```bash
git clone <repository-url>
cd MuxOS
sudo ./scripts/build-iso.sh
```

**Test in VM:**
```bash
./scripts/test-vm.sh
```

**Create Bootable USB:**
```bash
sudo ./scripts/create-bootable-usb.sh build/muxos-1.0-amd64.iso /dev/sdX
```

## 📋 Key Features

- ✅ **Low RAM Usage**: ~300-400 MB at idle
- ✅ **Gaming Optimized**: Pre-configured for maximum performance
- ✅ **Hardware Support**: Auto-detection and driver installation
- ✅ **Steam & Proton**: Pre-installed and configured
- ✅ **Control Panel**: Easy system configuration
- ✅ **Modern Desktop**: Lightweight but beautiful interface

## ⌨️ Essential Shortcuts

- **Win + Enter**: Terminal
- **Win + E**: File Manager
- **Win + R**: App Launcher
- **Win + L**: Lock Screen
- **Win + Left/Right**: Snap windows
- **Alt + F4**: Close window

## 🎮 Gaming Tips

1. **Enable GameMode for games:**
   ```bash
   gamemoderun ./game
   ```

2. **Use MangoHud for FPS overlay:**
   ```bash
   mangohud ./game
   ```

3. **For Steam games, add to launch options:**
   ```
   gamemoderun mangohud %command%
   ```

## 📚 Documentation

- **Installation Guide**: `docs/INSTALL.md`
- **Gaming Guide**: `docs/GAMING.md`
- **Build Guide**: `docs/BUILD.md`
- **FAQ**: `docs/FAQ.md`

## 🆘 Need Help?

**Check hardware:**
```bash
sudo /usr/share/muxos/drivers/detect-hardware.sh
```

**View logs:**
```bash
journalctl -xe
```

**Open Control Panel:**
```bash
muxos-control-panel
```

## 🌟 What's Included

### Desktop Environment
- Openbox (window manager)
- Picom (compositor)
- Tint2 (panel)
- LightDM (display manager)

### Applications
- Firefox (web browser)
- PCManFM (file manager)
- XFCE Terminal
- Mousepad (text editor)
- MPV (media player)
- Control Panel
- System Monitor

### Gaming Tools
- Steam
- Wine & Winetricks
- GameMode
- MangoHud
- Vulkan support
- Proton compatibility

### System Tools
- Network Manager
- PulseAudio
- Driver installers
- Gaming optimizations
- Hardware detection

## 🔧 Customization

**Change theme:**
```bash
sudo apt install lxappearance
lxappearance
```

**Change wallpaper:**
```bash
feh --bg-scale /path/to/image.jpg
```

**Edit keyboard shortcuts:**
```bash
nano ~/.config/openbox/rc.xml
openbox --reconfigure
```

## 📊 System Requirements

**Minimum:**
- CPU: x86_64 processor
- RAM: 512 MB
- Storage: 10 GB
- GPU: OpenGL 3.0+

**Recommended:**
- CPU: Quad-core
- RAM: 4 GB+
- Storage: 50 GB SSD
- GPU: GTX 1060 / RX 580+

---

**Ready to game? Boot MuxOS and enjoy! 🎮**
