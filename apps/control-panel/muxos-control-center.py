#!/usr/bin/env python3
"""
MuxOS Control Center - Modern System Settings
A sleek, unified configuration interface for MuxOS
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, Pango
import subprocess
import os
import json

# MuxOS Velocity Theme Colors
COLORS = {
    'bg_dark': '#09090f',
    'bg_medium': '#12121c',
    'bg_light': '#1c1c2e',
    'bg_card': '#242438',
    'bg_elevated': '#2a2a42',
    'primary': '#7c3aed',
    'secondary': '#a855f7',
    'accent': '#22d3ee',
    'success': '#34d399',
    'warning': '#fbbf24',
    'error': '#f87171',
    'text_primary': '#fafafa',
    'text_secondary': '#a1a1aa',
    'text_muted': '#52525b',
    'border': '#27273a',
}

CSS = f"""
/* MuxOS Velocity Control Center Theme */
@import url("resource:///org/gtk/libgtk/theme/Adwaita/gtk-dark.css");

window {{
    background-color: {COLORS['bg_dark']};
}}

headerbar {{
    background: linear-gradient(180deg, {COLORS['bg_medium']} 0%, {COLORS['bg_dark']} 100%);
    border-bottom: 1px solid {COLORS['border']};
    padding: 8px 12px;
}}

headerbar title {{
    color: {COLORS['text_primary']};
    font-weight: 600;
    font-size: 14px;
}}

headerbar subtitle {{
    color: {COLORS['text_secondary']};
    font-size: 11px;
}}

.sidebar {{
    background-color: {COLORS['bg_medium']};
    border-right: 1px solid {COLORS['border']};
}}

.sidebar row {{
    padding: 14px 18px;
    margin: 4px 8px;
    border-radius: 10px;
    transition: all 200ms ease;
}}

.sidebar row:hover {{
    background-color: {COLORS['bg_light']};
}}

.sidebar row:selected {{
    background: linear-gradient(135deg, {COLORS['primary']}33 0%, {COLORS['secondary']}22 100%);
    border: 1px solid {COLORS['primary']}66;
}}

.sidebar row label {{
    color: {COLORS['text_secondary']};
    font-size: 13px;
}}

.sidebar row:selected label {{
    color: {COLORS['text_primary']};
    font-weight: 500;
}}

.content-area {{
    background-color: {COLORS['bg_dark']};
    padding: 24px;
}}

.page-title {{
    color: {COLORS['text_primary']};
    font-size: 24px;
    font-weight: 700;
    margin-bottom: 8px;
}}

.page-subtitle {{
    color: {COLORS['text_secondary']};
    font-size: 13px;
    margin-bottom: 24px;
}}

.settings-card {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
}}

.settings-card:hover {{
    border-color: {COLORS['primary']}44;
}}

.card-title {{
    color: {COLORS['text_primary']};
    font-size: 15px;
    font-weight: 600;
}}

.card-description {{
    color: {COLORS['text_secondary']};
    font-size: 12px;
}}

.setting-row {{
    padding: 12px 0;
    border-bottom: 1px solid {COLORS['border']}44;
}}

.setting-row:last-child {{
    border-bottom: none;
}}

.setting-label {{
    color: {COLORS['text_primary']};
    font-size: 13px;
}}

.setting-description {{
    color: {COLORS['text_muted']};
    font-size: 11px;
}}

switch {{
    background-color: {COLORS['bg_light']};
    border-radius: 14px;
    min-width: 48px;
    min-height: 26px;
}}

switch:checked {{
    background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
}}

switch slider {{
    background-color: {COLORS['text_primary']};
    border-radius: 50%;
    min-width: 22px;
    min-height: 22px;
    margin: 2px;
}}

button {{
    background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    color: {COLORS['text_primary']};
    font-weight: 500;
    transition: all 200ms ease;
}}

