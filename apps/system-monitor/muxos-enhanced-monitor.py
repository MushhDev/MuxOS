#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Pango
import psutil
import os
import threading
import subprocess

class EnhancedSystemMonitor(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="MuxOS Enhanced System Monitor")
        self.set_default_size(800, 600)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        # Create header bar
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = "Enhanced System Monitor"
        
        # Add refresh button
        refresh_btn = Gtk.Button.new_from_icon_name("view-refresh", Gtk.IconSize.BUTTON)
        refresh_btn.connect("clicked", self.on_refresh_clicked)
        refresh_btn.set_tooltip_text("Refresh all information")
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
        notebook = Gtk.Notebook()
        main_box.pack_start(notebook, True, True, 0)
        
        # Create tabs
        self.create_processes_page(notebook)
        self.create_resources_page(notebook)
        self.create_hardware_page(notebook)
        self.create_network_page(notebook)
        self.create_storage_page(notebook)
        
        # Status bar
        self.status_label = Gtk.Label(label="Ready")
        self.status_label.set_halign(Gtk.Align.START)
        main_box.pack_start(self.status_label, False, False, 5)
        
        # Start updates
        GLib.timeout_add_seconds(2, self.update_data)
        self.update_hardware_info()
    
    def create_processes_page(self, notebook):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        self.process_store = Gtk.ListStore(int, str, str, str, str)
        
        treeview = Gtk.TreeView(model=self.process_store)
        
        # Columns
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("PID", renderer, text=0)
        treeview.append_column(column)
        
        column = Gtk.TreeViewColumn("Name", renderer, text=1)
        treeview.append_column(column)
        
        column = Gtk.TreeViewColumn("CPU %", renderer, text=2)
        treeview.append_column(column)
        
        column = Gtk.TreeViewColumn("Memory", renderer, text=3)
        treeview.append_column(column)
        
        column = Gtk.TreeViewColumn("Status", renderer, text=4)
        treeview.append_column(column)
        
        scrolled.add(treeview)
        notebook.append_page(scrolled, Gtk.Label(label="Processes"))
    
    def create_resources_page(self, notebook):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        # CPU Section
        cpu_frame = Gtk.Frame(label="CPU Usage")
        cpu_frame.set_label_align(0.05, 0.5)
        cpu_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        cpu_box.set_margin_top(10)
        cpu_box.set_margin_bottom(10)
        cpu_box.set_margin_start(10)
        cpu_box.set_margin_end(10)
        
        self.cpu_label = Gtk.Label()
        self.cpu_label.set_xalign(0)
        cpu_box.pack_start(self.cpu_label, False, False, 0)
        
        self.cpu_bar = Gtk.ProgressBar()
        self.cpu_bar.set_margin_top(5)
        cpu_box.pack_start(self.cpu_bar, False, False, 0)
        
        # CPU Cores
        self.cpu_cores_label = Gtk.Label()
        self.cpu_cores_label.set_xalign(0)
        cpu_box.pack_start(self.cpu_cores_label, False, False, 5)
        
        cpu_frame.add(cpu_box)
        box.pack_start(cpu_frame, False, False, 0)
        
        # Memory Section
        mem_frame = Gtk.Frame(label="Memory Usage")
        mem_frame.set_label_align(0.05, 0.5)
        mem_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        mem_box.set_margin_top(10)
        mem_box.set_margin_bottom(10)
        mem_box.set_margin_start(10)
        mem_box.set_margin_end(10)
        
        self.mem_label = Gtk.Label()
        self.mem_label.set_xalign(0)
        mem_box.pack_start(self.mem_label, False, False, 0)
        
        self.mem_bar = Gtk.ProgressBar()
        self.mem_bar.set_margin_top(5)
        mem_box.pack_start(self.mem_bar, False, False, 0)
        
        mem_frame.add(mem_box)
        box.pack_start(mem_frame, False, False, 0)
        
        # Swap Section
        swap_frame = Gtk.Frame(label="Swap Usage")
        swap_frame.set_label_align(0.05, 0.5)
        swap_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        swap_box.set_margin_top(10)
        swap_box.set_margin_bottom(10)
        swap_box.set_margin_start(10)
        swap_box.set_margin_end(10)
        
        self.swap_label = Gtk.Label()
        self.swap_label.set_xalign(0)
        swap_box.pack_start(self.swap_label, False, False, 0)
        
        self.swap_bar = Gtk.ProgressBar()
        self.swap_bar.set_margin_top(5)
        swap_box.pack_start(self.swap_bar, False, False, 0)
        
        swap_frame.add(swap_box)
        box.pack_start(swap_frame, False, False, 0)
        
        # System Load
        load_frame = Gtk.Frame(label="System Load")
        load_frame.set_label_align(0.05, 0.5)
        load_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        load_box.set_margin_top(10)
        load_box.set_margin_bottom(10)
        load_box.set_margin_start(10)
        load_box.set_margin_end(10)
        
        self.load_label = Gtk.Label()
        self.load_label.set_xalign(0)
        load_box.pack_start(self.load_label, False, False, 0)
        
        self.uptime_label = Gtk.Label()
        self.uptime_label.set_xalign(0)
        load_box.pack_start(self.uptime_label, False, False, 5)
        
        load_frame.add(load_box)
        box.pack_start(load_frame, False, False, 0)
        
        notebook.append_page(box, Gtk.Label(label="Resources"))
    
    def create_hardware_page(self, notebook):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        self.hardware_info = Gtk.Label(label="Loading hardware information...")
        self.hardware_info.set_xalign(0)
        self.hardware_info.set_yalign(0)
        self.hardware_info.set_selectable(True)
        box.pack_start(self.hardware_info, True, True, 0)
        
        scrolled.add(box)
        notebook.append_page(scrolled, Gtk.Label(label="Hardware"))
    
    def create_network_page(self, notebook):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        # Network I/O
        net_frame = Gtk.Frame(label="Network I/O")
        net_frame.set_label_align(0.05, 0.5)
        net_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        net_box.set_margin_top(10)
        net_box.set_margin_bottom(10)
        net_box.set_margin_start(10)
        net_box.set_margin_end(10)
        
        self.net_upload_label = Gtk.Label()
        self.net_upload_label.set_xalign(0)
        net_box.pack_start(self.net_upload_label, False, False, 0)
        
        self.net_download_label = Gtk.Label()
        self.net_download_label.set_xalign(0)
        net_box.pack_start(self.net_download_label, False, False, 0)
        
        net_frame.add(net_box)
        box.pack_start(net_frame, False, False, 0)
        
        # Network Connections
        conn_frame = Gtk.Frame(label="Active Connections")
        conn_frame.set_label_align(0.05, 0.5)
        conn_scrolled = Gtk.ScrolledWindow()
        conn_scrolled.set_min_content_height(200)
        
        self.connection_store = Gtk.ListStore(str, str, str, str)
        
        conn_treeview = Gtk.TreeView(model=self.connection_store)
        
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Local Address", renderer, text=0)
        conn_treeview.append_column(column)
        
        column = Gtk.TreeViewColumn("Remote Address", renderer, text=1)
        conn_treeview.append_column(column)
        
        column = Gtk.TreeViewColumn("Status", renderer, text=2)
        conn_treeview.append_column(column)
        
        column = Gtk.TreeViewColumn("PID", renderer, text=3)
        conn_treeview.append_column(column)
        
        conn_scrolled.add(conn_treeview)
        conn_frame.add(conn_scrolled)
        box.pack_start(conn_frame, True, True, 0)
        
        notebook.append_page(box, Gtk.Label(label="Network"))
    
    def create_storage_page(self, notebook):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        # Disk Usage
        disk_frame = Gtk.Frame(label="Disk Usage")
        disk_frame.set_label_align(0.05, 0.5)
        disk_scrolled = Gtk.ScrolledWindow()
        disk_scrolled.set_min_content_height(200)
        
        self.disk_store = Gtk.ListStore(str, str, str, str)
        
        disk_treeview = Gtk.TreeView(model=self.disk_store)
        
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Filesystem", renderer, text=0)
        disk_treeview.append_column(column)
        
        column = Gtk.TreeViewColumn("Size", renderer, text=1)
        disk_treeview.append_column(column)
        
        column = Gtk.TreeViewColumn("Used", renderer, text=2)
        disk_treeview.append_column(column)
        
        column = Gtk.TreeViewColumn("Available", renderer, text=3)
        disk_treeview.append_column(column)
        
        disk_scrolled.add(disk_treeview)
        disk_frame.add(disk_scrolled)
        box.pack_start(disk_frame, True, True, 0)
        
        # Disk I/O
        io_frame = Gtk.Frame(label="Disk I/O")
        io_frame.set_label_align(0.05, 0.5)
        io_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        io_box.set_margin_top(10)
        io_box.set_margin_bottom(10)
        io_box.set_margin_start(10)
        io_box.set_margin_end(10)
        
        self.disk_read_label = Gtk.Label()
        self.disk_read_label.set_xalign(0)
        io_box.pack_start(self.disk_read_label, False, False, 0)
        
        self.disk_write_label = Gtk.Label()
        self.disk_write_label.set_xalign(0)
        io_box.pack_start(self.disk_write_label, False, False, 0)
        
        io_frame.add(io_box)
        box.pack_start(io_frame, False, False, 0)
        
        notebook.append_page(box, Gtk.Label(label="Storage"))
    
    def run_command(self, command):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=5)
            return result.stdout.strip() if result.returncode == 0 else ""
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return ""
    
    def update_hardware_info(self):
        def get_hardware_info():
            info = []
            info.append("=== Hardware Information ===\n")
            
            # CPU Information
            cpu_model = self.run_command("grep 'model name' /proc/cpuinfo | head -1 | cut -d':' -f2 | sed 's/^ *//'")
            if cpu_model:
                info.append(f"CPU Model: {cpu_model}")
            
            cpu_cores = psutil.cpu_count(logical=False)
            cpu_threads = psutil.cpu_count(logical=True)
            info.append(f"Cores: {cpu_cores}, Threads: {cpu_threads}")
            
            # Memory Information
            mem = psutil.virtual_memory()
            info.append(f"Total Memory: {mem.total / (1024**3):.1f} GB")
            
            # Graphics Card
            gpu_info = self.run_command("lspci | grep -i vga | head -1")
            if gpu_info:
                info.append(f"Graphics: {gpu_info}")
            
            # Audio Devices
            audio_count = len(self.run_command("aplay -l 2>/dev/null | grep card").split('\n')) if self.run_command("aplay -l 2>/dev/null") else 0
            if audio_count > 0:
                info.append(f"Audio Devices: {audio_count}")
            
            # Network Interfaces
            net_interfaces = len([i for i in psutil.net_if_addrs().keys() if not i.startswith('lo')])
            info.append(f"Network Interfaces: {net_interfaces}")
            
            # Battery
            battery = psutil.sensors_battery()
            if battery:
                info.append(f"Battery: {battery.percent:.0f}% ({'Charging' if battery.power_plugged else 'Discharging'})")
            
            return "\n".join(info)
        
        def update_ui():
            self.hardware_info.set_text(get_hardware_info())
        
        threading.Thread(target=update_ui, daemon=True).start()
    
    def update_data(self):
        # Update processes
        self.process_store.clear()
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'status']):
            try:
                info = proc.info
                mem_mb = info['memory_info'].rss / 1024 / 1024
                self.process_store.append([
                    info['pid'],
                    info['name'][:30],  # Truncate long names
                    f"{info['cpu_percent']:.1f}",
                    f"{mem_mb:.1f} MB",
                    info['status']
                ])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Update CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        self.cpu_label.set_text(f"CPU Usage: {cpu_percent:.1f}%")
        self.cpu_bar.set_fraction(cpu_percent / 100)
        
        # Update CPU cores
        cpu_per_core = psutil.cpu_percent(percpu=True)
        core_info = " | ".join([f"Core {i+1}: {cpu:.1f}%" for i, cpu in enumerate(cpu_per_core)])
        self.cpu_cores_label.set_text(core_info)
        
        # Update Memory
        mem = psutil.virtual_memory()
        self.mem_label.set_text(f"Memory: {mem.used / 1024**3:.1f} GB / {mem.total / 1024**3:.1f} GB ({mem.percent:.1f}%)")
        self.mem_bar.set_fraction(mem.percent / 100)
        
        # Update Swap
        swap = psutil.swap_memory()
        self.swap_label.set_text(f"Swap: {swap.used / 1024**3:.1f} GB / {swap.total / 1024**3:.1f} GB ({swap.percent:.1f}%)")
        self.swap_bar.set_fraction(swap.percent / 100)
        
        # Update System Load
        load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else (0, 0, 0)
        self.load_label.set_text(f"Load Average: {load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}")
        
        # Update Uptime
        uptime_hours = psutil.boot_time()
        import time
        uptime_seconds = time.time() - uptime_hours
        uptime_days = uptime_seconds // 86400
        uptime_hours = (uptime_seconds % 86400) // 3600
        uptime_minutes = (uptime_seconds % 3600) // 60
        self.uptime_label.set_text(f"Uptime: {int(uptime_days)}d {int(uptime_hours)}h {int(uptime_minutes)}m")
        
        # Update Network I/O
        net_io = psutil.net_io_counters()
        if hasattr(self, 'last_net_io'):
            upload_speed = (net_io.bytes_sent - self.last_net_io.bytes_sent) / 1024 / 2  # KB/s
            download_speed = (net_io.bytes_recv - self.last_net_io.bytes_recv) / 1024 / 2  # KB/s
            self.net_upload_label.set_text(f"Upload: {upload_speed:.1f} KB/s")
            self.net_download_label.set_text(f"Download: {download_speed:.1f} KB/s")
        self.last_net_io = net_io
        
        # Update Network Connections
        self.connection_store.clear()
        for conn in psutil.net_connections(kind='inet')[:20]:  # Limit to 20 connections
            try:
                local_addr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A"
                remote_addr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"
                status = conn.status
                pid = str(conn.pid) if conn.pid else "N/A"
                
                self.connection_store.append([local_addr, remote_addr, status, pid])
            except:
                pass
        
        # Update Disk Usage
        self.disk_store.clear()
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                self.disk_store.append([
                    partition.device,
                    f"{usage.total / 1024**3:.1f} GB",
                    f"{usage.used / 1024**3:.1f} GB",
                    f"{usage.free / 1024**3:.1f} GB"
                ])
            except:
                pass
        
        # Update Disk I/O
        disk_io = psutil.disk_io_counters()
        if hasattr(self, 'last_disk_io'):
            read_speed = (disk_io.read_bytes - self.last_disk_io.read_bytes) / 1024 / 2  # KB/s
            write_speed = (disk_io.write_bytes - self.last_disk_io.write_bytes) / 1024 / 2  # KB/s
            self.disk_read_label.set_text(f"Disk Read: {read_speed:.1f} KB/s")
            self.disk_write_label.set_text(f"Disk Write: {write_speed:.1f} KB/s")
        self.last_disk_io = disk_io
        
        return True
    
    def on_refresh_clicked(self, button):
        self.update_hardware_info()
        self.status_label.set_text("Refreshing...")
        GLib.timeout_add_seconds(1, lambda: self.status_label.set_text("Ready"))

if __name__ == "__main__":
    win = EnhancedSystemMonitor()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
