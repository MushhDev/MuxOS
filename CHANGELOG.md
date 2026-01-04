# Changelog

All notable changes to MuxOS will be documented in this file.

## [1.0.0] - 2026-01-04

### Initial Release - "Velocity"

#### Features
- **Base System**
  - Debian Bookworm base
  - Custom optimized kernel (6.6)
  - Lightweight init system
  - ZRAM support for memory optimization
  - Low swappiness configuration (10)

- **Desktop Environment**
  - Openbox window manager
  - Picom compositor with gaming optimizations
  - Tint2 panel
  - LightDM display manager
  - Custom MuxOS theme

- **Gaming Optimizations**
  - Performance CPU governor
  - 1000 Hz kernel timer
  - PREEMPT kernel configuration
  - Optimized I/O schedulers
  - GameMode integration
  - MangoHud support
  - Esync/Fsync enabled
  - Disabled CPU mitigations for performance

- **Graphics Support**
  - NVIDIA driver installer
  - AMD Mesa drivers (pre-installed)
  - Intel drivers (pre-installed)
  - Vulkan support
  - Auto-detection script

- **Pre-installed Applications**
  - Firefox ESR
  - PCManFM file manager
  - XFCE Terminal
  - Mousepad text editor
  - GPicView image viewer
  - MPV media player
  - Steam (installer)
  - Wine & Winetricks
  - MuxOS Control Panel
  - MuxOS System Monitor

- **System Tools**
  - Network Manager with GUI
  - PulseAudio with low latency config
  - Hardware detection tool
  - Driver installation scripts
  - Gaming optimization script
  - ISO build system

- **Documentation**
  - Installation guide
  - Gaming guide
  - Build guide
  - FAQ
  - Quick start guide

#### Performance
- Idle RAM usage: ~300-400 MB
- Boot time: <30 seconds (SSD)
- Minimal background processes
- Optimized for gaming workloads

#### Known Issues
- Some anti-cheat systems may not work (EAC, BattlEye)
- RGB peripheral control requires additional software
- Wayland not supported (X11 only)

#### System Requirements
- **Minimum**: 512 MB RAM, 10 GB storage
- **Recommended**: 4 GB RAM, 50 GB SSD

---

## Future Releases

### Planned for 1.1.0
- [ ] Graphical installer
- [ ] Additional themes
- [ ] More pre-installed games
- [ ] Improved hardware detection
- [ ] Automatic driver updates
- [ ] Custom kernel 6.7+
- [ ] Performance monitoring dashboard
- [ ] One-click game optimization

### Planned for 2.0.0
- [ ] Wayland support (optional)
- [ ] Custom package manager GUI
- [ ] Cloud save synchronization
- [ ] Game library manager
- [ ] Overclocking utilities
- [ ] RGB control integration
- [ ] Custom kernel scheduler
- [ ] Advanced power management

---

**Note**: Version numbers follow [Semantic Versioning](https://semver.org/).