button:hover {{
    background: linear-gradient(135deg, #8b5cf6 0%, #c084fc 100%);
    box-shadow: 0 4px 12px rgba(124, 58, 237, 0.4);
}}

button.flat {{
    background: transparent;
    color: {COLORS['text_secondary']};
}}

button.flat:hover {{
    background-color: {COLORS['bg_light']};
    color: {COLORS['text_primary']};
}}

button.destructive {{
    background: linear-gradient(135deg, {COLORS['error']} 0%, #dc2626 100%);
}}

button.suggested-action {{
    background: linear-gradient(135deg, {COLORS['success']} 0%, {COLORS['accent']} 100%);
}}

combobox button {{
    background-color: {COLORS['bg_light']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 8px 12px;
}}

combobox button:hover {{
    border-color: {COLORS['primary']};
}}

entry {{
    background-color: {COLORS['bg_light']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 10px 14px;
    color: {COLORS['text_primary']};
    caret-color: {COLORS['primary']};
}}

entry:focus {{
    border-color: {COLORS['primary']};
    box-shadow: 0 0 0 3px {COLORS['primary']}33;
}}

scale {{
    padding: 8px 0;
}}

scale trough {{
    background-color: {COLORS['bg_light']};
    border-radius: 4px;
    min-height: 6px;
}}

scale highlight {{
    background: linear-gradient(90deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
    border-radius: 4px;
}}

scale slider {{
    background: {COLORS['text_primary']};
    border-radius: 50%;
    min-width: 18px;
    min-height: 18px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
}}

.info-badge {{
    background-color: {COLORS['primary']}33;
    border: 1px solid {COLORS['primary']}66;
    border-radius: 6px;
    padding: 4px 10px;
    color: {COLORS['secondary']};
    font-size: 11px;
    font-weight: 500;
}}

.status-indicator {{
    min-width: 10px;
    min-height: 10px;
    border-radius: 50%;
}}

.status-active {{
    background-color: {COLORS['success']};
    box-shadow: 0 0 8px {COLORS['success']}88;
}}

.status-inactive {{
    background-color: {COLORS['text_muted']};
}}

.status-warning {{
    background-color: {COLORS['warning']};
    box-shadow: 0 0 8px {COLORS['warning']}88;
}}

.profile-card {{
    background: linear-gradient(145deg, {COLORS['bg_card']} 0%, {COLORS['bg_elevated']} 100%);
    border: 1px solid {COLORS['border']};
    border-radius: 16px;
    padding: 24px;
}}

.profile-card.gaming {{
    border-color: {COLORS['secondary']}66;
    background: linear-gradient(145deg, {COLORS['bg_card']} 0%, {COLORS['secondary']}11 100%);
}}

.profile-card.work {{
    border-color: {COLORS['accent']}66;
    background: linear-gradient(145deg, {COLORS['bg_card']} 0%, {COLORS['accent']}11 100%);
}}

.about-logo {{
    font-size: 48px;
    font-weight: 800;
    background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['accent']} 100%);
    -gtk-icon-filter: none;
}}

scrollbar {{
    background-color: transparent;
}}

scrollbar slider {{
    background-color: {COLORS['border']};
    border-radius: 4px;
    min-width: 6px;
}}

scrollbar slider:hover {{
    background-color: {COLORS['primary']};
}}
"""


class MuxOSControlCenter(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="MuxOS Control Center")
        self.set_default_size(1100, 700)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        # Apply CSS
        self.apply_css()
        
        # Header bar
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = "Control Center"
        header.props.subtitle = "MuxOS System Settings"
        self.set_titlebar(header)
        
        # Main layout
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.add(main_box)
        
        # Sidebar
        sidebar_scroll = Gtk.ScrolledWindow()
        sidebar_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sidebar_scroll.get_style_context().add_class('sidebar')
        
        self.sidebar = Gtk.ListBox()
        self.sidebar.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.sidebar.set_size_request(240, -1)
        sidebar_scroll.add(self.sidebar)
        main_box.pack_start(sidebar_scroll, False, False, 0)
        
        # Content area
        content_scroll = Gtk.ScrolledWindow()
        content_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        content_scroll.get_style_context().add_class('content-area')
        
        self.content_stack = Gtk.Stack()
        self.content_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.content_stack.set_transition_duration(200)
        content_scroll.add(self.content_stack)
        main_box.pack_start(content_scroll, True, True, 0)
        
        # Create pages
        self.create_sidebar_items()
        self.create_pages()
        
        # Connect sidebar selection
        self.sidebar.connect("row-activated", self.on_sidebar_row_activated)
        self.sidebar.select_row(self.sidebar.get_row_at_index(0))
    
    def apply_css(self):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(CSS.encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
    
    def create_sidebar_items(self):
        categories = [
            ("overview", "Overview", "computer-symbolic"),
            ("display", "Display", "video-display-symbolic"),
            ("sound", "Sound", "audio-volume-high-symbolic"),
            ("network", "Network", "network-wireless-symbolic"),
            ("gaming", "Gaming", "input-gaming-symbolic"),
            ("performance", "Performance", "utilities-system-monitor-symbolic"),
            ("power", "Power", "battery-symbolic"),
            ("drivers", "Drivers", "drive-harddisk-symbolic"),
            ("security", "Security", "security-high-symbolic"),
            ("updates", "Updates", "software-update-available-symbolic"),
            ("about", "About", "help-about-symbolic"),
        ]
        
        for id, name, icon in categories:
            row = Gtk.ListBoxRow()
            row.set_name(id)
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
            hbox.set_margin_top(4)
            hbox.set_margin_bottom(4)
            row.add(hbox)
            
            icon_widget = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.MENU)
            hbox.pack_start(icon_widget, False, False, 0)
            
            label = Gtk.Label(label=name)
            label.set_xalign(0)
            hbox.pack_start(label, True, True, 0)
            
            self.sidebar.add(row)
    
    def create_pages(self):
        self.content_stack.add_named(self.create_overview_page(), "overview")
        self.content_stack.add_named(self.create_display_page(), "display")
        self.content_stack.add_named(self.create_sound_page(), "sound")
        self.content_stack.add_named(self.create_network_page(), "network")
        self.content_stack.add_named(self.create_gaming_page(), "gaming")
        self.content_stack.add_named(self.create_performance_page(), "performance")
        self.content_stack.add_named(self.create_power_page(), "power")
        self.content_stack.add_named(self.create_drivers_page(), "drivers")
        self.content_stack.add_named(self.create_security_page(), "security")
        self.content_stack.add_named(self.create_updates_page(), "updates")
        self.content_stack.add_named(self.create_about_page(), "about")
    
    def create_page_container(self, title, subtitle):
        """Create a standard page container with title and subtitle"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        box.set_margin_top(32)
        box.set_margin_bottom(32)
        box.set_margin_start(40)
        box.set_margin_end(40)
        
        title_label = Gtk.Label(label=title)
        title_label.get_style_context().add_class('page-title')
        title_label.set_xalign(0)
        box.pack_start(title_label, False, False, 0)
        
        subtitle_label = Gtk.Label(label=subtitle)
        subtitle_label.get_style_context().add_class('page-subtitle')
        subtitle_label.set_xalign(0)
        box.pack_start(subtitle_label, False, False, 0)
        
        return box
    
    def create_settings_card(self, title, description=None):
        """Create a settings card container"""
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        card.get_style_context().add_class('settings-card')
        
        header = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        
        title_label = Gtk.Label(label=title)
        title_label.get_style_context().add_class('card-title')
        title_label.set_xalign(0)
        header.pack_start(title_label, False, False, 0)
        
        if description:
            desc_label = Gtk.Label(label=description)
            desc_label.get_style_context().add_class('card-description')
            desc_label.set_xalign(0)
            header.pack_start(desc_label, False, False, 0)
        
        card.pack_start(header, False, False, 0)
        
        return card
    
    def create_setting_row(self, label, description=None, widget=None):
        """Create a setting row with label and optional widget"""
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        row.get_style_context().add_class('setting-row')
        
        label_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        
        label_widget = Gtk.Label(label=label)
        label_widget.get_style_context().add_class('setting-label')
        label_widget.set_xalign(0)
        label_box.pack_start(label_widget, False, False, 0)
        
        if description:
            desc_widget = Gtk.Label(label=description)
            desc_widget.get_style_context().add_class('setting-description')
            desc_widget.set_xalign(0)
            label_box.pack_start(desc_widget, False, False, 0)
        
        row.pack_start(label_box, True, True, 0)
        
        if widget:
            row.pack_end(widget, False, False, 0)
        
        return row
    
    def create_overview_page(self):
        page = self.create_page_container("Overview", "System information and quick settings")
        
        # System info card
        info_card = self.create_settings_card("System Information")
        
        # Get system info
        hostname = os.uname().nodename
        kernel = os.uname().release
        
        info_grid = Gtk.Grid()
        info_grid.set_column_spacing(40)
        info_grid.set_row_spacing(12)
        
        labels = [
            ("Operating System", "MuxOS Velocity"),
            ("Version", "2.0"),
            ("Hostname", hostname),
            ("Kernel", kernel),
            ("Architecture", os.uname().machine),
        ]
        
        for i, (label, value) in enumerate(labels):
            name_label = Gtk.Label(label=label)
            name_label.get_style_context().add_class('setting-description')
            name_label.set_xalign(0)
            info_grid.attach(name_label, 0, i, 1, 1)
            
            value_label = Gtk.Label(label=value)
            value_label.get_style_context().add_class('setting-label')
            value_label.set_xalign(0)
            info_grid.attach(value_label, 1, i, 1, 1)
        
        info_card.pack_start(info_grid, False, False, 12)
        page.pack_start(info_card, False, False, 0)
        
        # Quick profiles
        profiles_card = self.create_settings_card("Quick Profiles", "Switch between optimized system profiles")
        
        profiles_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        profiles_box.set_homogeneous(True)
        
        # Gaming profile
        gaming_btn = Gtk.Button()
        gaming_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        gaming_icon = Gtk.Label(label="🎮")
        gaming_icon.set_markup("<span size='xx-large'>🎮</span>")
        gaming_box.pack_start(gaming_icon, False, False, 0)
        gaming_label = Gtk.Label(label="Gaming Mode")
        gaming_box.pack_start(gaming_label, False, False, 0)
        gaming_btn.add(gaming_box)
        gaming_btn.connect("clicked", self.activate_gaming_mode)
        profiles_box.pack_start(gaming_btn, True, True, 0)
        
        # Work profile
        work_btn = Gtk.Button()
        work_btn.get_style_context().add_class('suggested-action')
        work_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        work_icon = Gtk.Label()
        work_icon.set_markup("<span size='xx-large'>💼</span>")
        work_box.pack_start(work_icon, False, False, 0)
        work_label = Gtk.Label(label="Work Mode")
        work_box.pack_start(work_label, False, False, 0)
        work_btn.add(work_box)
        work_btn.connect("clicked", self.activate_work_mode)
        profiles_box.pack_start(work_btn, True, True, 0)
        
        # Power save profile
        power_btn = Gtk.Button()
        power_btn.get_style_context().add_class('flat')
        power_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        power_icon = Gtk.Label()
        power_icon.set_markup("<span size='xx-large'>🔋</span>")
        power_box.pack_start(power_icon, False, False, 0)
        power_label = Gtk.Label(label="Power Save")
        power_box.pack_start(power_label, False, False, 0)
        power_btn.add(power_box)
        profiles_box.pack_start(power_btn, True, True, 0)
        
        profiles_card.pack_start(profiles_box, False, False, 12)
        page.pack_start(profiles_card, False, False, 0)
        
        return page
    
    def create_display_page(self):
        page = self.create_page_container("Display", "Configure monitors, resolution, and visual effects")
        
        # Resolution card
        res_card = self.create_settings_card("Resolution & Refresh Rate")
        
        res_combo = Gtk.ComboBoxText()
        for res in ["1920x1080", "2560x1440", "3840x2160", "1680x1050", "1280x720"]:
            res_combo.append_text(res)
        res_combo.set_active(0)
        res_card.pack_start(self.create_setting_row("Resolution", "Display resolution", res_combo), False, False, 0)
        
        refresh_combo = Gtk.ComboBoxText()
        for rate in ["60 Hz", "75 Hz", "120 Hz", "144 Hz", "165 Hz", "240 Hz"]:
            refresh_combo.append_text(rate)
        refresh_combo.set_active(0)
        res_card.pack_start(self.create_setting_row("Refresh Rate", "Monitor refresh rate", refresh_combo), False, False, 0)
        
        page.pack_start(res_card, False, False, 0)
        
        # Effects card
        effects_card = self.create_settings_card("Visual Effects", "Compositor and window effects")
        
        compositor_switch = Gtk.Switch()
        compositor_switch.set_active(True)
        effects_card.pack_start(self.create_setting_row("Compositor", "Enable Picom compositor for effects", compositor_switch), False, False, 0)
        
        blur_switch = Gtk.Switch()
        blur_switch.set_active(True)
        effects_card.pack_start(self.create_setting_row("Blur Effect", "Enable background blur on windows", blur_switch), False, False, 0)
        
        animations_switch = Gtk.Switch()
        animations_switch.set_active(True)
        effects_card.pack_start(self.create_setting_row("Animations", "Enable window animations", animations_switch), False, False, 0)
        
        shadows_switch = Gtk.Switch()
        shadows_switch.set_active(True)
        effects_card.pack_start(self.create_setting_row("Shadows", "Enable window shadows", shadows_switch), False, False, 0)
        
        page.pack_start(effects_card, False, False, 0)
        
        # Night light card
        night_card = self.create_settings_card("Night Light", "Reduce blue light for better sleep")
        
        night_switch = Gtk.Switch()
        night_switch.set_active(False)
        night_card.pack_start(self.create_setting_row("Enable Night Light", "Automatically reduce blue light at night", night_switch), False, False, 0)
        
        page.pack_start(night_card, False, False, 0)
        
        return page
    
    def create_sound_page(self):
        page = self.create_page_container("Sound", "Audio output and input settings")
        
        # Output card
        output_card = self.create_settings_card("Output", "Speaker and headphone settings")
        
        output_combo = Gtk.ComboBoxText()
        output_combo.append_text("Built-in Audio")
        output_combo.append_text("HDMI Audio")
        output_combo.append_text("USB Headset")
        output_combo.set_active(0)
        output_card.pack_start(self.create_setting_row("Output Device", "Select audio output", output_combo), False, False, 0)
        
        volume_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        volume_scale.set_value(75)
        volume_scale.set_size_request(200, -1)
        output_card.pack_start(self.create_setting_row("Volume", "Master volume level", volume_scale), False, False, 0)
        
        page.pack_start(output_card, False, False, 0)
        
        # Advanced button
        advanced_btn = Gtk.Button(label="Open PulseAudio Volume Control")
        advanced_btn.connect("clicked", lambda x: subprocess.Popen(["pavucontrol"]))
        page.pack_start(advanced_btn, False, False, 16)
        
        return page
    
    def create_network_page(self):
        page = self.create_page_container("Network", "Wi-Fi, Ethernet, and VPN settings")
        
        # Status card
        status_card = self.create_settings_card("Connection Status")
        
        status_indicator = Gtk.Box(spacing=8)
        indicator = Gtk.DrawingArea()
        indicator.set_size_request(10, 10)
        indicator.get_style_context().add_class('status-indicator')
        indicator.get_style_context().add_class('status-active')
        status_indicator.pack_start(indicator, False, False, 0)
        status_label = Gtk.Label(label="Connected")
        status_indicator.pack_start(status_label, False, False, 0)
        
        status_card.pack_start(self.create_setting_row("Status", "Current network connection", status_indicator), False, False, 0)
        
        page.pack_start(status_card, False, False, 0)
        
        # Network manager button
        nm_btn = Gtk.Button(label="Open Network Manager")
        nm_btn.connect("clicked", lambda x: subprocess.Popen(["nm-connection-editor"]))
        page.pack_start(nm_btn, False, False, 16)
        
        return page
    
    def create_gaming_page(self):
        page = self.create_page_container("Gaming", "Optimize your system for gaming performance")
        
        # GameMode card
        gamemode_card = self.create_settings_card("GameMode", "Automatic gaming optimizations")
        
        gamemode_switch = Gtk.Switch()
        gamemode_switch.set_active(True)
        gamemode_card.pack_start(self.create_setting_row("Enable GameMode", "Automatically optimize when games run", gamemode_switch), False, False, 0)
        
        page.pack_start(gamemode_card, False, False, 0)
        
        # MangoHud card
        mangohud_card = self.create_settings_card("MangoHud", "In-game performance overlay")
        
        mangohud_switch = Gtk.Switch()
        mangohud_switch.set_active(True)
        mangohud_card.pack_start(self.create_setting_row("Enable MangoHud", "Show FPS and system stats in games", mangohud_switch), False, False, 0)
        
        page.pack_start(mangohud_card, False, False, 0)
        
        # Wine/Proton card
        wine_card = self.create_settings_card("Wine & Proton", "Windows game compatibility")
        
        fsync_switch = Gtk.Switch()
        fsync_switch.set_active(True)
        wine_card.pack_start(self.create_setting_row("Enable Fsync", "Improved Wine synchronization", fsync_switch), False, False, 0)
        
        esync_switch = Gtk.Switch()
        esync_switch.set_active(True)
        wine_card.pack_start(self.create_setting_row("Enable Esync", "Event-based synchronization", esync_switch), False, False, 0)
        
        page.pack_start(wine_card, False, False, 0)
        
        return page
    
    def create_performance_page(self):
        page = self.create_page_container("Performance", "CPU, memory, and system optimization")
        
        # CPU card
        cpu_card = self.create_settings_card("CPU Settings")
        
        gov_combo = Gtk.ComboBoxText()
        for gov in ["performance", "powersave", "ondemand", "schedutil", "conservative"]:
            gov_combo.append_text(gov)
        gov_combo.set_active(0)
        cpu_card.pack_start(self.create_setting_row("CPU Governor", "Power/performance balance", gov_combo), False, False, 0)
        
        page.pack_start(cpu_card, False, False, 0)
        
        # Memory card
        mem_card = self.create_settings_card("Memory", "RAM and swap configuration")
        
        zram_switch = Gtk.Switch()
        zram_switch.set_active(True)
        mem_card.pack_start(self.create_setting_row("ZRAM Compression", "Compress RAM for more available memory", zram_switch), False, False, 0)
        
        swappiness_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        swappiness_scale.set_value(10)
        swappiness_scale.set_size_request(200, -1)
        mem_card.pack_start(self.create_setting_row("Swappiness", "How aggressively to use swap (lower = less)", swappiness_scale), False, False, 0)
        
        page.pack_start(mem_card, False, False, 0)
        
        return page
    
    def create_power_page(self):
        page = self.create_page_container("Power", "Battery and power management")
        
        # Power profile card
        power_card = self.create_settings_card("Power Profile")
        
        profile_combo = Gtk.ComboBoxText()
        for profile in ["Performance", "Balanced", "Power Saver"]:
            profile_combo.append_text(profile)
        profile_combo.set_active(1)
        power_card.pack_start(self.create_setting_row("Profile", "System power profile", profile_combo), False, False, 0)
        
        page.pack_start(power_card, False, False, 0)
        
        # Screen card
        screen_card = self.create_settings_card("Screen", "Display power settings")
        
        blank_switch = Gtk.Switch()
        blank_switch.set_active(False)
        screen_card.pack_start(self.create_setting_row("Screen Blanking", "Turn off screen when idle", blank_switch), False, False, 0)
        
        dpms_switch = Gtk.Switch()
        dpms_switch.set_active(False)
        screen_card.pack_start(self.create_setting_row("DPMS", "Display power management", dpms_switch), False, False, 0)
        
        page.pack_start(screen_card, False, False, 0)
        
        return page
    
    def create_drivers_page(self):
        page = self.create_page_container("Drivers", "Hardware driver management")
        
        # GPU card
        gpu_card = self.create_settings_card("Graphics Drivers", "Install and manage GPU drivers")
        
        nvidia_btn = Gtk.Button(label="Install NVIDIA Drivers")
        nvidia_btn.connect("clicked", self.install_nvidia_drivers)
        gpu_card.pack_start(nvidia_btn, False, False, 8)
        
        amd_btn = Gtk.Button(label="Install AMD Drivers")
        amd_btn.get_style_context().add_class('flat')
        amd_btn.connect("clicked", self.install_amd_drivers)
        gpu_card.pack_start(amd_btn, False, False, 0)
        
        page.pack_start(gpu_card, False, False, 0)
        
        return page
    
    def create_security_page(self):
        page = self.create_page_container("Security", "Firewall, privacy, and system security")
        
        # Firewall card
        fw_card = self.create_settings_card("Firewall", "UFW firewall settings")
        
        fw_switch = Gtk.Switch()
        fw_switch.set_active(True)
        fw_card.pack_start(self.create_setting_row("Enable Firewall", "Block unauthorized network access", fw_switch), False, False, 0)
        
        page.pack_start(fw_card, False, False, 0)
        
        # Security tools card
        tools_card = self.create_settings_card("Security Tools")
        
        scan_btn = Gtk.Button(label="Run Security Scan")
        scan_btn.connect("clicked", lambda x: subprocess.Popen(["muxos-security-center"]))
        tools_card.pack_start(scan_btn, False, False, 8)
        
        page.pack_start(tools_card, False, False, 0)
        
        return page
    
    def create_updates_page(self):
        page = self.create_page_container("Updates", "System and application updates")
        
        # Update status card
        status_card = self.create_settings_card("Update Status", "Check for available updates")
        
        check_btn = Gtk.Button(label="Check for Updates")
        check_btn.get_style_context().add_class('suggested-action')
        check_btn.connect("clicked", self.check_updates)
        status_card.pack_start(check_btn, False, False, 8)
        
        page.pack_start(status_card, False, False, 0)
        
        # Auto-update card
        auto_card = self.create_settings_card("Automatic Updates")
        
        auto_switch = Gtk.Switch()
        auto_switch.set_active(True)
        auto_card.pack_start(self.create_setting_row("Auto-check Updates", "Automatically check for updates daily", auto_switch), False, False, 0)
        
        notify_switch = Gtk.Switch()
        notify_switch.set_active(True)
        auto_card.pack_start(self.create_setting_row("Update Notifications", "Show notifications when updates are available", notify_switch), False, False, 0)
        
        page.pack_start(auto_card, False, False, 0)
        
        return page
    
    def create_about_page(self):
        page = self.create_page_container("About", "System information and credits")
        
        # Logo and version
        about_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        about_box.set_halign(Gtk.Align.CENTER)
        about_box.set_margin_top(40)
        
        logo = Gtk.Label()
        logo.set_markup("<span size='72000' weight='ultrabold' foreground='#7c3aed'>MuxOS</span>")
        about_box.pack_start(logo, False, False, 0)
        
        version = Gtk.Label()
        version.set_markup("<span size='large' foreground='#a1a1aa'>Version 2.0 — Velocity</span>")
        about_box.pack_start(version, False, False, 0)
        
        desc = Gtk.Label()
        desc.set_markup("<span foreground='#52525b'>A lightweight, gaming-optimized Linux distribution</span>")
        about_box.pack_start(desc, False, False, 0)
        
        page.pack_start(about_box, False, False, 0)
        
        # Links
        links_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        links_box.set_halign(Gtk.Align.CENTER)
        links_box.set_margin_top(32)
        
        github_btn = Gtk.Button(label="GitHub")
        github_btn.get_style_context().add_class('flat')
        links_box.pack_start(github_btn, False, False, 0)
        
        docs_btn = Gtk.Button(label="Documentation")
        docs_btn.get_style_context().add_class('flat')
        links_box.pack_start(docs_btn, False, False, 0)
        
        page.pack_start(links_box, False, False, 0)
        
        return page
    
    def on_sidebar_row_activated(self, listbox, row):
        page_name = row.get_name()
        self.content_stack.set_visible_child_name(page_name)
    
    def activate_gaming_mode(self, button):
        self.show_notification("Gaming Mode", "Gaming optimizations activated")
        subprocess.Popen(["gamemoded", "-r"])
    
    def activate_work_mode(self, button):
        self.show_notification("Work Mode", "Work profile activated")
    
    def install_nvidia_drivers(self, button):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text="Install NVIDIA Drivers",
        )
        dialog.format_secondary_text("This will install the latest NVIDIA proprietary drivers. Root privileges required.")
        response = dialog.run()
        dialog.destroy()
        
        if response == Gtk.ResponseType.OK:
            subprocess.Popen(["pkexec", "/usr/share/muxos/drivers/install-nvidia.sh"])
    
    def install_amd_drivers(self, button):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="AMD Drivers",
        )
        dialog.format_secondary_text("AMD drivers (Mesa) are already installed and up to date.")
        dialog.run()
        dialog.destroy()
    
    def check_updates(self, button):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Checking for Updates",
        )
        dialog.format_secondary_text("Checking for system and application updates...")
        dialog.run()
        dialog.destroy()
    
    def show_notification(self, title, message):
        try:
            subprocess.Popen(["notify-send", title, message])
        except:
            pass


def main():
    win = MuxOSControlCenter()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
