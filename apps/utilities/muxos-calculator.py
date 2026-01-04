#!/usr/bin/env python3
"""MuxOS Calculator"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import math

class Calculator(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Calculator")
        self.set_default_size(300, 400)
        self.set_resizable(False)
        
        self.current = ""
        self.result = ""
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_start(10)
        box.set_margin_end(10)
        self.add(box)
        
        self.display = Gtk.Entry()
        self.display.set_alignment(1)
        self.display.set_editable(False)
        self.display.set_text("0")
        box.pack_start(self.display, False, False, 5)
        
        buttons = [
            ['C', '(', ')', '/'],
            ['7', '8', '9', '*'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['0', '.', '±', '=']
        ]
        
        for row in buttons:
            hbox = Gtk.Box(spacing=5)
            for label in row:
                btn = Gtk.Button(label=label)
                btn.set_size_request(60, 50)
                btn.connect("clicked", self.on_button_clicked)
                hbox.pack_start(btn, True, True, 0)
            box.pack_start(hbox, False, False, 0)
        
        sci_box = Gtk.Box(spacing=5)
        for label in ['√', 'x²', 'sin', 'cos', 'tan']:
            btn = Gtk.Button(label=label)
            btn.connect("clicked", self.on_scientific)
            sci_box.pack_start(btn, True, True, 0)
        box.pack_start(sci_box, False, False, 5)
    
    def on_button_clicked(self, button):
        label = button.get_label()
        
        if label == 'C':
            self.current = ""
            self.display.set_text("0")
        elif label == '=':
            try:
                result = eval(self.current)
                self.display.set_text(str(result))
                self.current = str(result)
            except:
                self.display.set_text("Error")
                self.current = ""
        elif label == '±':
            if self.current and self.current[0] == '-':
                self.current = self.current[1:]
            elif self.current:
                self.current = '-' + self.current
            self.display.set_text(self.current or "0")
        else:
            self.current += label
            self.display.set_text(self.current)
    
    def on_scientific(self, button):
        label = button.get_label()
        try:
            val = float(self.current) if self.current else 0
            if label == '√':
                result = math.sqrt(val)
            elif label == 'x²':
                result = val ** 2
            elif label == 'sin':
                result = math.sin(math.radians(val))
            elif label == 'cos':
                result = math.cos(math.radians(val))
            elif label == 'tan':
                result = math.tan(math.radians(val))
            self.current = str(result)
            self.display.set_text(self.current)
        except:
            self.display.set_text("Error")

if __name__ == "__main__":
    win = Calculator()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
