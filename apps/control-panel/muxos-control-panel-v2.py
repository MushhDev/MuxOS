#!/usr/bin/env python3
"""MuxOS Control Panel v2 - Complete system settings with Work/Gaming modes"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk
import subprocess
import os
import json

class ControlPanelV2(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="MuxOS Control Panel")
        self.set_default_size(1100, 750)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        self.config_file = os.path.expanduser("~/.config/muxos/settings.json")
        self.load_config()
        
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = "⚙️ Control Panel"
        self.set_titlebar(header)
        
        mode_box = Gtk.Box(spacing=5)
        self.work_btn = Gtk.ToggleButton(label="💼 Work")
        self.work_btn.connect("toggled", self.on_work_mode)
        mode_box.pack_start(self.work_btn, False, False, 0)
        
        self.game_btn = Gtk.ToggleButton(label="🎮 Gaming")
        self.game_btn.connect("toggled", self.on_gaming_mode)
        mode_box.pack_start(self.game_btn, False, False, 0)
        header.pack_end(mode_box)
        
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.add(main_box)
        
        sidebar = self.create_sidebar()
        main_box.pack_start(sidebar, False, False, 0)
        
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        main_box.pack_start(self.stack, True, True, 10)
        
        self.create_all_pages()
    
    def load_config(self):
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            if os.path.exists(self.config_file):
                with open(self.config_file) as f:
                    self.config = json.load(f)
            else:
                self.config = {"mode": "normal", "theme": "dark"}
                self.save_config()
        except:
            self.config = {}
    
    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def create_sidebar(self):
        sidebar = Gtk.ListBox()
        sidebar.set_size_request(220, -1)
        
        categories = [
            ("🏠 Overview", "overview"),
            ("🖥️ Display", "display"),
            ("🔊 Sound", "sound"),
            ("🌐 Network", "network"),
            ("⌨️ Keyboard", "keyboard"),
            ("🖱️ Mouse", "mouse"),
            ("🔋 Power", "power"),
            ("👤 Users", "users"),
            ("📅 Date & Time", "datetime"),
            ("🌍 Region", "region"),
            ("🎨 Appearance", "appearance"),
            ("🔔 Notifications", "notifications"),
            ("🔒 Privacy", "privacy"),
            ("♿ Accessibility", "accessibility"),
            ("🎮 Gaming", "gaming"),
            ("💼 Productivity", "productivity"),
            ("🔧 Advanced", "advanced"),
            ("ℹ️ About", "about")
        ]
        
        for name, page_id in categories:
            row = Gtk.ListBoxRow()
            row.page_id = page_id
            label = Gtk.Label(label=name)
            label.set_xalign(0)
            label.set_margin_start(10)
            label.set_margin_top(8)
            label.set_margin_bottom(8)
            row.add(label)
            sidebar.add(row)
        
        sidebar.connect("row-activated", lambda lb, r: self.stack.set_visible_child_name(r.page_id))
        return sidebar
    
    def create_all_pages(self):
        self.stack.add_titled(self.create_overview_page(), "overview", "Overview")
        self.stack.add_titled(self.create_display_page(), "display", "Display")
        self.stack.add_titled(self.create_sound_page(), "sound", "Sound")
        self.stack.add_titled(self.create_network_page(), "network", "Network")
        self.stack.add_titled(self.create_keyboard_page(), "keyboard", "Keyboard")
        self.stack.add_titled(self.create_mouse_page(), "mouse", "Mouse")
        self.stack.add_titled(self.create_power_page(), "power", "Power")
        self.stack.add_titled(self.create_users_page(), "users", "Users")
        self.stack.add_titled(self.create_datetime_page(), "datetime", "Date & Time")
        self.stack.add_titled(self.create_region_page(), "region", "Region")
        self.stack.add_titled(self.create_appearance_page(), "appearance", "Appearance")
        self.stack.add_titled(self.create_notifications_page(), "notifications", "Notifications")
        self.stack.add_titled(self.create_privacy_page(), "privacy", "Privacy")
        self.stack.add_titled(self.create_accessibility_page(), "accessibility", "Accessibility")
        self.stack.add_titled(self.create_gaming_page(), "gaming", "Gaming")
        self.stack.add_titled(self.create_productivity_page(), "productivity", "Productivity")
        self.stack.add_titled(self.create_advanced_page(), "advanced", "Advanced")
        self.stack.add_titled(self.create_about_page(), "about", "About")
    
    def create_section(self, title):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        label = Gtk.Label()
        label.set_markup(f"<span size='large' weight='bold'>{title}</span>")
        label.set_xalign(0)
        box.pack_start(label, False, False, 0)
        return box
    
    def add_switch_row(self, box, label_text, default=True, callback=None):
        hbox = Gtk.Box(spacing=10)
        label = Gtk.Label(label=label_text)
        label.set_xalign(0)
        hbox.pack_start(label, True, True, 0)
        switch = Gtk.Switch()
        switch.set_active(default)
        if callback:
            switch.connect("notify::active", callback)
        hbox.pack_start(switch, False, False, 0)
        box.pack_start(hbox, False, False, 5)
        return switch
    
    def add_combo_row(self, box, label_text, options, default=0):
        hbox = Gtk.Box(spacing=10)
        label = Gtk.Label(label=label_text)
        label.set_xalign(0)
        hbox.pack_start(label, True, True, 0)
        combo = Gtk.ComboBoxText()
        for opt in options:
            combo.append_text(opt)
        combo.set_active(default)
        hbox.pack_start(combo, False, False, 0)
        box.pack_start(hbox, False, False, 5)
        return combo
    
    def add_scale_row(self, box, label_text, min_val, max_val, default):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        label = Gtk.Label(label=label_text)
        label.set_xalign(0)
        vbox.pack_start(label, False, False, 0)
        scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, min_val, max_val, 1)
        scale.set_value(default)
        scale.set_draw_value(True)
        vbox.pack_start(scale, False, False, 0)
        box.pack_start(vbox, False, False, 5)
        return scale
    
    def create_overview_page(self):
        box = self.create_section("🏠 System Overview")
        
        grid = Gtk.Grid()
        grid.set_column_spacing(20)
        grid.set_row_spacing(15)
        
        quick_settings = [
            ("🖥️ Display", "display"),
            ("🔊 Sound", "sound"),
            ("🌐 Network", "network"),
            ("🔋 Power", "power"),
            ("🎨 Appearance", "appearance"),
            ("🔒 Privacy", "privacy"),
            ("🎮 Gaming", "gaming"),
            ("🔄 Updates", "updates")
        ]
        
        for i, (name, action) in enumerate(quick_settings):
            row, col = divmod(i, 4)
            btn = Gtk.Button(label=name)
            btn.set_size_request(150, 80)
            if action == "updates":
                btn.connect("clicked", lambda x: subprocess.Popen(["muxos-updater"]))
            else:
                btn.connect("clicked", lambda x, a=action: self.stack.set_visible_child_name(a))
            grid.attach(btn, col, row, 1, 1)
        
        box.pack_start(grid, False, False, 20)
        
        info_frame = Gtk.Frame(label="System Information")
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        info_box.set_margin_top(10)
        info_box.set_margin_bottom(10)
        info_box.set_margin_start(10)
        info_box.set_margin_end(10)
        
        try:
            import platform
            info = [
                f"OS: MuxOS 1.0 (Velocity)",
                f"Kernel: {platform.release()}",
                f"Architecture: {platform.machine()}",
                f"Hostname: {platform.node()}"
            ]
        except:
            info = ["OS: MuxOS 1.0"]
        
        for line in info:
            label = Gtk.Label(label=line)
            label.set_xalign(0)
            info_box.pack_start(label, False, False, 0)
        
        info_frame.add(info_box)
        box.pack_start(info_frame, False, False, 0)
        
        return box
    
    def create_display_page(self):
        box = self.create_section("🖥️ Display Settings")
        
        self.add_combo_row(box, "Resolution", ["1920x1080", "2560x1440", "3840x2160", "1366x768"], 0)
        self.add_combo_row(box, "Refresh Rate", ["60 Hz", "75 Hz", "120 Hz", "144 Hz", "165 Hz", "240 Hz"], 0)
        self.add_combo_row(box, "Scaling", ["100%", "125%", "150%", "175%", "200%"], 0)
        self.add_scale_row(box, "Brightness", 0, 100, 80)
        self.add_switch_row(box, "Night Light (Blue Light Filter)", False)
        self.add_switch_row(box, "Enable VSync", True)
        self.add_switch_row(box, "Enable Compositor", True)
        self.add_switch_row(box, "Variable Refresh Rate (FreeSync/G-Sync)", True)
        
        btn = Gtk.Button(label="🖥️ Configure Multiple Displays")
        btn.connect("clicked", lambda x: subprocess.Popen(["arandr"]))
        box.pack_start(btn, False, False, 10)
        
        return box
    
    def create_sound_page(self):
        box = self.create_section("🔊 Sound Settings")
        
        self.add_scale_row(box, "Master Volume", 0, 100, 80)
        self.add_combo_row(box, "Output Device", ["Built-in Speakers", "HDMI", "USB Headset"], 0)
        self.add_combo_row(box, "Input Device", ["Built-in Microphone", "USB Microphone"], 0)
        self.add_switch_row(box, "Enable System Sounds", True)
        self.add_switch_row(box, "Low Latency Audio (Gaming)", True)
        
        btn = Gtk.Button(label="🔊 Open PulseAudio Volume Control")
        btn.connect("clicked", lambda x: subprocess.Popen(["pavucontrol"]))
        box.pack_start(btn, False, False, 10)
        
        return box
    
    def create_network_page(self):
        box = self.create_section("🌐 Network Settings")
        
        self.add_switch_row(box, "Enable Wi-Fi", True)
        self.add_switch_row(box, "Enable Bluetooth", True)
        self.add_switch_row(box, "Enable Airplane Mode", False)
        
        btn_box = Gtk.Box(spacing=10)
        wifi_btn = Gtk.Button(label="📶 Wi-Fi Settings")
        wifi_btn.connect("clicked", lambda x: subprocess.Popen(["nm-connection-editor"]))
        btn_box.pack_start(wifi_btn, False, False, 0)
        
        bt_btn = Gtk.Button(label="🔵 Bluetooth Settings")
        bt_btn.connect("clicked", lambda x: subprocess.Popen(["blueman-manager"]))
        btn_box.pack_start(bt_btn, False, False, 0)
        
        box.pack_start(btn_box, False, False, 10)
        
        return box
    
    def create_keyboard_page(self):
        box = self.create_section("⌨️ Keyboard Settings")
        
        self.add_combo_row(box, "Keyboard Layout", ["US", "UK", "Spanish", "German", "French"], 0)
        self.add_scale_row(box, "Key Repeat Delay (ms)", 100, 1000, 300)
        self.add_scale_row(box, "Key Repeat Rate", 10, 50, 30)
        self.add_switch_row(box, "Num Lock on Startup", True)
        self.add_switch_row(box, "Caps Lock Warning", True)
        
        btn = Gtk.Button(label="⌨️ Configure Keyboard Shortcuts")
        box.pack_start(btn, False, False, 10)
        
        return box
    
    def create_mouse_page(self):
        box = self.create_section("🖱️ Mouse & Touchpad")
        
        self.add_scale_row(box, "Pointer Speed", 1, 10, 5)
        self.add_switch_row(box, "Natural Scrolling", False)
        self.add_switch_row(box, "Tap to Click (Touchpad)", True)
        self.add_combo_row(box, "Primary Button", ["Left", "Right"], 0)
        self.add_scale_row(box, "Double-Click Speed", 100, 800, 400)
        self.add_switch_row(box, "Mouse Acceleration", True)
        self.add_scale_row(box, "Polling Rate", 125, 1000, 500)
        
        return box
    
    def create_power_page(self):
        box = self.create_section("🔋 Power Management")
        
        self.add_combo_row(box, "Power Profile", ["Performance", "Balanced", "Power Saver"], 0)
        self.add_combo_row(box, "When Lid is Closed", ["Suspend", "Hibernate", "Nothing", "Shutdown"], 0)
        self.add_combo_row(box, "Turn Off Display After", ["Never", "5 minutes", "10 minutes", "15 minutes", "30 minutes"], 2)
        self.add_switch_row(box, "Dim Screen When Inactive", True)
        self.add_switch_row(box, "Show Battery Percentage", True)
        self.add_switch_row(box, "Disable Screen Blanking (Gaming)", True)
        
        return box
    
    def create_users_page(self):
        box = self.create_section("👤 User Accounts")
        
        frame = Gtk.Frame(label="Current User")
        user_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        user_box.set_margin_top(10)
        user_box.set_margin_bottom(10)
        user_box.set_margin_start(10)
        user_box.set_margin_end(10)
        
        user_label = Gtk.Label(label=f"Username: {os.getenv('USER', 'muxos')}")
        user_label.set_xalign(0)
        user_box.pack_start(user_label, False, False, 0)
        
        btn_box = Gtk.Box(spacing=10)
        passwd_btn = Gtk.Button(label="🔑 Change Password")
        btn_box.pack_start(passwd_btn, False, False, 0)
        
        add_user_btn = Gtk.Button(label="➕ Add User")
        btn_box.pack_start(add_user_btn, False, False, 0)
        
        user_box.pack_start(btn_box, False, False, 0)
        frame.add(user_box)
        box.pack_start(frame, False, False, 0)
        
        self.add_switch_row(box, "Automatic Login", False)
        
        return box
    
    def create_datetime_page(self):
        box = self.create_section("📅 Date & Time")
        
        self.add_switch_row(box, "Set Time Automatically", True)
        self.add_combo_row(box, "Time Zone", ["UTC", "America/New_York", "Europe/London", "Europe/Madrid", "Asia/Tokyo"], 0)
        self.add_switch_row(box, "Use 24-hour Format", True)
        self.add_switch_row(box, "Show Date in Panel", True)
        self.add_switch_row(box, "Show Seconds", False)
        
        return box
    
    def create_region_page(self):
        box = self.create_section("🌍 Region & Language")
        
        self.add_combo_row(box, "Language", ["English (US)", "Spanish", "German", "French", "Portuguese"], 0)
        self.add_combo_row(box, "Region Format", ["United States", "Spain", "Germany", "France", "United Kingdom"], 0)
        self.add_combo_row(box, "First Day of Week", ["Sunday", "Monday"], 1)
        
        return box
    
    def create_appearance_page(self):
        box = self.create_section("🎨 Appearance")
        
        self.add_combo_row(box, "Theme", ["MuxOS Dark", "MuxOS Light", "Adwaita", "Arc", "Dracula"], 0)
        self.add_combo_row(box, "Icon Theme", ["Papirus", "Numix", "Adwaita", "Breeze"], 0)
        self.add_combo_row(box, "Cursor Theme", ["Default", "Breeze", "DMZ", "Bibata"], 0)
        self.add_combo_row(box, "Font", ["Noto Sans 10", "Ubuntu 10", "Roboto 10", "DejaVu Sans 10"], 0)
        
        wallpaper_btn = Gtk.Button(label="🖼️ Change Wallpaper")
        wallpaper_btn.connect("clicked", self.change_wallpaper)
        box.pack_start(wallpaper_btn, False, False, 10)
        
        self.add_switch_row(box, "Enable Desktop Effects", True)
        self.add_scale_row(box, "Window Opacity", 50, 100, 95)
        
        return box
    
    def create_notifications_page(self):
        box = self.create_section("🔔 Notifications")
        
        self.add_switch_row(box, "Enable Notifications", True)
        self.add_switch_row(box, "Show on Lock Screen", False)
        self.add_switch_row(box, "Do Not Disturb Mode", False)
        self.add_combo_row(box, "Notification Position", ["Top Right", "Top Left", "Bottom Right", "Bottom Left"], 0)
        self.add_scale_row(box, "Notification Duration (seconds)", 1, 10, 5)
        self.add_switch_row(box, "Play Sound for Notifications", True)
        
        return box
    
    def create_privacy_page(self):
        box = self.create_section("🔒 Privacy & Security")
        
        self.add_switch_row(box, "Screen Lock", True)
        self.add_combo_row(box, "Lock Screen After", ["1 minute", "5 minutes", "10 minutes", "30 minutes", "Never"], 1)
        self.add_switch_row(box, "Show Notifications on Lock Screen", False)
        self.add_switch_row(box, "Location Services", False)
        self.add_switch_row(box, "Camera Access", True)
        self.add_switch_row(box, "Microphone Access", True)
        self.add_switch_row(box, "Usage Statistics", False)
        
        security_btn = Gtk.Button(label="🛡️ Open Security Center")
        security_btn.connect("clicked", lambda x: subprocess.Popen(["muxos-security-center"]))
        box.pack_start(security_btn, False, False, 10)
        
        return box
    
    def create_accessibility_page(self):
        box = self.create_section("♿ Accessibility")
        
        self.add_switch_row(box, "High Contrast Theme", False)
        self.add_switch_row(box, "Large Text", False)
        self.add_switch_row(box, "Screen Reader", False)
        self.add_switch_row(box, "Visual Alerts", False)
        self.add_switch_row(box, "Sticky Keys", False)
        self.add_switch_row(box, "Slow Keys", False)
        self.add_switch_row(box, "Bounce Keys", False)
        self.add_switch_row(box, "Mouse Keys", False)
        self.add_scale_row(box, "Cursor Size", 24, 96, 24)
        
        return box
    
    def create_gaming_page(self):
        box = self.create_section("🎮 Gaming Settings")
        
        self.add_switch_row(box, "Enable GameMode", True)
        self.add_switch_row(box, "MangoHud FPS Overlay", True)
        self.add_switch_row(box, "Performance CPU Governor", True)
        self.add_switch_row(box, "Disable Compositor for Games", True)
        self.add_switch_row(box, "Disable Notifications While Gaming", True)
        self.add_switch_row(box, "Mouse Raw Input", True)
        self.add_combo_row(box, "GPU Power Profile", ["Auto", "Low", "Medium", "High", "Peak"], 3)
        
        btn_box = Gtk.Box(spacing=10)
        game_center_btn = Gtk.Button(label="🎮 Game Center")
        game_center_btn.connect("clicked", lambda x: subprocess.Popen(["muxos-game-center"]))
        btn_box.pack_start(game_center_btn, False, False, 0)
        
        optimize_btn = Gtk.Button(label="⚡ Apply Gaming Optimizations")
        optimize_btn.connect("clicked", lambda x: subprocess.run(["/usr/share/muxos/optimizations/gaming-tweaks.sh"]))
        btn_box.pack_start(optimize_btn, False, False, 0)
        
        box.pack_start(btn_box, False, False, 10)
        
        return box
    
    def create_productivity_page(self):
        box = self.create_section("💼 Productivity Settings")
        
        self.add_switch_row(box, "Focus Mode (Block Distractions)", False)
        self.add_switch_row(box, "Auto-save Documents", True)
        self.add_switch_row(box, "Recent Files Tracking", True)
        self.add_combo_row(box, "Default Browser", ["Firefox", "Chromium", "Brave"], 0)
        self.add_combo_row(box, "Default Email Client", ["Thunderbird", "Evolution", "Geary"], 0)
        self.add_combo_row(box, "Default Office Suite", ["LibreOffice", "OnlyOffice", "WPS Office"], 0)
        
        self.add_switch_row(box, "Cloud Sync (Nextcloud)", False)
        self.add_switch_row(box, "Calendar Integration", True)
        
        return box
    
    def create_advanced_page(self):
        box = self.create_section("🔧 Advanced Settings")
        
        btn_list = [
            ("🖥️ Terminal", "xfce4-terminal"),
            ("📊 System Monitor", "muxos-monitor"),
            ("💾 Disk Manager", "muxos-disk-manager"),
            ("🔐 Security Center", "muxos-security-center"),
            ("🔄 Update Center", "muxos-updater"),
            ("📋 Startup Applications", "lxsession-edit"),
            ("🔧 Services Manager", "systemctl --user"),
            ("📝 Config Editor", "dconf-editor")
        ]
        
        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)
        
        for i, (name, cmd) in enumerate(btn_list):
            row, col = divmod(i, 2)
            btn = Gtk.Button(label=name)
            btn.set_size_request(200, 40)
            btn.connect("clicked", lambda x, c=cmd: subprocess.Popen([c]))
            grid.attach(btn, col, row, 1, 1)
        
        box.pack_start(grid, False, False, 10)
        
        self.add_switch_row(box, "Developer Mode", False)
        self.add_switch_row(box, "SSH Server", False)
        self.add_switch_row(box, "Remote Desktop (VNC)", False)
        
        return box
    
    def create_about_page(self):
        box = self.create_section("ℹ️ About MuxOS")
        
        logo = Gtk.Label()
        logo.set_markup("<span size='xx-large'>🎮 MuxOS</span>")
        box.pack_start(logo, False, False, 10)
        
        version = Gtk.Label(label="Version 1.0.0 - Velocity")
        box.pack_start(version, False, False, 0)
        
        desc = Gtk.Label(label="A lightweight, gaming-optimized operating system")
        box.pack_start(desc, False, False, 5)
        
        info = [
            "Based on: Debian GNU/Linux",
            "Desktop: Openbox + Picom",
            "License: MIT / GPL",
            "Website: https://muxos.org"
        ]
        
        for line in info:
            label = Gtk.Label(label=line)
            box.pack_start(label, False, False, 2)
        
        btn_box = Gtk.Box(spacing=10)
        btn_box.set_halign(Gtk.Align.CENTER)
        
        website_btn = Gtk.Button(label="🌐 Website")
        btn_box.pack_start(website_btn, False, False, 0)
        
        github_btn = Gtk.Button(label="📦 GitHub")
        btn_box.pack_start(github_btn, False, False, 0)
        
        box.pack_start(btn_box, False, False, 10)
        
        return box
    
    def on_work_mode(self, button):
        if button.get_active():
            self.game_btn.set_active(False)
            self.config["mode"] = "work"
            self.save_config()
            subprocess.run(["notify-send", "Work Mode Activated", "Distractions minimized"])
    
    def on_gaming_mode(self, button):
        if button.get_active():
            self.work_btn.set_active(False)
            self.config["mode"] = "gaming"
            self.save_config()
            subprocess.Popen(["gamemoded", "-r"])
            subprocess.run(["notify-send", "Gaming Mode Activated", "System optimized for gaming"])
    
    def change_wallpaper(self, button):
        dialog = Gtk.FileChooserDialog(title="Select Wallpaper", parent=self,
                                        action=Gtk.FileChooserAction.OPEN)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                          Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        
        filter_img = Gtk.FileFilter()
        filter_img.set_name("Images")
        filter_img.add_mime_type("image/png")
        filter_img.add_mime_type("image/jpeg")
        dialog.add_filter(filter_img)
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            path = dialog.get_filename()
            subprocess.run(["feh", "--bg-scale", path])
        dialog.destroy()

if __name__ == "__main__":
    win = ControlPanelV2()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
