# Gaming on MuxOS

MuxOS is optimized for gaming performance. This guide covers everything you need to know.

## Pre-configured Optimizations

MuxOS includes these gaming optimizations out of the box:

### Kernel Optimizations
- **1000 Hz timer frequency** for lower latency
- **PREEMPT kernel** for better responsiveness
- **Transparent Huge Pages** enabled
- **ZRAM** for efficient memory compression
- **Low swappiness** (10) to prefer RAM over swap

### System Optimizations
- **Performance CPU governor** by default
- **Optimized I/O schedulers** (mq-deadline for HDD, none for NVMe)
- **Disabled CPU mitigations** for maximum performance
- **Increased file descriptor limits** for Wine/Proton
- **Esync/Fsync support** enabled

### Graphics Optimizations
- **VSync** configurable per-application
- **Compositor** optimized for gaming (auto-disables for fullscreen)
- **GPU performance profiles** set to maximum
- **Vulkan** support included

## Installing Games

### Steam

Steam is pre-configured for optimal performance:

```bash
# Install Steam (if not already installed)
sudo apt install steam

# Launch Steam
steam
```

**Proton Configuration:**
1. Open Steam
2. Go to Settings → Steam Play
3. Enable "Enable Steam Play for all other titles"
4. Select latest Proton version

### Lutris

Lutris manages games from multiple sources:

```bash
# Install Lutris
sudo apt install lutris

# Launch Lutris
lutris
```

**Recommended Lutris Settings:**
- Enable Esync
- Enable Fsync
- Enable DXVK
- Enable GameMode

### Native Linux Games

Many games run natively on Linux:
- Download from Steam, GOG, or itch.io
- Install and play directly
- No compatibility layer needed

### Wine/Proton Games

For Windows games not on Steam:

```bash
# Wine is pre-installed
wine --version

# Install Winetricks for dependencies
winetricks
```

## Performance Tools

### GameMode

GameMode automatically optimizes your system when gaming:

```bash
# Check if GameMode is running
systemctl status gamemode

# Launch a game with GameMode
gamemoderun ./game

# For Steam games, add to launch options:
gamemoderun %command%
```

### MangoHud

Display performance overlay in games:

```bash
# MangoHud is pre-installed
# For Steam games, add to launch options:
mangohud %command%

# For other games:
mangohud ./game

# Configure MangoHud
mkdir -p ~/.config/MangoHud
nano ~/.config/MangoHud/MangoHud.conf
```

**Recommended MangoHud config:**
```ini
fps
frame_timing
gpu_stats
cpu_stats
ram
vulkan_driver
engine_version
position=top-left
```

### Performance Monitoring

Monitor system performance:

```bash
# MuxOS System Monitor
muxos-monitor

# Terminal monitoring
htop

# GPU monitoring (NVIDIA)
nvidia-smi

# GPU monitoring (AMD)
radeontop
```

## Graphics Drivers

### NVIDIA

For best gaming performance on NVIDIA:

```bash
# Install proprietary drivers
sudo /usr/share/muxos/drivers/install-nvidia.sh

# Reboot after installation
sudo reboot

# Verify installation
nvidia-smi

# Configure settings
nvidia-settings
```

**NVIDIA Settings for Gaming:**
- Power Management: Prefer Maximum Performance
- Texture Filtering: High Performance
- Threaded Optimization: On
- Vertical Sync: Off (or Application-controlled)

### AMD

AMD drivers are pre-installed (Mesa):

```bash
# Verify installation
vulkaninfo | grep "deviceName"

# Monitor GPU
radeontop

# Check performance level
cat /sys/class/drm/card0/device/power_dpm_force_performance_level
```

### Intel

Intel drivers are pre-installed and optimized.

## Optimizing Specific Games

### Counter-Strike 2 / CS:GO

Launch options:
```
gamemoderun mangohud %command% -high -threads 4 +fps_max 0 -novid -nojoy
```

### Dota 2

Launch options:
```
gamemoderun mangohud %command% -vulkan -high
```

### Cyberpunk 2077

Proton version: Proton Experimental
Launch options:
```
gamemoderun mangohud %command%
```

### Elden Ring

Proton version: Proton GE (install via ProtonUp-Qt)
Launch options:
```
gamemoderun mangohud %command%
```

## Troubleshooting

### Low FPS

1. **Check GPU drivers:**
   ```bash
   sudo /usr/share/muxos/drivers/detect-hardware.sh
   ```

2. **Verify CPU governor:**
   ```bash
   cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
   # Should show "performance"
   ```

3. **Apply gaming tweaks:**
   ```bash
   sudo /usr/share/muxos/optimizations/gaming-tweaks.sh
   ```

4. **Disable compositor for fullscreen games:**
   - Edit `~/.config/picom/picom.conf`
   - Set `unredir-if-possible = true;`

### Game won't start

1. **Check Proton version:** Try different Proton versions
2. **Install dependencies:** Use Winetricks or Protontricks
3. **Check logs:** `~/.steam/steam/logs/`
4. **Verify game files:** In Steam, right-click game → Properties → Verify Integrity

### Stuttering

1. **Enable Esync/Fsync:**
   ```bash
   # Check limits
   ulimit -Hn
   # Should be 1048576 or higher
   ```

2. **Disable compositor:**
   ```bash
   killall picom
   ```

3. **Check for background processes:**
   ```bash
   htop
   ```

### Input lag

1. **Reduce mouse polling rate** if too high (1000Hz recommended)
2. **Disable VSync** in game settings
3. **Use performance CPU governor**
4. **Disable compositor**

### Audio issues

1. **Check PulseAudio:**
   ```bash
   pulseaudio --check
   pulseaudio -k && pulseaudio --start
   ```

2. **Adjust latency:**
   Edit `/etc/pulse/daemon.conf`:
   ```
   default-fragments = 2
   default-fragment-size-msec = 5
   ```

## Advanced Tweaks

### Custom Kernel Parameters

Edit `/etc/default/grub` and add to `GRUB_CMDLINE_LINUX_DEFAULT`:

```
mitigations=off processor.max_cstate=1 intel_idle.max_cstate=0
```

Then update GRUB:
```bash
sudo update-grub
sudo reboot
```

### CPU Affinity

Pin game to specific CPU cores:

```bash
taskset -c 0-7 ./game
```

### Process Priority

Run game with higher priority:

```bash
nice -n -10 ./game
```

### Overclocking

**NVIDIA:**
```bash
# Enable overclocking (Coolbits already enabled)
nvidia-settings
# Go to PowerMizer section
```

**AMD:**
```bash
# Install CoreCtrl
sudo apt install corectrl
corectrl
```

## Performance Benchmarks

Test your system performance:

```bash
# Unigine Heaven
# Download from unigine.com

# glxgears (basic test)
glxgears

# Vulkan test
vkcube
```

## Recommended Settings by Game Type

### Competitive FPS (CS:GO, Valorant, etc.)
- Disable VSync
- Lowest graphics settings
- Maximum FPS
- Disable compositor
- Use GameMode

### AAA Single-Player (Cyberpunk, Witcher, etc.)
- Enable VSync or FreeSync/G-Sync
- Balance graphics and performance
- Use MangoHud to monitor
- Enable GameMode

### Strategy/Simulation
- Standard settings
- VSync on
- Compositor can stay enabled

## Resources

- **ProtonDB**: Check game compatibility - protondb.com
- **Lutris**: Game installers - lutris.net
- **Wine HQ**: Windows app compatibility - winehq.org
- **MangoHud**: Performance overlay - github.com/flightlessmango/MangoHud
