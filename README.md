# MuxOS

**A lightweight, gaming-optimized Linux distribution**

MuxOS is a pure Linux distribution built for gamers and power users. Minimal footprint, maximum performance, stunning visuals.

## ✨ Features

- 🎮 **Gaming Optimized**: Pre-configured GameMode, MangoHud, Wine/Proton ready
- 💨 **Ultra Lightweight**: Only ~300-400 MB RAM at idle
- 🖥️ **Modern Desktop**: Sleek Openbox-based desktop with blur effects and animations
- 🔧 **Control Center**: Unified system configuration with Work/Gaming profiles
- 📦 **Ready to Use**: Essential applications pre-installed and configured
- 🔌 **Hardware Support**: Auto-detection for NVIDIA, AMD, Intel GPUs
- ⚡ **Performance Tuned**: Optimized kernel (1000Hz, PREEMPT), ZRAM, CPU governors
- 🔒 **Secure by Default**: UFW firewall, Fail2ban, AppArmor enabled
- 🔄 **Rolling Updates**: GitHub-based update system with notifications

## 🖥️ Included Applications

### System Tools
- **Control Center** - Unified system settings and configuration
- **Task Manager** - Process monitoring and system management
- **Disk Manager** - Storage, cleanup, backup tools
- **Security Center** - Firewall, antivirus, privacy
- **Update Center** - GitHub-based update system
- **System Monitor** - Real-time performance monitoring

### Gaming
- **Game Center** - Gaming hub with optimizations
- Steam, Lutris, Wine pre-configured
- GameMode & MangoHud included
- GPU driver installers (NVIDIA/AMD)

### Productivity
- **Notes** - Simple note-taking app
- **Calculator** - Scientific calculator
- **Screenshot** - Screen capture tool
- Firefox, File Manager, Terminal, Text Editor

## 📊 System Requirements

| | Minimum | Recommended |
|---|---------|-------------|
| **RAM** | 512 MB | 4 GB+ |
| **Storage** | 10 GB | 50 GB SSD |
| **CPU** | x86_64 | Quad-core |
| **GPU** | OpenGL 3.0+ | GTX 1060 / RX 580+ |

## 🚀 Quick Start

```bash
# 1. Build ISO (on Linux)
sudo ./scripts/build-iso-v2.sh

# 2. Create bootable USB
sudo dd if=build/muxos-1.0-amd64.iso of=/dev/sdX bs=4M status=progress

# 3. Boot and enjoy!
```

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Win + Enter` | Terminal |
| `Win + E` | File Manager |
| `Win + R` | App Launcher |
| `Win + L` | Lock Screen |
| `Win + Left/Right` | Snap Window |
| `Alt + F4` | Close Window |

## 📚 Documentation

- [Installation Guide](docs/INSTALL.md)
- [Gaming Guide](docs/GAMING.md)
- [Build Guide](docs/BUILD.md)
- [FAQ](docs/FAQ.md)

## 🔒 Security Features

- UFW Firewall (pre-configured)
- Fail2ban intrusion prevention
- Rootkit detection (rkhunter, chkrootkit)
- System hardening scripts
- Privacy tools and DNS encryption

## 📁 Project Structure

```
MuxOS/
├── apps/           # Custom applications
│   ├── control-panel/
│   ├── gaming/
│   ├── security/
│   ├── storage/
│   ├── updater/
│   └── utilities/
├── boot/           # GRUB configuration
├── config/         # System configuration
├── desktop/        # Desktop environment
├── docs/           # Documentation
├── scripts/        # Build scripts
└── system/         # System components
    ├── drivers/
    ├── optimizations/
    ├── security/
    └── services/
```

## 📜 License

MuxOS is built on open-source components under MIT/GPL licenses.
