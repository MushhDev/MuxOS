#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Pango
import subprocess
import re
import os
import threading

class HardwareDetector(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="MuxOS Hardware Detector")
        self.set_default_size(900, 700)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        # Create header bar
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = "Hardware Detector"
        
        # Add refresh button
        refresh_btn = Gtk.Button.new_from_icon_name("view-refresh", Gtk.IconSize.BUTTON)
        refresh_btn.connect("clicked", self.on_refresh_clicked)
        refresh_btn.set_tooltip_text("Refresh hardware information")
        header.pack_end(refresh_btn)
        
        self.set_titlebar(header)
        
        # Create main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_top(10)
        main_box.set_margin_bottom(10)
        main_box.set_margin_start(10)
        main_box.set_margin_end(10)
        self.add(main_box)
        
        # Create notebook for tabs
        self.notebook = Gtk.Notebook()
        main_box.pack_start(self.notebook, True, True, 0)
        
        # Create tabs
        self.create_system_tab()
        self.create_cpu_tab()
        self.create_memory_tab()
        self.create_graphics_tab()
        self.create_audio_tab()
        self.create_network_tab()
        self.create_storage_tab()
        self.create_usb_tab()
        self.create_sensors_tab()
        
        # Status bar
        self.status_label = Gtk.Label(label="Ready")
        self.status_label.set_halign(Gtk.Align.START)
        main_box.pack_start(self.status_label, False, False, 5)
        
        # Initial detection
        self.detect_all_hardware()
    
    def create_system_tab(self):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        self.system_info = Gtk.Label(label="Detecting system information...")
        self.system_info.set_xalign(0)
        self.system_info.set_yalign(0)
        self.system_info.set_selectable(True)
        self.system_info.set_line_wrap(True)
        box.pack_start(self.system_info, True, True, 0)
        
        scrolled.add(box)
        self.notebook.append_page(scrolled, Gtk.Label(label="System"))
    
    def create_cpu_tab(self):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        self.cpu_info = Gtk.Label(label="Detecting CPU information...")
        self.cpu_info.set_xalign(0)
        self.cpu_info.set_yalign(0)
        self.cpu_info.set_selectable(True)
        box.pack_start(self.cpu_info, True, True, 0)
        
        scrolled.add(box)
        self.notebook.append_page(scrolled, Gtk.Label(label="CPU"))
    
    def create_memory_tab(self):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        self.memory_info = Gtk.Label(label="Detecting memory information...")
        self.memory_info.set_xalign(0)
        self.memory_info.set_yalign(0)
        self.memory_info.set_selectable(True)
        box.pack_start(self.memory_info, True, True, 0)
        
        scrolled.add(box)
        self.notebook.append_page(scrolled, Gtk.Label(label="Memory"))
    
    def create_graphics_tab(self):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        self.graphics_info = Gtk.Label(label="Detecting graphics information...")
        self.graphics_info.set_xalign(0)
        self.graphics_info.set_yalign(0)
        self.graphics_info.set_selectable(True)
        box.pack_start(self.graphics_info, True, True, 0)
        
        scrolled.add(box)
        self.notebook.append_page(scrolled, Gtk.Label(label="Graphics"))
    
    def create_audio_tab(self):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        self.audio_info = Gtk.Label(label="Detecting audio devices...")
        self.audio_info.set_xalign(0)
        self.audio_info.set_yalign(0)
        self.audio_info.set_selectable(True)
        box.pack_start(self.audio_info, True, True, 0)
        
        scrolled.add(box)
        self.notebook.append_page(scrolled, Gtk.Label(label="Audio"))
    
    def create_network_tab(self):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        self.network_info = Gtk.Label(label="Detecting network devices...")
        self.network_info.set_xalign(0)
        self.network_info.set_yalign(0)
        self.network_info.set_selectable(True)
        box.pack_start(self.network_info, True, True, 0)
        
        scrolled.add(box)
        self.notebook.append_page(scrolled, Gtk.Label(label="Network"))
    
    def create_storage_tab(self):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        self.storage_info = Gtk.Label(label="Detecting storage devices...")
        self.storage_info.set_xalign(0)
        self.storage_info.set_yalign(0)
        self.storage_info.set_selectable(True)
        box.pack_start(self.storage_info, True, True, 0)
        
        scrolled.add(box)
        self.notebook.append_page(scrolled, Gtk.Label(label="Storage"))
    
    def create_usb_tab(self):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        self.usb_info = Gtk.Label(label="Detecting USB devices...")
        self.usb_info.set_xalign(0)
        self.usb_info.set_yalign(0)
        self.usb_info.set_selectable(True)
        box.pack_start(self.usb_info, True, True, 0)
        
        scrolled.add(box)
        self.notebook.append_page(scrolled, Gtk.Label(label="USB"))
    
    def create_sensors_tab(self):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        self.sensors_info = Gtk.Label(label="Detecting sensors...")
        self.sensors_info.set_xalign(0)
        self.sensors_info.set_yalign(0)
        self.sensors_info.set_selectable(True)
        box.pack_start(self.sensors_info, True, True, 0)
        
        scrolled.add(box)
        self.notebook.append_page(scrolled, Gtk.Label(label="Sensors"))
    
    def run_command(self, command):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
            return result.stdout.strip() if result.returncode == 0 else ""
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return ""
    
    def detect_system_info(self):
        info = []
        info.append("=== System Information ===\n")
        
        # OS Information
        if os.path.exists("/etc/os-release"):
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME"):
                        info.append(f"OS: {line.split('=')[1].strip('\"')}")
                        break
        
        # Kernel and Architecture
        info.append(f"Kernel: {self.run_command('uname -r')}")
        info.append(f"Architecture: {self.run_command('uname -m')}")
        info.append(f"Uptime: {self.run_command('uptime -p 2>/dev/null || uptime')}")
        
        # Hostname
        info.append(f"Hostname: {self.run_command('hostname')}")
        
        GLib.idle_add(lambda: self.system_info.set_text("\n".join(info)))
    
    def detect_cpu_info(self):
        info = []
        info.append("=== CPU Information ===\n")
        
        # CPU details
        lscpu_output = self.run_command("lscpu")
        if lscpu_output:
            for line in lscpu_output.split('\n'):
                if any(keyword in line for keyword in ["Model name", "CPU(s)", "Core(s)", "Thread", "Architecture", "CPU max MHz", "CPU min MHz"]):
                    info.append(line)
        
        # CPU load
        load_avg = self.run_command("cat /proc/loadavg")
        if load_avg:
            info.append(f"\nLoad Average: {load_avg}")
        
        GLib.idle_add(lambda: self.cpu_info.set_text("\n".join(info)))
    
    def detect_memory_info(self):
        info = []
        info.append("=== Memory Information ===\n")
        
        # Memory details
        free_output = self.run_command("free -h")
        if free_output:
            info.append(free_output)
        
        # Additional memory info from /proc/meminfo
        meminfo = self.run_command("cat /proc/meminfo | head -10")
        if meminfo:
            info.append(f"\n=== Memory Details ===")
            info.append(meminfo)
        
        GLib.idle_add(lambda: self.memory_info.set_text("\n".join(info)))
    
    def detect_graphics_info(self):
        info = []
        info.append("=== Graphics Information ===\n")
        
        # Graphics cards
        lspci_output = self.run_command("lspci | grep -i vga")
        if lspci_output:
            info.append("Graphics Cards:")
            info.append(lspci_output)
        
        # Display information
        xrandr_output = self.run_command("xrandr --query 2>/dev/null | grep -E '(connected|disconnected)'")
        if xrandr_output:
            info.append(f"\n=== Display Information ===")
            info.append(xrandr_output)
        
        # Loaded drivers
        drivers_output = self.run_command("lsmod | grep -E '(nvidia|amdgpu|i915|nouveau)'")
        if drivers_output:
            info.append(f"\n=== Loaded Graphics Drivers ===")
            info.append(drivers_output)
        
        GLib.idle_add(lambda: self.graphics_info.set_text("\n".join(info)))
    
    def detect_audio_info(self):
        info = []
        info.append("=== Audio Information ===\n")
        
        # Playback devices
        aplay_output = self.run_command("aplay -l 2>/dev/null")
        if aplay_output:
            info.append("=== Playback Devices ===")
            info.append(aplay_output)
        
        # Capture devices (microphones)
        arecord_output = self.run_command("arecord -l 2>/dev/null")
        if arecord_output:
            info.append(f"\n=== Capture Devices (Microphones) ===")
            info.append(arecord_output)
        
        # ALSA cards
        alsa_output = self.run_command("cat /proc/asound/cards 2>/dev/null")
        if alsa_output:
            info.append(f"\n=== ALSA Sound Cards ===")
            info.append(alsa_output)
        
        GLib.idle_add(lambda: self.audio_info.set_text("\n".join(info)))
    
    def detect_network_info(self):
        info = []
        info.append("=== Network Information ===\n")
        
        # Network interfaces
        ip_output = self.run_command("ip link show | grep -E '^[0-9]'")
        if ip_output:
            info.append("Network Interfaces:")
            info.append(ip_output)
        
        # WiFi interfaces
        wifi_output = self.run_command("iw dev 2>/dev/null | grep Interface")
        if wifi_output:
            info.append(f"\n=== WiFi Interfaces ===")
            info.append(wifi_output)
        
        # WiFi scan
        wifi_scan = self.run_command("iwlist scan 2>/dev/null | head -20")
        if wifi_scan:
            info.append(f"\n=== WiFi Networks (first 20 lines) ===")
            info.append(wifi_scan)
        
        # Bluetooth
        bluetooth_devices = self.run_command("bluetoothctl devices 2>/dev/null")
        if bluetooth_devices:
            info.append(f"\n=== Bluetooth Devices ===")
            info.append(bluetooth_devices)
        elif self.run_command("hciconfig -a 2>/dev/null"):
            info.append(f"\n=== Bluetooth Interfaces ===")
            info.append(self.run_command("hciconfig -a 2>/dev/null"))
        
        GLib.idle_add(lambda: self.network_info.set_text("\n".join(info)))
    
    def detect_storage_info(self):
        info = []
        info.append("=== Storage Information ===\n")
        
        # Block devices
        lsblk_output = self.run_command("lsblk -o NAME,SIZE,TYPE,MOUNTPOINT,FSTYPE")
        if lsblk_output:
            info.append("Block Devices:")
            info.append(lsblk_output)
        
        # Filesystems
        df_output = self.run_command("df -h")
        if df_output:
            info.append(f"\n=== Mounted Filesystems ===")
            info.append(df_output)
        
        GLib.idle_add(lambda: self.storage_info.set_text("\n".join(info)))
    
    def detect_usb_info(self):
        info = []
        info.append("=== USB Information ===\n")
        
        # USB devices
        lsusb_output = self.run_command("lsusb")
        if lsusb_output:
            info.append("USB Devices:")
            info.append(lsusb_output)
        
        # Input devices
        input_devices = self.run_command("grep -E '(Name|Phys)' /proc/bus/input/devices | grep -v 'N: Name'")
        if input_devices:
            info.append(f"\n=== Input Devices ===")
            info.append(input_devices)
        
        GLib.idle_add(lambda: self.usb_info.set_text("\n".join(info)))
    
    def detect_sensors_info(self):
        info = []
        info.append("=== Sensors Information ===\n")
        
        # Temperature sensors
        sensors_output = self.run_command("sensors 2>/dev/null")
        if sensors_output:
            info.append("Temperature Sensors:")
            info.append(sensors_output)
        
        # Thermal zones
        thermal_info = []
        if os.path.exists("/sys/class/thermal"):
            for zone in sorted(os.listdir("/sys/class/thermal")):
                if zone.startswith("thermal_zone"):
                    temp_file = f"/sys/class/thermal/{zone}/temp"
                    if os.path.exists(temp_file):
                        try:
                            with open(temp_file, "r") as f:
                                temp_millidegrees = int(f.read().strip())
                                temp_celsius = temp_millidegrees // 1000
                                thermal_info.append(f"{zone}: {temp_celsius}°C")
                        except:
                            pass
        
        if thermal_info:
            info.append(f"\n=== Thermal Zones ===")
            info.append("\n".join(thermal_info))
        
        # Battery information
        battery_info = []
        if os.path.exists("/sys/class/power_supply"):
            for supply in os.listdir("/sys/class/power_supply"):
                status_file = f"/sys/class/power_supply/{supply}/status"
                if os.path.exists(status_file):
                    try:
                        with open(status_file, "r") as f:
                            status = f.read().strip()
                        
                        battery_info.append(f"{supply}: {status}")
                        
                        capacity_file = f"/sys/class/power_supply/{supply}/capacity"
                        if os.path.exists(capacity_file):
                            with open(capacity_file, "r") as f:
                                capacity = f.read().strip()
                            battery_info.append(f"  Capacity: {capacity}%")
                    except:
                        pass
        
        if battery_info:
            info.append(f"\n=== Battery Information ===")
            info.append("\n".join(battery_info))
        
        GLib.idle_add(lambda: self.sensors_info.set_text("\n".join(info)))
    
    def detect_all_hardware(self):
        self.status_label.set_text("Detecting hardware...")
        
        # Run detection in separate threads
        threading.Thread(target=self.detect_system_info, daemon=True).start()
        threading.Thread(target=self.detect_cpu_info, daemon=True).start()
        threading.Thread(target=self.detect_memory_info, daemon=True).start()
        threading.Thread(target=self.detect_graphics_info, daemon=True).start()
        threading.Thread(target=self.detect_audio_info, daemon=True).start()
        threading.Thread(target=self.detect_network_info, daemon=True).start()
        threading.Thread(target=self.detect_storage_info, daemon=True).start()
        threading.Thread(target=self.detect_usb_info, daemon=True).start()
        threading.Thread(target=self.detect_sensors_info, daemon=True).start()
        
        GLib.timeout_add_seconds(2, lambda: self.status_label.set_text("Hardware detection complete"))
    
    def on_refresh_clicked(self, button):
        self.detect_all_hardware()

if __name__ == "__main__":
    win = HardwareDetector()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
