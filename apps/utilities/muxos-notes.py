#!/usr/bin/env python3
"""MuxOS Notes - Simple note-taking app"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango
import os
import json
from datetime import datetime

class NotesApp(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="MuxOS Notes")
        self.set_default_size(800, 600)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        self.notes_dir = os.path.expanduser("~/.local/share/muxos/notes")
        os.makedirs(self.notes_dir, exist_ok=True)
        self.current_note = None
        
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = "📝 Notes"
        self.set_titlebar(header)
        
        new_btn = Gtk.Button(label="+ New")
        new_btn.connect("clicked", self.new_note)
        header.pack_start(new_btn)
        
        save_btn = Gtk.Button(label="💾 Save")
        save_btn.connect("clicked", self.save_note)
        header.pack_end(save_btn)
        
        delete_btn = Gtk.Button(label="🗑️")
        delete_btn.connect("clicked", self.delete_note)
        header.pack_end(delete_btn)
        
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.add(main_box)
        
        sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        sidebar.set_size_request(200, -1)
        
        search = Gtk.SearchEntry()
        search.set_placeholder_text("Search notes...")
        search.connect("search-changed", self.search_notes)
        sidebar.pack_start(search, False, False, 5)
        
        scrolled = Gtk.ScrolledWindow()
        self.notes_list = Gtk.ListBox()
        self.notes_list.connect("row-selected", self.on_note_selected)
        scrolled.add(self.notes_list)
        sidebar.pack_start(scrolled, True, True, 0)
        
        main_box.pack_start(sidebar, False, False, 0)
        main_box.pack_start(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL), False, False, 0)
        
        editor_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        self.title_entry = Gtk.Entry()
        self.title_entry.set_placeholder_text("Note title...")
        editor_box.pack_start(self.title_entry, False, False, 5)
        
        scrolled_editor = Gtk.ScrolledWindow()
        self.text_view = Gtk.TextView()
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.text_view.set_left_margin(10)
        self.text_view.set_right_margin(10)
        self.text_view.set_top_margin(10)
        scrolled_editor.add(self.text_view)
        editor_box.pack_start(scrolled_editor, True, True, 0)
        
        main_box.pack_start(editor_box, True, True, 5)
        
        self.load_notes()
    
    def load_notes(self):
        for child in self.notes_list.get_children():
            self.notes_list.remove(child)
        
        notes = []
        for f in os.listdir(self.notes_dir):
            if f.endswith('.json'):
                path = os.path.join(self.notes_dir, f)
                try:
                    with open(path) as file:
                        data = json.load(file)
                        data['filename'] = f
                        notes.append(data)
                except:
                    pass
        
        notes.sort(key=lambda x: x.get('modified', ''), reverse=True)
        
        for note in notes:
            row = Gtk.ListBoxRow()
            row.note_data = note
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            box.set_margin_top(5)
            box.set_margin_bottom(5)
            box.set_margin_start(10)
            
            title = Gtk.Label(label=note.get('title', 'Untitled'))
            title.set_xalign(0)
            title.set_ellipsize(Pango.EllipsizeMode.END)
            box.pack_start(title, False, False, 0)
            
            date = Gtk.Label(label=note.get('modified', '')[:10])
            date.set_xalign(0)
            date.get_style_context().add_class("dim-label")
            box.pack_start(date, False, False, 0)
            
            row.add(box)
            self.notes_list.add(row)
        
        self.notes_list.show_all()
    
    def new_note(self, button):
        self.current_note = None
        self.title_entry.set_text("")
        self.text_view.get_buffer().set_text("")
    
    def save_note(self, button):
        title = self.title_entry.get_text() or "Untitled"
        buffer = self.text_view.get_buffer()
        content = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True)
        
        now = datetime.now().isoformat()
        
        if self.current_note:
            filename = self.current_note['filename']
        else:
            filename = f"note_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = {
            'title': title,
            'content': content,
            'created': self.current_note.get('created', now) if self.current_note else now,
            'modified': now
        }
        
        with open(os.path.join(self.notes_dir, filename), 'w') as f:
            json.dump(data, f, indent=2)
        
        self.load_notes()
    
    def delete_note(self, button):
        if self.current_note:
            dialog = Gtk.MessageDialog(transient_for=self, message_type=Gtk.MessageType.QUESTION,
                                       buttons=Gtk.ButtonsType.YES_NO, text="Delete Note?")
            response = dialog.run()
            dialog.destroy()
            if response == Gtk.ResponseType.YES:
                os.remove(os.path.join(self.notes_dir, self.current_note['filename']))
                self.new_note(None)
                self.load_notes()
    
    def on_note_selected(self, listbox, row):
        if row:
            self.current_note = row.note_data
            self.title_entry.set_text(self.current_note.get('title', ''))
            self.text_view.get_buffer().set_text(self.current_note.get('content', ''))
    
    def search_notes(self, entry):
        query = entry.get_text().lower()
        for row in self.notes_list.get_children():
            note = row.note_data
            visible = query in note.get('title', '').lower() or query in note.get('content', '').lower()
            row.set_visible(visible)

if __name__ == "__main__":
    win = NotesApp()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
