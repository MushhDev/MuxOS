#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import subprocess
import os

class MuxOSControlPanel(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="MuxOS Control Panel")
        self.set_default_size(900, 600)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = "MuxOS Control Panel"
        header.props.subtitle = "System Settings"
        self.set_titlebar(header)
        
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.add(main_box)
        
        sidebar = self.create_sidebar()
        main_box.pack_start(sidebar, False, False, 0)
        
        separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        main_box.pack_start(separator, False, False, 0)
        
        self.content_stack = Gtk.Stack()
        self.content_stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        main_box.pack_start(self.content_stack, True, True, 10)
        
        self.create_pages()
        
    def create_sidebar(self):
        sidebar = Gtk.ListBox()
        sidebar.set_size_request(200, -1)
        
        categories = [
            ("System", "computer"),
            ("Display", "video-display"),
            ("Network", "network-wireless"),
            ("Sound", "audio-card"),
            ("Gaming", "applications-games"),
            ("Performance", "utilities-system-monitor"),
            ("Drivers", "drive-harddisk"),
            ("Updates", "system-software-update"),
            ("About", "help-about")
        ]
        
        for name, icon in categories:
            row = Gtk.ListBoxRow()
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            row.add(hbox)
            
            icon_widget = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.BUTTON)
            hbox.pack_start(icon_widget, False, False, 10)
            
            label = Gtk.Label(label=name)
            label.set_xalign(0)
            hbox.pack_start(label, True, True, 0)
            
            sidebar.add(row)
        
        sidebar.connect("row-activated", self.on_sidebar_row_activated)
        return sidebar
    
    def create_pages(self):
        self.content_stack.add_titled(self.create_system_page(), "system", "System")
        self.content_stack.add_titled(self.create_display_page(), "display", "Display")
        self.content_stack.add_titled(self.create_network_page(), "network", "Network")
        self.content_stack.add_titled(self.create_sound_page(), "sound", "Sound")
        self.content_stack.add_titled(self.create_gaming_page(), "gaming", "Gaming")
        self.content_stack.add_titled(self.create_performance_page(), "performance", "Performance")
        self.content_stack.add_titled(self.create_drivers_page(), "drivers", "Drivers")
        self.content_stack.add_titled(self.create_updates_page(), "updates", "Updates")
        self.content_stack.add_titled(self.create_about_page(), "about", "About")
    
    def create_system_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>System Settings</span>")
        title.set_xalign(0)
        box.pack_start(title, False, False, 0)
        
        hostname_box = self.create_setting_row("Hostname", "muxos-pc", self.on_hostname_changed)
        box.pack_start(hostname_box, False, False, 0)
        
        timezone_box = self.create_combo_row("Timezone", ["UTC", "America/New_York", "Europe/London", "Asia/Tokyo"])
        box.pack_start(timezone_box, False, False, 0)
        
        autologin_box = self.create_switch_row("Auto Login", False, self.on_autologin_toggled)
        box.pack_start(autologin_box, False, False, 0)
        
        return box
    
    def create_display_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>Display Settings</span>")
        title.set_xalign(0)
        box.pack_start(title, False, False, 0)
        
        resolution_box = self.create_combo_row("Resolution", ["1920x1080", "2560x1440", "3840x2160"])
        box.pack_start(resolution_box, False, False, 0)
        
        refresh_box = self.create_combo_row("Refresh Rate", ["60 Hz", "75 Hz", "144 Hz", "240 Hz"])
        box.pack_start(refresh_box, False, False, 0)
        
        compositor_box = self.create_switch_row("Enable Compositor", True, None)
        box.pack_start(compositor_box, False, False, 0)
        
        vsync_box = self.create_switch_row("VSync", True, None)
        box.pack_start(vsync_box, False, False, 0)
        
        return box
    
    def create_network_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>Network Settings</span>")
        title.set_xalign(0)
        box.pack_start(title, False, False, 0)
        
        btn = Gtk.Button(label="Open Network Manager")
        btn.connect("clicked", lambda x: subprocess.Popen(["nm-connection-editor"]))
        box.pack_start(btn, False, False, 0)
        
        return box
    
    def create_sound_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>Sound Settings</span>")
        title.set_xalign(0)
        box.pack_start(title, False, False, 0)
        
        btn = Gtk.Button(label="Open Volume Control")
        btn.connect("clicked", lambda x: subprocess.Popen(["pavucontrol"]))
        box.pack_start(btn, False, False, 0)
        
        return box
    
    def create_gaming_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>Gaming Optimizations</span>")
        title.set_xalign(0)
        box.pack_start(title, False, False, 0)
        
        gamemode_box = self.create_switch_row("Enable GameMode", True, None)
        box.pack_start(gamemode_box, False, False, 0)
        
        mangohud_box = self.create_switch_row("Enable MangoHud", True, None)
        box.pack_start(mangohud_box, False, False, 0)
        
        fsync_box = self.create_switch_row("Enable Fsync (Wine)", True, None)
        box.pack_start(fsync_box, False, False, 0)
        
        esync_box = self.create_switch_row("Enable Esync (Wine)", True, None)
        box.pack_start(esync_box, False, False, 0)
        
        return box
    
    def create_performance_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>Performance Settings</span>")
        title.set_xalign(0)
        box.pack_start(title, False, False, 0)
        
        cpu_gov_box = self.create_combo_row("CPU Governor", ["performance", "powersave", "ondemand", "schedutil"])
        box.pack_start(cpu_gov_box, False, False, 0)
        
        zram_box = self.create_switch_row("Enable ZRAM", True, None)
        box.pack_start(zram_box, False, False, 0)
        
        swappiness_box = self.create_scale_row("Swappiness", 10, 0, 100)
        box.pack_start(swappiness_box, False, False, 0)
        
        return box
    
    def create_drivers_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>Hardware Drivers</span>")
        title.set_xalign(0)
        box.pack_start(title, False, False, 0)
        
        nvidia_btn = Gtk.Button(label="Install NVIDIA Drivers")
        nvidia_btn.connect("clicked", self.install_nvidia_drivers)
        box.pack_start(nvidia_btn, False, False, 0)
        
        amd_btn = Gtk.Button(label="Install AMD Drivers")
        amd_btn.connect("clicked", self.install_amd_drivers)
        box.pack_start(amd_btn, False, False, 0)
        
        return box
    
    def create_updates_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>System Updates</span>")
        title.set_xalign(0)
        box.pack_start(title, False, False, 0)
        
        check_btn = Gtk.Button(label="Check for Updates")
        check_btn.connect("clicked", self.check_updates)
        box.pack_start(check_btn, False, False, 0)
        
        return box
    
    def create_about_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        title = Gtk.Label()
        title.set_markup("<span size='xx-large' weight='bold'>MuxOS</span>")
        box.pack_start(title, False, False, 10)
        
        version = Gtk.Label(label="Version 1.0 - Velocity")
        box.pack_start(version, False, False, 0)
        
        desc = Gtk.Label(label="A lightweight, gaming-optimized operating system")
        box.pack_start(desc, False, False, 0)
        
        return box
    
    def create_setting_row(self, label_text, default_value, callback):
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        label = Gtk.Label(label=label_text)
        label.set_xalign(0)
        label.set_size_request(150, -1)
        hbox.pack_start(label, False, False, 0)
        
        entry = Gtk.Entry()
        entry.set_text(default_value)
        if callback:
            entry.connect("changed", callback)
        hbox.pack_start(entry, True, True, 0)
        
        return hbox
    
    def create_combo_row(self, label_text, options):
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        label = Gtk.Label(label=label_text)
        label.set_xalign(0)
        label.set_size_request(150, -1)
        hbox.pack_start(label, False, False, 0)
        
        combo = Gtk.ComboBoxText()
        for option in options:
            combo.append_text(option)
        combo.set_active(0)
        hbox.pack_start(combo, True, True, 0)
        
        return hbox
    
    def create_switch_row(self, label_text, default_state, callback):
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        label = Gtk.Label(label=label_text)
        label.set_xalign(0)
        hbox.pack_start(label, True, True, 0)
        
        switch = Gtk.Switch()
        switch.set_active(default_state)
        if callback:
            switch.connect("notify::active", callback)
        hbox.pack_start(switch, False, False, 0)
        
        return hbox
    
    def create_scale_row(self, label_text, default_value, min_val, max_val):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        
        label = Gtk.Label(label=label_text)
        label.set_xalign(0)
        vbox.pack_start(label, False, False, 0)
        
        scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, min_val, max_val, 1)
        scale.set_value(default_value)
        scale.set_draw_value(True)
        vbox.pack_start(scale, False, False, 0)
        
        return vbox
    
    def on_sidebar_row_activated(self, listbox, row):
        index = row.get_index()
        pages = ["system", "display", "network", "sound", "gaming", "performance", "drivers", "updates", "about"]
        if index < len(pages):
            self.content_stack.set_visible_child_name(pages[index])
    
    def on_hostname_changed(self, entry):
        pass
    
    def on_autologin_toggled(self, switch, gparam):
        pass
    
    def install_nvidia_drivers(self, button):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="NVIDIA Driver Installation",
        )
        dialog.format_secondary_text("This will install the latest NVIDIA drivers. Requires root privileges.")
        dialog.run()
        dialog.destroy()
    
    def install_amd_drivers(self, button):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="AMD Driver Installation",
        )
        dialog.format_secondary_text("AMD drivers are included by default. Mesa drivers are already installed.")
        dialog.run()
        dialog.destroy()
    
    def check_updates(self, button):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="System Updates",
        )
        dialog.format_secondary_text("Checking for updates...")
        dialog.run()
        dialog.destroy()

if __name__ == "__main__":
    win = MuxOSControlPanel()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
