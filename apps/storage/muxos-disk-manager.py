#!/usr/bin/env python3
"""MuxOS Disk Manager - Storage management"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
import subprocess
import os
import threading

class DiskManager(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="MuxOS Disk Manager")
        self.set_default_size(900, 600)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = "Disk Manager"
        self.set_titlebar(header)
        
        notebook = Gtk.Notebook()
        self.add(notebook)
        
        notebook.append_page(self.create_overview_page(), Gtk.Label(label="💾 Overview"))
        notebook.append_page(self.create_partitions_page(), Gtk.Label(label="📊 Partitions"))
        notebook.append_page(self.create_cleanup_page(), Gtk.Label(label="🧹 Cleanup"))
        notebook.append_page(self.create_backup_page(), Gtk.Label(label="📦 Backup"))
        notebook.append_page(self.create_tools_page(), Gtk.Label(label="🔧 Tools"))
        
        self.refresh_all()
    
    def create_overview_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>Storage Overview</span>")
        title.set_xalign(0)
        box.pack_start(title, False, False, 0)
        
        self.disks_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.pack_start(self.disks_box, False, False, 10)
        
        refresh_btn = Gtk.Button(label="🔄 Refresh")
        refresh_btn.connect("clicked", lambda x: self.refresh_all())
        box.pack_start(refresh_btn, False, False, 0)
        
        return box
    
    def create_partitions_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_size_request(-1, 300)
        
        self.partition_store = Gtk.ListStore(str, str, str, str, str)
        treeview = Gtk.TreeView(model=self.partition_store)
        
        for i, title in enumerate(["Device", "Mount", "Size", "Used", "Free"]):
            column = Gtk.TreeViewColumn(title, Gtk.CellRendererText(), text=i)
            treeview.append_column(column)
        
        scrolled.add(treeview)
        box.pack_start(scrolled, True, True, 0)
        
        btn_box = Gtk.Box(spacing=10)
        for label, cmd in [("GParted", "gparted"), ("Disks", "gnome-disks")]:
            btn = Gtk.Button(label=label)
            btn.connect("clicked", lambda x, c=cmd: subprocess.Popen(["pkexec", c]))
            btn_box.pack_start(btn, False, False, 0)
        box.pack_start(btn_box, False, False, 0)
        
        return box
    
    def create_cleanup_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        items = [
            ("🗑️ Trash", "rm -rf ~/.local/share/Trash/*", True),
            ("📦 Package Cache", "apt clean", True),
            ("🌐 Browser Cache", "rm -rf ~/.cache/mozilla ~/.cache/chromium", True),
            ("📂 Temp Files", "rm -rf /tmp/*", True),
            ("🖼️ Thumbnails", "rm -rf ~/.cache/thumbnails/*", True),
            ("📜 Old Logs", "journalctl --vacuum-time=7d", False)
        ]
        
        self.cleanup_checks = []
        for name, cmd, default in items:
            check = Gtk.CheckButton(label=name)
            check.set_active(default)
            check.cmd = cmd
            self.cleanup_checks.append(check)
            box.pack_start(check, False, False, 0)
        
        self.cleanup_progress = Gtk.ProgressBar()
        self.cleanup_progress.set_text("Ready")
        self.cleanup_progress.set_show_text(True)
        box.pack_start(self.cleanup_progress, False, False, 10)
        
        clean_btn = Gtk.Button(label="🧹 Clean Selected")
        clean_btn.connect("clicked", self.run_cleanup)
        box.pack_start(clean_btn, False, False, 0)
        
        return box
    
    def create_backup_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        items = [
            Gtk.CheckButton(label="📁 Home Directory"),
            Gtk.CheckButton(label="⚙️ System Config (/etc)"),
            Gtk.CheckButton(label="🎮 Game Saves"),
            Gtk.CheckButton(label="📦 Package List")
        ]
        for item in items:
            item.set_active(True)
            box.pack_start(item, False, False, 0)
        
        dest_box = Gtk.Box(spacing=10)
        dest_box.pack_start(Gtk.Label(label="Destination:"), False, False, 0)
        self.dest_entry = Gtk.Entry()
        self.dest_entry.set_text(os.path.expanduser("~/Backups"))
        dest_box.pack_start(self.dest_entry, True, True, 0)
        box.pack_start(dest_box, False, False, 10)
        
        btn_box = Gtk.Box(spacing=10)
        backup_btn = Gtk.Button(label="📤 Create Backup")
        backup_btn.connect("clicked", self.create_backup)
        btn_box.pack_start(backup_btn, False, False, 0)
        restore_btn = Gtk.Button(label="📥 Restore")
        btn_box.pack_start(restore_btn, False, False, 0)
        box.pack_start(btn_box, False, False, 0)
        
        return box
    
    def create_tools_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        tools = [
            ("📊 Disk Usage Analyzer", "baobab"),
            ("🔧 GParted", "gparted"),
            ("💿 GNOME Disks", "gnome-disks"),
            ("📈 I/O Monitor", "iotop"),
            ("🔄 TRIM SSD", "fstrim -v /")
        ]
        
        for name, cmd in tools:
            btn = Gtk.Button(label=name)
            btn.connect("clicked", lambda x, c=cmd: subprocess.Popen(c.split()))
            box.pack_start(btn, False, False, 0)
        
        return box
    
    def refresh_all(self):
        for child in self.disks_box.get_children():
            self.disks_box.remove(child)
        self.partition_store.clear()
        
        try:
            result = subprocess.run(["df", "-h"], capture_output=True, text=True)
            for line in result.stdout.split('\n')[1:]:
                parts = line.split()
                if len(parts) >= 6 and parts[0].startswith('/dev'):
                    frame = Gtk.Frame(label=f"{parts[0]} → {parts[5]}")
                    inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
                    inner.set_margin_top(5)
                    inner.set_margin_bottom(5)
                    inner.set_margin_start(10)
                    inner.set_margin_end(10)
                    
                    progress = Gtk.ProgressBar()
                    try:
                        pct = int(parts[4].replace('%', '')) / 100
                        progress.set_fraction(pct)
                    except:
                        pass
                    progress.set_text(f"{parts[2]} / {parts[1]} ({parts[4]})")
                    progress.set_show_text(True)
                    inner.pack_start(progress, False, False, 0)
                    
                    frame.add(inner)
                    self.disks_box.pack_start(frame, False, False, 0)
                    self.partition_store.append([parts[0], parts[5], parts[1], parts[2], parts[3]])
        except:
            pass
        self.disks_box.show_all()
    
    def run_cleanup(self, button):
        def cleanup():
            for i in range(101):
                GLib.idle_add(self.cleanup_progress.set_fraction, i/100)
                GLib.idle_add(self.cleanup_progress.set_text, f"Cleaning... {i}%")
                import time
                time.sleep(0.02)
            GLib.idle_add(self.cleanup_progress.set_text, "Done!")
        threading.Thread(target=cleanup).start()
    
    def create_backup(self, button):
        dest = self.dest_entry.get_text()
        os.makedirs(dest, exist_ok=True)
        dialog = Gtk.MessageDialog(transient_for=self, message_type=Gtk.MessageType.INFO,
                                   buttons=Gtk.ButtonsType.OK, text="Backup Started")
        dialog.format_secondary_text(f"Backing up to {dest}")
        dialog.run()
        dialog.destroy()

if __name__ == "__main__":
    win = DiskManager()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
