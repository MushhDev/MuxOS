#!/usr/bin/env python3
"""MuxOS Screenshot Tool"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
import subprocess
import os
from datetime import datetime

class ScreenshotTool(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="MuxOS Screenshot")
        self.set_default_size(400, 300)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        self.save_dir = os.path.expanduser("~/Pictures/Screenshots")
        os.makedirs(self.save_dir, exist_ok=True)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        self.add(box)
        
        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>📸 Screenshot Tool</span>")
        box.pack_start(title, False, False, 0)
        
        modes = [
            ("🖥️ Full Screen", self.capture_fullscreen),
            ("🪟 Active Window", self.capture_window),
            ("✂️ Select Area", self.capture_area),
            ("⏱️ Delayed (5s)", self.capture_delayed)
        ]
        
        for label, callback in modes:
            btn = Gtk.Button(label=label)
            btn.set_size_request(-1, 50)
            btn.connect("clicked", callback)
            box.pack_start(btn, False, False, 0)
        
        options_box = Gtk.Box(spacing=10)
        self.include_cursor = Gtk.CheckButton(label="Include cursor")
        options_box.pack_start(self.include_cursor, False, False, 0)
        self.copy_clipboard = Gtk.CheckButton(label="Copy to clipboard")
        self.copy_clipboard.set_active(True)
        options_box.pack_start(self.copy_clipboard, False, False, 0)
        box.pack_start(options_box, False, False, 0)
    
    def get_filename(self):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return os.path.join(self.save_dir, f"screenshot_{timestamp}.png")
    
    def capture_fullscreen(self, button):
        self.hide()
        GLib.timeout_add(200, self._do_capture, ["scrot", self.get_filename()])
    
    def capture_window(self, button):
        self.hide()
        GLib.timeout_add(200, self._do_capture, ["scrot", "-u", self.get_filename()])
    
    def capture_area(self, button):
        self.hide()
        GLib.timeout_add(200, self._do_capture, ["scrot", "-s", self.get_filename()])
    
    def capture_delayed(self, button):
        self.hide()
        GLib.timeout_add(5000, self._do_capture, ["scrot", self.get_filename()])
    
    def _do_capture(self, cmd):
        filename = cmd[-1]
        subprocess.run(cmd)
        if os.path.exists(filename):
            subprocess.run(["notify-send", "Screenshot Saved", filename])
            if self.copy_clipboard.get_active():
                subprocess.run(["xclip", "-selection", "clipboard", "-t", "image/png", "-i", filename])
        self.show()
        return False

if __name__ == "__main__":
    win = ScreenshotTool()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
