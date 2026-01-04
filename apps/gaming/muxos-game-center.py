#!/usr/bin/env python3
"""MuxOS Game Center - Gaming hub and optimization"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
import subprocess
import os
import json
import threading

class GameCenter(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="MuxOS Game Center")
        self.set_default_size(1100, 700)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        self.config_file = os.path.expanduser("~/.config/muxos/games.json")
        self.load_config()
        
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = "🎮 Game Center"
        self.set_titlebar(header)
        
        mode_btn = Gtk.Button(label="⚡ Gaming Mode")
        mode_btn.connect("clicked", self.toggle_gaming_mode)
        header.pack_end(mode_btn)
        
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.add(main_box)
        
        sidebar = self.create_sidebar()
        main_box.pack_start(sidebar, False, False, 0)
        
        self.content_stack = Gtk.Stack()
        main_box.pack_start(self.content_stack, True, True, 10)
        
        self.create_pages()
    
    def load_config(self):
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            if os.path.exists(self.config_file):
                with open(self.config_file) as f:
                    self.config = json.load(f)
            else:
                self.config = {"gaming_mode": False, "games": [], "optimizations": {}}
        except:
            self.config = {}
    
    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def create_sidebar(self):
        sidebar = Gtk.ListBox()
        sidebar.set_size_request(200, -1)
        
        items = [
            ("🏠 Dashboard", "dashboard"),
            ("🎮 My Games", "games"),
            ("⚡ Optimizations", "optimize"),
            ("🖥️ Performance", "performance"),
            ("🛠️ Tools", "tools"),
            ("📊 Stats", "stats"),
            ("⚙️ Settings", "settings")
        ]
        
        for name, page_id in items:
            row = Gtk.ListBoxRow()
            row.page_id = page_id
            label = Gtk.Label(label=name)
            label.set_xalign(0)
            label.set_margin_start(10)
            label.set_margin_top(8)
            label.set_margin_bottom(8)
            row.add(label)
            sidebar.add(row)
        
        sidebar.connect("row-activated", lambda lb, r: self.content_stack.set_visible_child_name(r.page_id))
        return sidebar
    
    def create_pages(self):
        self.content_stack.add_titled(self.create_dashboard_page(), "dashboard", "Dashboard")
        self.content_stack.add_titled(self.create_games_page(), "games", "Games")
        self.content_stack.add_titled(self.create_optimize_page(), "optimize", "Optimize")
        self.content_stack.add_titled(self.create_performance_page(), "performance", "Performance")
        self.content_stack.add_titled(self.create_tools_page(), "tools", "Tools")
        self.content_stack.add_titled(self.create_stats_page(), "stats", "Stats")
        self.content_stack.add_titled(self.create_settings_page(), "settings", "Settings")
    
    def create_dashboard_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        box.set_margin_top(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        title = Gtk.Label()
        title.set_markup("<span size='xx-large' weight='bold'>🎮 Gaming Dashboard</span>")
        title.set_xalign(0)
        box.pack_start(title, False, False, 0)
        
        self.status_label = Gtk.Label()
        self.update_status()
        box.pack_start(self.status_label, False, False, 10)
        
        quick_frame = Gtk.Frame(label="Quick Launch")
        quick_box = Gtk.Box(spacing=15)
        quick_box.set_margin_top(10)
        quick_box.set_margin_bottom(10)
        quick_box.set_margin_start(10)
        quick_box.set_margin_end(10)
        
        launchers = [
            ("🎮 Steam", "steam"),
            ("🍷 Lutris", "lutris"),
            ("🎯 Heroic", "heroic"),
            ("🎲 ProtonUp", "protonup-qt")
        ]
        
        for name, cmd in launchers:
            btn = Gtk.Button(label=name)
            btn.set_size_request(120, 60)
            btn.connect("clicked", lambda x, c=cmd: subprocess.Popen([c]))
            quick_box.pack_start(btn, False, False, 0)
        
        quick_frame.add(quick_box)
        box.pack_start(quick_frame, False, False, 0)
        
        perf_frame = Gtk.Frame(label="System Performance")
        perf_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        perf_box.set_margin_top(10)
        perf_box.set_margin_bottom(10)
        perf_box.set_margin_start(10)
        perf_box.set_margin_end(10)
        
        self.cpu_bar = Gtk.ProgressBar()
        self.cpu_bar.set_text("CPU: 0%")
        self.cpu_bar.set_show_text(True)
        perf_box.pack_start(self.cpu_bar, False, False, 0)
        
        self.gpu_bar = Gtk.ProgressBar()
        self.gpu_bar.set_text("GPU: 0%")
        self.gpu_bar.set_show_text(True)
        perf_box.pack_start(self.gpu_bar, False, False, 0)
        
        self.ram_bar = Gtk.ProgressBar()
        self.ram_bar.set_text("RAM: 0%")
        self.ram_bar.set_show_text(True)
        perf_box.pack_start(self.ram_bar, False, False, 0)
        
        perf_frame.add(perf_box)
        box.pack_start(perf_frame, False, False, 0)
        
        GLib.timeout_add_seconds(2, self.update_performance)
        
        return box
    
    def create_games_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>🎮 My Games Library</span>")
        title.set_xalign(0)
        box.pack_start(title, False, False, 0)
        
        btn_box = Gtk.Box(spacing=10)
        add_btn = Gtk.Button(label="➕ Add Game")
        add_btn.connect("clicked", self.add_game)
        btn_box.pack_start(add_btn, False, False, 0)
        
        scan_btn = Gtk.Button(label="🔍 Scan for Games")
        scan_btn.connect("clicked", self.scan_games)
        btn_box.pack_start(scan_btn, False, False, 0)
        box.pack_start(btn_box, False, False, 0)
        
        scrolled = Gtk.ScrolledWindow()
        self.games_flow = Gtk.FlowBox()
        self.games_flow.set_max_children_per_line(4)
        self.games_flow.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled.add(self.games_flow)
        box.pack_start(scrolled, True, True, 0)
        
        return box
    
    def create_optimize_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>⚡ Gaming Optimizations</span>")
        title.set_xalign(0)
        box.pack_start(title, False, False, 0)
        
        optimizations = [
            ("🚀 Enable GameMode", "Optimize CPU and GPU for gaming", True),
            ("📊 MangoHud Overlay", "Show FPS and system stats", True),
            ("🔧 Performance Governor", "Set CPU to max performance", True),
            ("💾 Disable Swap", "Reduce latency by disabling swap", False),
            ("🖥️ Disable Compositor", "Reduce input lag", False),
            ("🔇 Disable Notifications", "No interruptions while gaming", True),
            ("🌙 Night Light Off", "Disable blue light filter", True),
            ("⚡ High Priority", "Run games with high process priority", True),
            ("🔌 Disable Power Saving", "Keep system at full power", True),
            ("🎯 CPU Pinning", "Pin game to specific CPU cores", False)
        ]
        
        for name, desc, default in optimizations:
            hbox = Gtk.Box(spacing=10)
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            
            label = Gtk.Label(label=name)
            label.set_xalign(0)
            vbox.pack_start(label, False, False, 0)
            
            desc_label = Gtk.Label(label=desc)
            desc_label.set_xalign(0)
            desc_label.get_style_context().add_class("dim-label")
            vbox.pack_start(desc_label, False, False, 0)
            
            hbox.pack_start(vbox, True, True, 0)
            
            switch = Gtk.Switch()
            switch.set_active(default)
            switch.set_valign(Gtk.Align.CENTER)
            hbox.pack_start(switch, False, False, 0)
            
            box.pack_start(hbox, False, False, 5)
        
        apply_btn = Gtk.Button(label="✅ Apply All Optimizations")
        apply_btn.connect("clicked", self.apply_optimizations)
        box.pack_start(apply_btn, False, False, 10)
        
        return box
    
    def create_performance_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>🖥️ Performance Monitor</span>")
        title.set_xalign(0)
        box.pack_start(title, False, False, 0)
        
        grid = Gtk.Grid()
        grid.set_column_spacing(20)
        grid.set_row_spacing(10)
        
        metrics = [
            ("CPU Usage", "0%"),
            ("CPU Temp", "0°C"),
            ("GPU Usage", "0%"),
            ("GPU Temp", "0°C"),
            ("VRAM Used", "0 MB"),
            ("RAM Used", "0 MB"),
            ("FPS (avg)", "0"),
            ("Frame Time", "0 ms")
        ]
        
        for i, (name, val) in enumerate(metrics):
            row, col = divmod(i, 2)
            frame = Gtk.Frame(label=name)
            frame.set_size_request(200, 80)
            label = Gtk.Label(label=val)
            label.set_margin_top(10)
            label.set_margin_bottom(10)
            frame.add(label)
            grid.attach(frame, col, row, 1, 1)
        
        box.pack_start(grid, False, False, 10)
        
        return box
    
    def create_tools_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>🛠️ Gaming Tools</span>")
        title.set_xalign(0)
        box.pack_start(title, False, False, 0)
        
        tools = [
            ("🍷 Wine Configuration", "winecfg"),
            ("🔧 Winetricks", "winetricks"),
            ("📦 ProtonUp-Qt", "protonup-qt"),
            ("🎮 Steam", "steam"),
            ("🎯 Lutris", "lutris"),
            ("📊 MangoHud Config", "goverlay"),
            ("🖥️ GPU Monitor (NVIDIA)", "nvidia-settings"),
            ("🖥️ GPU Monitor (AMD)", "corectrl"),
            ("🎮 Controller Config", "sc-controller"),
            ("🔊 Audio Config", "pavucontrol")
        ]
        
        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)
        
        for i, (name, cmd) in enumerate(tools):
            row, col = divmod(i, 3)
            btn = Gtk.Button(label=name)
            btn.set_size_request(180, 50)
            btn.connect("clicked", lambda x, c=cmd: subprocess.Popen([c]))
            grid.attach(btn, col, row, 1, 1)
        
        box.pack_start(grid, False, False, 0)
        
        return box
    
    def create_stats_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>📊 Gaming Statistics</span>")
        title.set_xalign(0)
        box.pack_start(title, False, False, 0)
        
        stats = [
            ("Total Play Time", "0 hours"),
            ("Games Played", "0"),
            ("Most Played", "None"),
            ("Avg FPS", "0"),
            ("Gaming Sessions", "0")
        ]
        
        for name, val in stats:
            hbox = Gtk.Box(spacing=10)
            label = Gtk.Label(label=name + ":")
            label.set_xalign(0)
            hbox.pack_start(label, False, False, 0)
            val_label = Gtk.Label(label=val)
            hbox.pack_start(val_label, False, False, 0)
            box.pack_start(hbox, False, False, 5)
        
        return box
    
    def create_settings_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>⚙️ Game Center Settings</span>")
        title.set_xalign(0)
        box.pack_start(title, False, False, 0)
        
        settings = [
            ("Auto-enable Gaming Mode when launching games", True),
            ("Show FPS overlay by default", True),
            ("Notify when game updates available", True),
            ("Auto-scan for new games", True),
            ("Sync saves to cloud", False),
            ("Record gameplay (last 5 minutes)", False)
        ]
        
        for name, default in settings:
            hbox = Gtk.Box(spacing=10)
            label = Gtk.Label(label=name)
            label.set_xalign(0)
            hbox.pack_start(label, True, True, 0)
            switch = Gtk.Switch()
            switch.set_active(default)
            hbox.pack_start(switch, False, False, 0)
            box.pack_start(hbox, False, False, 5)
        
        return box
    
    def toggle_gaming_mode(self, button):
        self.config["gaming_mode"] = not self.config.get("gaming_mode", False)
        self.save_config()
        self.update_status()
        
        if self.config["gaming_mode"]:
            subprocess.Popen(["gamemoded", "-r"])
        
    def update_status(self):
        if self.config.get("gaming_mode", False):
            self.status_label.set_markup("<span size='large' color='#4CAF50'>⚡ Gaming Mode: ACTIVE</span>")
        else:
            self.status_label.set_markup("<span size='large' color='#888'>💤 Gaming Mode: OFF</span>")
    
    def update_performance(self):
        try:
            import psutil
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory()
            self.cpu_bar.set_fraction(cpu / 100)
            self.cpu_bar.set_text(f"CPU: {cpu:.0f}%")
            self.ram_bar.set_fraction(mem.percent / 100)
            self.ram_bar.set_text(f"RAM: {mem.percent:.0f}%")
        except:
            pass
        return True
    
    def add_game(self, button):
        dialog = Gtk.FileChooserDialog(title="Select Game", parent=self,
                                        action=Gtk.FileChooserAction.OPEN)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                          Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            game_path = dialog.get_filename()
            self.config.setdefault("games", []).append(game_path)
            self.save_config()
        dialog.destroy()
    
    def scan_games(self, button):
        dialog = Gtk.MessageDialog(transient_for=self, message_type=Gtk.MessageType.INFO,
                                   buttons=Gtk.ButtonsType.OK, text="Scanning...")
        dialog.format_secondary_text("Scanning for installed games...")
        dialog.run()
        dialog.destroy()
    
    def apply_optimizations(self, button):
        subprocess.run(["/usr/share/muxos/optimizations/gaming-tweaks.sh"])
        dialog = Gtk.MessageDialog(transient_for=self, message_type=Gtk.MessageType.INFO,
                                   buttons=Gtk.ButtonsType.OK, text="Applied!")
        dialog.format_secondary_text("Gaming optimizations applied successfully!")
        dialog.run()
        dialog.destroy()

if __name__ == "__main__":
    win = GameCenter()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
