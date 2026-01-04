#!/usr/bin/env python3
"""MuxOS Task Manager - Process and system management"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
import subprocess
import os

class TaskManager(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="MuxOS Task Manager")
        self.set_default_size(900, 600)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = "Task Manager"
        self.set_titlebar(header)
        
        end_btn = Gtk.Button(label="End Task")
        end_btn.connect("clicked", self.end_task)
        header.pack_end(end_btn)
        
        notebook = Gtk.Notebook()
        self.add(notebook)
        
        notebook.append_page(self.create_processes_page(), Gtk.Label(label="Processes"))
        notebook.append_page(self.create_performance_page(), Gtk.Label(label="Performance"))
        notebook.append_page(self.create_startup_page(), Gtk.Label(label="Startup"))
        notebook.append_page(self.create_services_page(), Gtk.Label(label="Services"))
        notebook.append_page(self.create_users_page(), Gtk.Label(label="Users"))
        
        GLib.timeout_add_seconds(2, self.refresh_processes)
        GLib.timeout_add_seconds(1, self.update_performance)
    
    def create_processes_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        scrolled = Gtk.ScrolledWindow()
        
        self.process_store = Gtk.ListStore(int, str, str, str, str)
        self.process_tree = Gtk.TreeView(model=self.process_store)
        
        columns = ["PID", "Name", "CPU %", "Memory", "User"]
        for i, title in enumerate(columns):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(title, renderer, text=i)
            column.set_sortable(True)
            column.set_resizable(True)
            self.process_tree.append_column(column)
        
        scrolled.add(self.process_tree)
        box.pack_start(scrolled, True, True, 0)
        
        self.refresh_processes()
        return box
    
    def create_performance_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        box.set_margin_top(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        self.cpu_label = Gtk.Label()
        self.cpu_label.set_xalign(0)
        box.pack_start(self.cpu_label, False, False, 0)
        self.cpu_bar = Gtk.ProgressBar()
        box.pack_start(self.cpu_bar, False, False, 0)
        
        self.mem_label = Gtk.Label()
        self.mem_label.set_xalign(0)
        box.pack_start(self.mem_label, False, False, 10)
        self.mem_bar = Gtk.ProgressBar()
        box.pack_start(self.mem_bar, False, False, 0)
        
        self.swap_label = Gtk.Label()
        self.swap_label.set_xalign(0)
        box.pack_start(self.swap_label, False, False, 10)
        self.swap_bar = Gtk.ProgressBar()
        box.pack_start(self.swap_bar, False, False, 0)
        
        self.disk_label = Gtk.Label()
        self.disk_label.set_xalign(0)
        box.pack_start(self.disk_label, False, False, 10)
        self.disk_bar = Gtk.ProgressBar()
        box.pack_start(self.disk_bar, False, False, 0)
        
        self.uptime_label = Gtk.Label()
        self.uptime_label.set_xalign(0)
        box.pack_start(self.uptime_label, False, False, 10)
        
        return box
    
    def create_startup_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        scrolled = Gtk.ScrolledWindow()
        
        self.startup_store = Gtk.ListStore(bool, str, str, str)
        startup_tree = Gtk.TreeView(model=self.startup_store)
        
        toggle = Gtk.CellRendererToggle()
        toggle.connect("toggled", self.on_startup_toggled)
        col = Gtk.TreeViewColumn("Enabled", toggle, active=0)
        startup_tree.append_column(col)
        
        for i, title in enumerate(["Name", "Command", "Status"], 1):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(title, renderer, text=i)
            startup_tree.append_column(column)
        
        self.startup_store.append([True, "Network Manager Applet", "nm-applet", "Running"])
        self.startup_store.append([True, "Volume Icon", "volumeicon", "Running"])
        self.startup_store.append([True, "Compositor", "picom", "Running"])
        self.startup_store.append([False, "Bluetooth Manager", "blueman-applet", "Disabled"])
        
        scrolled.add(startup_tree)
        box.pack_start(scrolled, True, True, 0)
        
        return box
    
    def create_services_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        scrolled = Gtk.ScrolledWindow()
        
        self.services_store = Gtk.ListStore(str, str, str)
        services_tree = Gtk.TreeView(model=self.services_store)
        
        for i, title in enumerate(["Service", "Status", "Description"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(title, renderer, text=i)
            column.set_resizable(True)
            services_tree.append_column(column)
        
        services = [
            ("NetworkManager", "active", "Network connection manager"),
            ("lightdm", "active", "Display manager"),
            ("pulseaudio", "active", "Sound server"),
            ("ssh", "inactive", "OpenSSH server"),
            ("cups", "inactive", "Printing service"),
            ("bluetooth", "inactive", "Bluetooth service")
        ]
        
        for name, status, desc in services:
            self.services_store.append([name, status, desc])
        
        scrolled.add(services_tree)
        box.pack_start(scrolled, True, True, 0)
        
        btn_box = Gtk.Box(spacing=10)
        btn_box.set_margin_top(10)
        btn_box.set_margin_bottom(10)
        btn_box.set_margin_start(10)
        
        start_btn = Gtk.Button(label="Start")
        btn_box.pack_start(start_btn, False, False, 0)
        
        stop_btn = Gtk.Button(label="Stop")
        btn_box.pack_start(stop_btn, False, False, 0)
        
        restart_btn = Gtk.Button(label="Restart")
        btn_box.pack_start(restart_btn, False, False, 0)
        
        box.pack_start(btn_box, False, False, 0)
        
        return box
    
    def create_users_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        scrolled = Gtk.ScrolledWindow()
        
        users_store = Gtk.ListStore(str, str, str, str)
        users_tree = Gtk.TreeView(model=users_store)
        
        for i, title in enumerate(["User", "Session", "CPU", "Memory"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(title, renderer, text=i)
            users_tree.append_column(column)
        
        users_store.append([os.getenv("USER", "muxos"), "X11", "5%", "1.2 GB"])
        
        scrolled.add(users_tree)
        box.pack_start(scrolled, True, True, 0)
        
        return box
    
    def refresh_processes(self):
        self.process_store.clear()
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'username']):
                try:
                    info = proc.info
                    mem_mb = info['memory_info'].rss / 1024 / 1024
                    self.process_store.append([
                        info['pid'],
                        info['name'][:30],
                        f"{info['cpu_percent']:.1f}%",
                        f"{mem_mb:.1f} MB",
                        info['username'] or "system"
                    ])
                except:
                    pass
        except:
            result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
            for line in result.stdout.split('\n')[1:11]:
                parts = line.split()
                if len(parts) >= 11:
                    self.process_store.append([
                        int(parts[1]),
                        parts[10][:30],
                        parts[2] + "%",
                        parts[5],
                        parts[0]
                    ])
        return True
    
    def update_performance(self):
        try:
            import psutil
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            disk = psutil.disk_usage('/')
            
            self.cpu_label.set_text(f"CPU Usage: {cpu:.1f}%")
            self.cpu_bar.set_fraction(cpu / 100)
            
            self.mem_label.set_text(f"Memory: {mem.used/1024**3:.1f} GB / {mem.total/1024**3:.1f} GB ({mem.percent:.1f}%)")
            self.mem_bar.set_fraction(mem.percent / 100)
            
            self.swap_label.set_text(f"Swap: {swap.used/1024**3:.1f} GB / {swap.total/1024**3:.1f} GB ({swap.percent:.1f}%)")
            self.swap_bar.set_fraction(swap.percent / 100 if swap.total > 0 else 0)
            
            self.disk_label.set_text(f"Disk: {disk.used/1024**3:.1f} GB / {disk.total/1024**3:.1f} GB ({disk.percent:.1f}%)")
            self.disk_bar.set_fraction(disk.percent / 100)
            
            uptime = subprocess.run(["uptime", "-p"], capture_output=True, text=True)
            self.uptime_label.set_text(f"Uptime: {uptime.stdout.strip()}")
        except:
            pass
        return True
    
    def end_task(self, button):
        selection = self.process_tree.get_selection()
        model, treeiter = selection.get_selected()
        if treeiter:
            pid = model[treeiter][0]
            dialog = Gtk.MessageDialog(transient_for=self, message_type=Gtk.MessageType.QUESTION,
                                       buttons=Gtk.ButtonsType.YES_NO, text="End Process?")
            dialog.format_secondary_text(f"Are you sure you want to end process {pid}?")
            response = dialog.run()
            dialog.destroy()
            if response == Gtk.ResponseType.YES:
                subprocess.run(["kill", str(pid)])
                self.refresh_processes()
    
    def on_startup_toggled(self, widget, path):
        self.startup_store[path][0] = not self.startup_store[path][0]

if __name__ == "__main__":
    win = TaskManager()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
