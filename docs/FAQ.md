# MuxOS Frequently Asked Questions

## General Questions

### What is MuxOS?

MuxOS is a lightweight, gaming-optimized Linux distribution based on Debian. It combines the stability of Linux with optimizations specifically designed for gaming performance and low RAM usage.

### Is MuxOS free?

Yes, MuxOS is completely free and open-source.

### What are the system requirements?

**Minimum:**
- CPU: x86_64 compatible processor
- RAM: 512 MB
- Storage: 10 GB
- GPU: Any with OpenGL 3.0+ support

**Recommended:**
- CPU: Quad-core processor
- RAM: 4 GB or more
- Storage: 50 GB SSD
- GPU: NVIDIA GTX 1060 / AMD RX 580 or better

### How much RAM does MuxOS use?

MuxOS uses approximately 300-400 MB of RAM at idle with the desktop environment running, making it one of the most memory-efficient gaming-focused distributions.

### Can I dual-boot with Windows?

Yes! MuxOS can be installed alongside Windows or any other operating system. The installer will detect existing systems and configure dual-boot automatically.

## Installation Questions

### How do I create a bootable USB?

**On Linux:**
```bash
sudo dd if=muxos-1.0-amd64.iso of=/dev/sdX bs=4M status=progress
```

**On Windows:**
Use Rufus or Etcher to write the ISO to USB.

### Do I need to disable Secure Boot?

For best compatibility, yes. However, MuxOS may work with Secure Boot enabled on some systems.

### Can I install MuxOS on an external drive?

Yes, you can install MuxOS on an external USB drive or external SSD/HDD.

### Will installation delete my files?

Only if you choose to format the entire disk. You can install MuxOS on a separate partition to keep your existing files.

## Gaming Questions

### Can I play Windows games on MuxOS?

Yes! MuxOS includes Wine and Proton for running Windows games. Steam's Proton makes most Windows games work seamlessly.

### Does MuxOS support Steam?

Yes, Steam is included and pre-configured for optimal performance.

### What about anti-cheat games?

Some anti-cheat systems (EAC, BattlEye) now support Linux. Check ProtonDB for specific game compatibility.

### How do I install Epic Games / GOG games?

Use Lutris, which provides installers for Epic Games Store, GOG, and many other platforms.

### Will games run faster on MuxOS than Windows?

Performance is typically comparable, sometimes better due to lower system overhead. Results vary by game and hardware.

### Can I use my gaming peripherals?

Most gaming mice, keyboards, and controllers work out of the box. RGB control may require additional software like OpenRGB.

## Hardware Questions

### Does MuxOS support NVIDIA GPUs?

Yes, with proprietary drivers available via:
```bash
sudo /usr/share/muxos/drivers/install-nvidia.sh
```

### Does MuxOS support AMD GPUs?

Yes, AMD drivers (Mesa) are pre-installed and optimized.

### What about Intel integrated graphics?

Intel graphics drivers are pre-installed and work out of the box.

### Will my Wi-Fi work?

Most Wi-Fi adapters work automatically. Some may require additional firmware from the non-free repository.

### Does MuxOS support VR?

Yes, SteamVR is supported. Install Steam and SteamVR, then connect your headset.

## Performance Questions

### How do I maximize gaming performance?

1. Install proper GPU drivers
2. Run gaming optimization script
3. Use GameMode for games
4. Set CPU governor to performance
5. Disable compositor for fullscreen games

### Why is my system using swap?

Even with plenty of RAM, Linux may use swap for inactive processes. This is normal and doesn't impact performance.

### How do I reduce input lag?

1. Disable VSync in games
2. Use performance CPU governor
3. Disable compositor
4. Reduce mouse polling rate if too high

### Can I overclock on MuxOS?

Yes, overclocking tools are available:
- NVIDIA: nvidia-settings (Coolbits enabled)
- AMD: CoreCtrl
- CPU: Use BIOS/UEFI settings

## Software Questions

### Can I install other Linux software?

Yes! MuxOS is based on Debian, so you can install any Debian/Ubuntu compatible software using apt.

### How do I update MuxOS?

```bash
sudo apt update
sudo apt upgrade
```

### Can I change the desktop environment?

Yes, you can install other desktop environments (KDE, GNOME, XFCE) though Openbox is optimized for gaming.

### Where do I find more applications?

Use the package manager:
```bash
sudo apt search <application-name>
sudo apt install <application-name>
```

## Troubleshooting Questions

### My game won't start

1. Check ProtonDB for compatibility
2. Try different Proton versions
3. Install missing dependencies with Winetricks
4. Check game logs in `~/.steam/steam/logs/`

### No sound in games

1. Check PulseAudio: `pulseaudio --check`
2. Restart audio: `pulseaudio -k && pulseaudio --start`
3. Check volume: `alsamixer`

### Screen tearing

1. Enable VSync in game settings
2. Enable compositor: `picom &`
3. For NVIDIA, enable ForceFullCompositionPipeline

### System freezes during gaming

1. Check temperatures: `sensors`
2. Update GPU drivers
3. Increase swap size
4. Check system logs: `journalctl -xe`

## Customization Questions

### How do I change the theme?

Use LXAppearance:
```bash
sudo apt install lxappearance
lxappearance
```

### Can I change keyboard shortcuts?

Edit `~/.config/openbox/rc.xml` and reload Openbox.

### How do I change the wallpaper?

Right-click desktop → Set Wallpaper, or use:
```bash
feh --bg-scale /path/to/image.jpg
```

### Can I customize the panel?

Edit `~/.config/tint2/tint2rc` and restart tint2.

## Support Questions

### Where can I get help?

- Check documentation in `/usr/share/doc/muxos/`
- Run hardware detection: `muxos-detect-hardware`
- Check system logs: `journalctl -xe`
- Search online Linux gaming communities

### How do I report a bug?

Document the issue with:
1. System information: `neofetch`
2. Hardware info: `lspci`
3. Relevant logs: `journalctl -xe`
4. Steps to reproduce

### Can I contribute to MuxOS?

Yes! MuxOS is open-source. Contributions are welcome.

### Is there a community forum?

Check the project repository for community links and discussion forums.

## Comparison Questions

### MuxOS vs Ubuntu?

MuxOS is lighter, gaming-focused, and uses less RAM. Ubuntu is more general-purpose with more pre-installed software.

### MuxOS vs Pop!_OS?

Both are gaming-focused. MuxOS is lighter and more minimal. Pop!_OS has more features and polish.

### MuxOS vs Windows for gaming?

- **MuxOS Pros:** Free, lighter, more private, better performance on older hardware
- **Windows Pros:** Better anti-cheat support, more native games, easier for beginners

### MuxOS vs Arch Linux?

MuxOS is easier to install and maintain. Arch is more customizable but requires more technical knowledge.

## Advanced Questions

### Can I build MuxOS from source?

Yes! See `docs/BUILD.md` for instructions.

### How do I customize the kernel?

Edit `system/kernel/config-gaming` and rebuild the kernel.

### Can I create my own MuxOS variant?

Yes, MuxOS is open-source. Fork the project and customize as needed.

### Does MuxOS support Wayland?

Currently MuxOS uses X11 for better gaming compatibility. Wayland support may be added in future versions.
