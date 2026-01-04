#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
import psutil
import os

class SystemMonitor(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="MuxOS System Monitor")
        self.set_default_size(600, 400)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = "System Monitor"
        self.set_titlebar(header)
        
        notebook = Gtk.Notebook()
        self.add(notebook)
        
        self.processes_page = self.create_processes_page()
        notebook.append_page(self.processes_page, Gtk.Label(label="Processes"))
        
        self.resources_page = self.create_resources_page()
        notebook.append_page(self.resources_page, Gtk.Label(label="Resources"))
        
        GLib.timeout_add_seconds(2, self.update_data)
        
    def create_processes_page(self):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        self.process_store = Gtk.ListStore(int, str, str, str)
        
        treeview = Gtk.TreeView(model=self.process_store)
        
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("PID", renderer, text=0)
        treeview.append_column(column)
        
        column = Gtk.TreeViewColumn("Name", renderer, text=1)
        treeview.append_column(column)
        
        column = Gtk.TreeViewColumn("CPU %", renderer, text=2)
        treeview.append_column(column)
        
        column = Gtk.TreeViewColumn("Memory", renderer, text=3)
        treeview.append_column(column)
        
        scrolled.add(treeview)
        return scrolled
    
    def create_resources_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
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
        
        return box
    
    def update_data(self):
        self.process_store.clear()
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
            try:
                info = proc.info
                mem_mb = info['memory_info'].rss / 1024 / 1024
                self.process_store.append([
                    info['pid'],
                    info['name'],
                    f"{info['cpu_percent']:.1f}",
                    f"{mem_mb:.1f} MB"
                ])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        cpu_percent = psutil.cpu_percent(interval=1)
        self.cpu_label.set_text(f"CPU Usage: {cpu_percent:.1f}%")
        self.cpu_bar.set_fraction(cpu_percent / 100)
        
        mem = psutil.virtual_memory()
        self.mem_label.set_text(f"Memory: {mem.used / 1024**3:.1f} GB / {mem.total / 1024**3:.1f} GB ({mem.percent:.1f}%)")
        self.mem_bar.set_fraction(mem.percent / 100)
        
        swap = psutil.swap_memory()
        self.swap_label.set_text(f"Swap: {swap.used / 1024**3:.1f} GB / {swap.total / 1024**3:.1f} GB ({swap.percent:.1f}%)")
        self.swap_bar.set_fraction(swap.percent / 100)
        
        return True

if __name__ == "__main__":
    win = SystemMonitor()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
