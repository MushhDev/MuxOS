#!/usr/bin/env python3
"""MuxOS Theme Editor - Complete appearance customization"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, Pango
import json
import os
import subprocess

class ThemeEditor(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="MuxOS Theme Editor")
        self.set_default_size(900, 700)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        self.config_file = os.path.expanduser("~/.config/muxos/theme.json")
        self.load_theme()
        
        # Apply CSS
        self.apply_css()
        
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = "🎨 Theme Editor"
        header.props.subtitle = self.theme.get("name", "MuxOS Velocity")
        self.set_titlebar(header)
        
        save_btn = Gtk.Button(label="💾 Save & Apply")
        save_btn.get_style_context().add_class("suggested-action")
        save_btn.connect("clicked", self.save_and_apply)
        header.pack_end(save_btn)
        
        reset_btn = Gtk.Button(label="🔄 Reset")
        reset_btn.connect("clicked", self.reset_theme)
        header.pack_end(reset_btn)
        
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.add(main_box)
        
        sidebar = self.create_sidebar()
        main_box.pack_start(sidebar, False, False, 0)
        
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        main_box.pack_start(self.stack, True, True, 10)
        
        self.create_pages()
    
    def load_theme(self):
        default_theme = {
            "name": "MuxOS Velocity",
            "colors": {
                "primary": "#6366f1",
                "secondary": "#8b5cf6",
                "accent": "#06b6d4",
                "success": "#10b981",
                "warning": "#f59e0b",
                "error": "#ef4444",
                "bg_dark": "#0f0f1a",
                "bg_medium": "#1a1a2e",
                "bg_light": "#252542",
                "text_primary": "#f8fafc",
                "text_secondary": "#cbd5e1"
            },
            "fonts": {
                "family": "Inter",
                "size": 11,
                "monospace": "JetBrains Mono"
            },
            "wallpaper": {
                "path": "/usr/share/backgrounds/muxos-gradient.png",
                "style": "fill"
            },
            "effects": {
                "blur": True,
                "animations": True,
                "transparency": 0.92,
                "corner_radius": 12
            }
        }
        
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            if os.path.exists(self.config_file):
                with open(self.config_file) as f:
                    self.theme = json.load(f)
            else:
                self.theme = default_theme
        except:
            self.theme = default_theme
    
    def save_theme(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.theme, f, indent=2)
    
    def apply_css(self):
        css = b"""
        window {
            background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #0f172a 100%);
        }
        .color-preview {
            border-radius: 8px;
            border: 2px solid #3b3b5c;
            min-width: 40px;
            min-height: 40px;
        }
        .section-title {
            font-size: 16px;
            font-weight: bold;
            color: #f8fafc;
        }
        .preview-box {
            background: #1a1a2e;
            border-radius: 12px;
            border: 1px solid #3b3b5c;
            padding: 20px;
        }
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
    
    def create_sidebar(self):
        sidebar = Gtk.ListBox()
        sidebar.set_size_request(200, -1)
        
        sections = [
            ("🎨 Colors", "colors"),
            ("🔤 Fonts", "fonts"),
            ("🖼️ Wallpaper", "wallpaper"),
            ("✨ Effects", "effects"),
            ("📐 Layout", "layout"),
            ("🎭 Presets", "presets"),
            ("👁️ Preview", "preview")
        ]
        
        for name, page_id in sections:
            row = Gtk.ListBoxRow()
            row.page_id = page_id
            label = Gtk.Label(label=name)
            label.set_xalign(0)
            label.set_margin_start(15)
            label.set_margin_top(12)
            label.set_margin_bottom(12)
            row.add(label)
            sidebar.add(row)
        
        sidebar.connect("row-activated", lambda lb, r: self.stack.set_visible_child_name(r.page_id))
        return sidebar
    
    def create_pages(self):
        self.stack.add_titled(self.create_colors_page(), "colors", "Colors")
        self.stack.add_titled(self.create_fonts_page(), "fonts", "Fonts")
        self.stack.add_titled(self.create_wallpaper_page(), "wallpaper", "Wallpaper")
        self.stack.add_titled(self.create_effects_page(), "effects", "Effects")
        self.stack.add_titled(self.create_layout_page(), "layout", "Layout")
        self.stack.add_titled(self.create_presets_page(), "presets", "Presets")
        self.stack.add_titled(self.create_preview_page(), "preview", "Preview")
    
    def create_colors_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        box.set_margin_top(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>🎨 Color Scheme</span>")
        title.set_xalign(0)
        box.pack_start(title, False, False, 0)
        
        colors_grid = Gtk.Grid()
        colors_grid.set_column_spacing(20)
        colors_grid.set_row_spacing(15)
        
        color_items = [
            ("Primary", "primary", "Main accent color"),
            ("Secondary", "secondary", "Secondary accent"),
            ("Accent", "accent", "Highlights and links"),
            ("Success", "success", "Success states"),
            ("Warning", "warning", "Warning states"),
            ("Error", "error", "Error states"),
            ("Background Dark", "bg_dark", "Darkest background"),
            ("Background Medium", "bg_medium", "Medium background"),
            ("Background Light", "bg_light", "Light background"),
            ("Text Primary", "text_primary", "Main text color"),
            ("Text Secondary", "text_secondary", "Secondary text")
        ]
        
        self.color_buttons = {}
        
        for i, (name, key, desc) in enumerate(color_items):
            row = i // 2
            col = (i % 2) * 3
            
            label = Gtk.Label(label=name)
            label.set_xalign(0)
            colors_grid.attach(label, col, row, 1, 1)
            
            color = self.theme.get("colors", {}).get(key, "#6366f1")
            btn = Gtk.ColorButton()
            btn.set_rgba(self.hex_to_rgba(color))
            btn.connect("color-set", self.on_color_changed, key)
            btn.set_tooltip_text(desc)
            self.color_buttons[key] = btn
            colors_grid.attach(btn, col + 1, row, 1, 1)
        
        box.pack_start(colors_grid, False, False, 10)
        
        # Gradient preview
        gradient_frame = Gtk.Frame(label="Gradient Preview")
        gradient_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        gradient_box.set_margin_top(10)
        gradient_box.set_margin_bottom(10)
        gradient_box.set_margin_start(10)
        gradient_box.set_margin_end(10)
        
        self.gradient_preview = Gtk.DrawingArea()
        self.gradient_preview.set_size_request(-1, 60)
        self.gradient_preview.connect("draw", self.draw_gradient)
        gradient_box.pack_start(self.gradient_preview, False, False, 0)
        
        gradient_frame.add(gradient_box)
        box.pack_start(gradient_frame, False, False, 10)
        
        return box
    
    def create_fonts_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        box.set_margin_top(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>🔤 Typography</span>")
        title.set_xalign(0)
        box.pack_start(title, False, False, 0)
        
        # Font Family
        font_frame = Gtk.Frame(label="Interface Font")
        font_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        font_box.set_margin_top(10)
        font_box.set_margin_bottom(10)
        font_box.set_margin_start(10)
        font_box.set_margin_end(10)
        
        self.font_button = Gtk.FontButton()
        current_font = self.theme.get("fonts", {}).get("family", "Inter")
        current_size = self.theme.get("fonts", {}).get("size", 11)
        self.font_button.set_font(f"{current_font} {current_size}")
        self.font_button.connect("font-set", self.on_font_changed)
        font_box.pack_start(self.font_button, False, False, 0)
        
        font_frame.add(font_box)
        box.pack_start(font_frame, False, False, 0)
        
        # Monospace Font
        mono_frame = Gtk.Frame(label="Monospace Font (Terminal)")
        mono_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        mono_box.set_margin_top(10)
        mono_box.set_margin_bottom(10)
        mono_box.set_margin_start(10)
        mono_box.set_margin_end(10)
        
        self.mono_font_button = Gtk.FontButton()
        mono_font = self.theme.get("fonts", {}).get("monospace", "JetBrains Mono")
        self.mono_font_button.set_font(f"{mono_font} 11")
        mono_box.pack_start(self.mono_font_button, False, False, 0)
        
        mono_frame.add(mono_box)
        box.pack_start(mono_frame, False, False, 0)
        
        # Font Size Scale
        size_frame = Gtk.Frame(label="Base Font Size")
        size_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        size_box.set_margin_top(10)
        size_box.set_margin_bottom(10)
        size_box.set_margin_start(10)
        size_box.set_margin_end(10)
        
        self.size_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 8, 16, 1)
        self.size_scale.set_value(current_size)
        self.size_scale.set_draw_value(True)
        self.size_scale.add_mark(10, Gtk.PositionType.BOTTOM, "Small")
        self.size_scale.add_mark(11, Gtk.PositionType.BOTTOM, "Normal")
        self.size_scale.add_mark(13, Gtk.PositionType.BOTTOM, "Large")
        size_box.pack_start(self.size_scale, False, False, 0)
        
        size_frame.add(size_box)
        box.pack_start(size_frame, False, False, 0)
        
        # Preview
        preview_frame = Gtk.Frame(label="Preview")
        preview_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        preview_box.set_margin_top(10)
        preview_box.set_margin_bottom(10)
        preview_box.set_margin_start(10)
        preview_box.set_margin_end(10)
        
        self.font_preview = Gtk.Label()
        self.font_preview.set_markup("<span size='large'>The quick brown fox jumps over the lazy dog</span>")
        preview_box.pack_start(self.font_preview, False, False, 0)
        
        mono_preview = Gtk.Label()
        mono_preview.set_markup("<span font_family='monospace'>console.log('Hello, MuxOS!');</span>")
        preview_box.pack_start(mono_preview, False, False, 0)
        
        preview_frame.add(preview_box)
        box.pack_start(preview_frame, False, False, 0)
        
        return box
    
    def create_wallpaper_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        box.set_margin_top(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>🖼️ Wallpaper</span>")
        title.set_xalign(0)
        box.pack_start(title, False, False, 0)
        
        # Current wallpaper
        current_frame = Gtk.Frame(label="Current Wallpaper")
        current_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        current_box.set_margin_top(10)
        current_box.set_margin_bottom(10)
        current_box.set_margin_start(10)
        current_box.set_margin_end(10)
        
        self.wallpaper_preview = Gtk.Image()
        self.wallpaper_preview.set_size_request(400, 225)
        current_box.pack_start(self.wallpaper_preview, False, False, 0)
        
        path_label = Gtk.Label()
        wp_path = self.theme.get("wallpaper", {}).get("path", "")
        path_label.set_text(wp_path)
        path_label.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        current_box.pack_start(path_label, False, False, 0)
        
        btn_box = Gtk.Box(spacing=10)
        browse_btn = Gtk.Button(label="📁 Browse...")
        browse_btn.connect("clicked", self.browse_wallpaper)
        btn_box.pack_start(browse_btn, False, False, 0)
        
        gradient_btn = Gtk.Button(label="🎨 Use Gradient")
        gradient_btn.connect("clicked", self.use_gradient_wallpaper)
        btn_box.pack_start(gradient_btn, False, False, 0)
        
        current_box.pack_start(btn_box, False, False, 0)
        current_frame.add(current_box)
        box.pack_start(current_frame, False, False, 0)
        
        # Wallpaper style
        style_frame = Gtk.Frame(label="Display Style")
        style_box = Gtk.Box(spacing=10)
        style_box.set_margin_top(10)
        style_box.set_margin_bottom(10)
        style_box.set_margin_start(10)
        style_box.set_margin_end(10)
        
        styles = [("Fill", "fill"), ("Fit", "fit"), ("Center", "center"), ("Tile", "tile"), ("Stretch", "stretch")]
        self.style_combo = Gtk.ComboBoxText()
        for name, val in styles:
            self.style_combo.append(val, name)
        self.style_combo.set_active_id(self.theme.get("wallpaper", {}).get("style", "fill"))
        style_box.pack_start(self.style_combo, True, True, 0)
        
        style_frame.add(style_box)
        box.pack_start(style_frame, False, False, 0)
        
        return box
    
    def create_effects_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        box.set_margin_top(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>✨ Visual Effects</span>")
        title.set_xalign(0)
        box.pack_start(title, False, False, 0)
        
        effects = self.theme.get("effects", {})
        
        # Toggles
        toggles = [
            ("Enable Animations", "animations", effects.get("animations", True)),
            ("Window Blur", "blur", effects.get("blur", True)),
            ("Window Shadows", "shadows", effects.get("shadows", True)),
            ("Rounded Corners", "rounded", effects.get("rounded", True))
        ]
        
        for name, key, default in toggles:
            hbox = Gtk.Box(spacing=10)
            label = Gtk.Label(label=name)
            label.set_xalign(0)
            hbox.pack_start(label, True, True, 0)
            switch = Gtk.Switch()
            switch.set_active(default)
            switch.connect("notify::active", self.on_effect_toggle, key)
            hbox.pack_start(switch, False, False, 0)
            box.pack_start(hbox, False, False, 5)
        
        # Transparency
        trans_frame = Gtk.Frame(label="Window Transparency")
        trans_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        trans_box.set_margin_top(10)
        trans_box.set_margin_bottom(10)
        trans_box.set_margin_start(10)
        trans_box.set_margin_end(10)
        
        self.trans_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0.5, 1.0, 0.01)
        self.trans_scale.set_value(effects.get("transparency", 0.92))
        self.trans_scale.set_draw_value(True)
        self.trans_scale.add_mark(0.7, Gtk.PositionType.BOTTOM, "70%")
        self.trans_scale.add_mark(0.85, Gtk.PositionType.BOTTOM, "85%")
        self.trans_scale.add_mark(1.0, Gtk.PositionType.BOTTOM, "100%")
        trans_box.pack_start(self.trans_scale, False, False, 0)
        
        trans_frame.add(trans_box)
        box.pack_start(trans_frame, False, False, 10)
        
        # Corner radius
        radius_frame = Gtk.Frame(label="Corner Radius")
        radius_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        radius_box.set_margin_top(10)
        radius_box.set_margin_bottom(10)
        radius_box.set_margin_start(10)
        radius_box.set_margin_end(10)
        
        self.radius_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 24, 1)
        self.radius_scale.set_value(effects.get("corner_radius", 12))
        self.radius_scale.set_draw_value(True)
        self.radius_scale.add_mark(0, Gtk.PositionType.BOTTOM, "Square")
        self.radius_scale.add_mark(12, Gtk.PositionType.BOTTOM, "Normal")
        self.radius_scale.add_mark(24, Gtk.PositionType.BOTTOM, "Round")
        radius_box.pack_start(self.radius_scale, False, False, 0)
        
        radius_frame.add(radius_box)
        box.pack_start(radius_frame, False, False, 0)
        
        return box
    
    def create_layout_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        box.set_margin_top(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>📐 Panel & Layout</span>")
        title.set_xalign(0)
        box.pack_start(title, False, False, 0)
        
        # Panel position
        pos_hbox = Gtk.Box(spacing=10)
        pos_label = Gtk.Label(label="Panel Position")
        pos_label.set_xalign(0)
        pos_hbox.pack_start(pos_label, True, True, 0)
        
        self.pos_combo = Gtk.ComboBoxText()
        for pos in ["Top", "Bottom"]:
            self.pos_combo.append_text(pos)
        self.pos_combo.set_active(1)
        pos_hbox.pack_start(self.pos_combo, False, False, 0)
        box.pack_start(pos_hbox, False, False, 5)
        
        # Panel height
        height_frame = Gtk.Frame(label="Panel Height")
        height_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        height_box.set_margin_top(10)
        height_box.set_margin_bottom(10)
        height_box.set_margin_start(10)
        height_box.set_margin_end(10)
        
        self.height_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 32, 56, 2)
        self.height_scale.set_value(44)
        self.height_scale.set_draw_value(True)
        height_box.pack_start(self.height_scale, False, False, 0)
        
        height_frame.add(height_box)
        box.pack_start(height_frame, False, False, 0)
        
        # Icon size
        icon_frame = Gtk.Frame(label="Icon Size")
        icon_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        icon_box.set_margin_top(10)
        icon_box.set_margin_bottom(10)
        icon_box.set_margin_start(10)
        icon_box.set_margin_end(10)
        
        self.icon_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 16, 48, 4)
        self.icon_scale.set_value(28)
        self.icon_scale.set_draw_value(True)
        icon_box.pack_start(self.icon_scale, False, False, 0)
        
        icon_frame.add(icon_box)
        box.pack_start(icon_frame, False, False, 0)
        
        return box
    
    def create_presets_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        box.set_margin_top(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>🎭 Theme Presets</span>")
        title.set_xalign(0)
        box.pack_start(title, False, False, 0)
        
        presets = [
            ("🌌 Velocity (Default)", "velocity", "#6366f1", "#8b5cf6", "#06b6d4"),
            ("🌊 Ocean", "ocean", "#0ea5e9", "#06b6d4", "#14b8a6"),
            ("🌲 Forest", "forest", "#10b981", "#14b8a6", "#22c55e"),
            ("🌅 Sunset", "sunset", "#f97316", "#ec4899", "#8b5cf6"),
            ("🌙 Midnight", "midnight", "#3b82f6", "#6366f1", "#8b5cf6"),
            ("🔥 Ember", "ember", "#ef4444", "#f97316", "#eab308"),
            ("💜 Grape", "grape", "#a855f7", "#8b5cf6", "#ec4899"),
            ("⚡ Neon", "neon", "#22d3ee", "#a855f7", "#f43f5e")
        ]
        
        grid = Gtk.Grid()
        grid.set_column_spacing(15)
        grid.set_row_spacing(15)
        
        for i, (name, preset_id, c1, c2, c3) in enumerate(presets):
            row, col = divmod(i, 2)
            
            frame = Gtk.Frame()
            frame.set_size_request(300, 100)
            inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            inner.set_margin_top(10)
            inner.set_margin_bottom(10)
            inner.set_margin_start(10)
            inner.set_margin_end(10)
            
            btn = Gtk.Button(label=name)
            btn.connect("clicked", self.apply_preset, preset_id)
            inner.pack_start(btn, False, False, 0)
            
            colors_box = Gtk.Box(spacing=5)
            colors_box.set_halign(Gtk.Align.CENTER)
            for color in [c1, c2, c3]:
                color_box = Gtk.DrawingArea()
                color_box.set_size_request(30, 20)
                color_box.color = color
                color_box.connect("draw", self.draw_color_swatch)
                colors_box.pack_start(color_box, False, False, 0)
            inner.pack_start(colors_box, False, False, 0)
            
            frame.add(inner)
            grid.attach(frame, col, row, 1, 1)
        
        box.pack_start(grid, False, False, 0)
        
        return box
    
    def create_preview_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        box.set_margin_top(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>👁️ Live Preview</span>")
        title.set_xalign(0)
        box.pack_start(title, False, False, 0)
        
        preview_frame = Gtk.Frame(label="UI Components Preview")
        preview_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        preview_box.set_margin_top(15)
        preview_box.set_margin_bottom(15)
        preview_box.set_margin_start(15)
        preview_box.set_margin_end(15)
        
        # Buttons
        btn_box = Gtk.Box(spacing=10)
        btn_box.pack_start(Gtk.Button(label="Normal"), False, False, 0)
        suggested = Gtk.Button(label="Primary")
        suggested.get_style_context().add_class("suggested-action")
        btn_box.pack_start(suggested, False, False, 0)
        destructive = Gtk.Button(label="Danger")
        destructive.get_style_context().add_class("destructive-action")
        btn_box.pack_start(destructive, False, False, 0)
        preview_box.pack_start(btn_box, False, False, 0)
        
        # Entry
        entry = Gtk.Entry()
        entry.set_placeholder_text("Text input field...")
        preview_box.pack_start(entry, False, False, 0)
        
        # Switch
        switch_box = Gtk.Box(spacing=10)
        switch_box.pack_start(Gtk.Label(label="Toggle Switch"), False, False, 0)
        switch = Gtk.Switch()
        switch.set_active(True)
        switch_box.pack_start(switch, False, False, 0)
        preview_box.pack_start(switch_box, False, False, 0)
        
        # Progress
        progress = Gtk.ProgressBar()
        progress.set_fraction(0.7)
        progress.set_text("70%")
        progress.set_show_text(True)
        preview_box.pack_start(progress, False, False, 0)
        
        # Scale
        scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        scale.set_value(50)
        preview_box.pack_start(scale, False, False, 0)
        
        preview_frame.add(preview_box)
        box.pack_start(preview_frame, False, False, 0)
        
        return box
    
    # Helper functions
    def hex_to_rgba(self, hex_color):
        rgba = Gdk.RGBA()
        rgba.parse(hex_color)
        return rgba
    
    def rgba_to_hex(self, rgba):
        return "#{:02x}{:02x}{:02x}".format(
            int(rgba.red * 255),
            int(rgba.green * 255),
            int(rgba.blue * 255)
        )
    
    def draw_gradient(self, widget, cr):
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()
        
        colors = self.theme.get("colors", {})
        primary = colors.get("primary", "#6366f1")
        secondary = colors.get("secondary", "#8b5cf6")
        accent = colors.get("accent", "#06b6d4")
        
        pattern = cr.create_linear_gradient(0, 0, width, 0)
        
        r1, g1, b1 = self.hex_to_rgb(primary)
        r2, g2, b2 = self.hex_to_rgb(secondary)
        r3, g3, b3 = self.hex_to_rgb(accent)
        
        pattern.add_color_stop_rgb(0, r1, g1, b1)
        pattern.add_color_stop_rgb(0.5, r2, g2, b2)
        pattern.add_color_stop_rgb(1, r3, g3, b3)
        
        cr.set_source(pattern)
        self.draw_rounded_rect(cr, 0, 0, width, height, 8)
        cr.fill()
    
    def draw_color_swatch(self, widget, cr):
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()
        
        r, g, b = self.hex_to_rgb(widget.color)
        cr.set_source_rgb(r, g, b)
        self.draw_rounded_rect(cr, 0, 0, width, height, 4)
        cr.fill()
    
    def draw_rounded_rect(self, cr, x, y, w, h, r):
        cr.move_to(x + r, y)
        cr.line_to(x + w - r, y)
        cr.arc(x + w - r, y + r, r, -0.5 * 3.14159, 0)
        cr.line_to(x + w, y + h - r)
        cr.arc(x + w - r, y + h - r, r, 0, 0.5 * 3.14159)
        cr.line_to(x + r, y + h)
        cr.arc(x + r, y + h - r, r, 0.5 * 3.14159, 3.14159)
        cr.line_to(x, y + r)
        cr.arc(x + r, y + r, r, 3.14159, 1.5 * 3.14159)
        cr.close_path()
    
    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    
    def on_color_changed(self, button, key):
        rgba = button.get_rgba()
        hex_color = self.rgba_to_hex(rgba)
        if "colors" not in self.theme:
            self.theme["colors"] = {}
        self.theme["colors"][key] = hex_color
        self.gradient_preview.queue_draw()
    
    def on_font_changed(self, button):
        font = button.get_font()
        if "fonts" not in self.theme:
            self.theme["fonts"] = {}
        parts = font.rsplit(' ', 1)
        self.theme["fonts"]["family"] = parts[0]
        if len(parts) > 1:
            try:
                self.theme["fonts"]["size"] = int(parts[1])
            except:
                pass
    
    def on_effect_toggle(self, switch, gparam, key):
        if "effects" not in self.theme:
            self.theme["effects"] = {}
        self.theme["effects"][key] = switch.get_active()
    
    def browse_wallpaper(self, button):
        dialog = Gtk.FileChooserDialog(title="Select Wallpaper", parent=self,
                                        action=Gtk.FileChooserAction.OPEN)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                          Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        
        filter_img = Gtk.FileFilter()
        filter_img.set_name("Images")
        filter_img.add_mime_type("image/png")
        filter_img.add_mime_type("image/jpeg")
        filter_img.add_mime_type("image/webp")
        dialog.add_filter(filter_img)
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            path = dialog.get_filename()
            if "wallpaper" not in self.theme:
                self.theme["wallpaper"] = {}
            self.theme["wallpaper"]["path"] = path
        dialog.destroy()
    
    def use_gradient_wallpaper(self, button):
        if "wallpaper" not in self.theme:
            self.theme["wallpaper"] = {}
        self.theme["wallpaper"]["path"] = "/usr/share/backgrounds/muxos-gradient.png"
    
    def apply_preset(self, button, preset_id):
        presets = {
            "velocity": {"primary": "#6366f1", "secondary": "#8b5cf6", "accent": "#06b6d4"},
            "ocean": {"primary": "#0ea5e9", "secondary": "#06b6d4", "accent": "#14b8a6"},
            "forest": {"primary": "#10b981", "secondary": "#14b8a6", "accent": "#22c55e"},
            "sunset": {"primary": "#f97316", "secondary": "#ec4899", "accent": "#8b5cf6"},
            "midnight": {"primary": "#3b82f6", "secondary": "#6366f1", "accent": "#8b5cf6"},
            "ember": {"primary": "#ef4444", "secondary": "#f97316", "accent": "#eab308"},
            "grape": {"primary": "#a855f7", "secondary": "#8b5cf6", "accent": "#ec4899"},
            "neon": {"primary": "#22d3ee", "secondary": "#a855f7", "accent": "#f43f5e"}
        }
        
        if preset_id in presets:
            colors = presets[preset_id]
            if "colors" not in self.theme:
                self.theme["colors"] = {}
            self.theme["colors"].update(colors)
            
            for key, btn in self.color_buttons.items():
                if key in colors:
                    btn.set_rgba(self.hex_to_rgba(colors[key]))
            
            self.gradient_preview.queue_draw()
    
    def save_and_apply(self, button):
        self.save_theme()
        
        # Apply wallpaper
        wp = self.theme.get("wallpaper", {})
        if wp.get("path"):
            style = wp.get("style", "fill")
            feh_style = {"fill": "--bg-fill", "fit": "--bg-max", "center": "--bg-center",
                        "tile": "--bg-tile", "stretch": "--bg-scale"}.get(style, "--bg-fill")
            subprocess.run(["feh", feh_style, wp["path"]])
        
        # Restart picom
        subprocess.run(["pkill", "picom"])
        subprocess.Popen(["picom", "--config", "/etc/xdg/picom/picom-velocity.conf"])
        
        dialog = Gtk.MessageDialog(transient_for=self, message_type=Gtk.MessageType.INFO,
                                   buttons=Gtk.ButtonsType.OK, text="Theme Applied!")
        dialog.format_secondary_text("Some changes may require logging out to take full effect.")
        dialog.run()
        dialog.destroy()
    
    def reset_theme(self, button):
        dialog = Gtk.MessageDialog(transient_for=self, message_type=Gtk.MessageType.QUESTION,
                                   buttons=Gtk.ButtonsType.YES_NO, text="Reset Theme?")
        dialog.format_secondary_text("This will restore default theme settings.")
        response = dialog.run()
        dialog.destroy()
        
        if response == Gtk.ResponseType.YES:
            if os.path.exists(self.config_file):
                os.remove(self.config_file)
            self.load_theme()

if __name__ == "__main__":
    win = ThemeEditor()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
