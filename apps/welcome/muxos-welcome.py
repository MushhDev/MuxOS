#!/usr/bin/env python3
"""MuxOS Welcome App - First-run setup and introduction"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
import subprocess
import os
import sys
import json
import re

class WelcomeApp(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="MuxOS Setup")
        self.set_default_size(760, 520)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)

        self.completed = False

        self.selected_locale = "en_US.UTF-8"
        self.user_username = ""
        self.user_password = ""
        self.user_email = ""
        self.wifi_ssid = ""
        self.wifi_password = ""

        self.locales = [
            ("English", "en_US.UTF-8"),
            ("Español", "es_ES.UTF-8"),
            ("中文(简体)", "zh_CN.UTF-8"),
            ("Français", "fr_FR.UTF-8"),
            ("Deutsch", "de_DE.UTF-8"),
        ]

        self.pages = ["language", "account", "wifi", "finish"]
        self.current_page = 0

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(main_box)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        main_box.pack_start(self.stack, True, True, 0)

        self.stack.add_named(self.create_language_page(), "language")
        self.stack.add_named(self.create_account_page(), "account")
        self.stack.add_named(self.create_wifi_page(), "wifi")
        self.stack.add_named(self.create_finish_page(), "finish")

        nav_box = Gtk.Box(spacing=10)
        nav_box.set_margin_bottom(18)
        nav_box.set_margin_start(20)
        nav_box.set_margin_end(20)

        self.back_btn = Gtk.Button(label="← Back")
        self.back_btn.connect("clicked", self.go_back)
        self.back_btn.set_sensitive(False)
        nav_box.pack_start(self.back_btn, False, False, 0)

        nav_box.pack_start(Gtk.Box(), True, True, 0)

        self.next_btn = Gtk.Button(label="Next →")
        self.next_btn.connect("clicked", self.go_next)
        nav_box.pack_start(self.next_btn, False, False, 0)

        main_box.pack_start(nav_box, False, False, 0)

        self.stack.set_visible_child_name(self.pages[self.current_page])
        self.update_nav()

        self.connect("delete-event", self.on_window_close)

    def show_error(self, title, message):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=title,
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def create_language_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        box.set_margin_top(40)
        box.set_margin_start(40)
        box.set_margin_end(40)

        title = Gtk.Label()
        title.set_markup("<span size='xx-large' weight='bold'>Welcome to MuxOS</span>")
        box.pack_start(title, False, False, 0)

        subtitle = Gtk.Label(label="Choose your language")
        box.pack_start(subtitle, False, False, 0)

        self.language_combo = Gtk.ComboBoxText()
        for name, locale in self.locales:
            self.language_combo.append(locale, name)
        self.language_combo.set_active_id(self.selected_locale)
        self.language_combo.connect("changed", self.on_language_changed)
        box.pack_start(self.language_combo, False, False, 10)

        hint = Gtk.Label(label="You can change language later in settings.")
        hint.set_line_wrap(True)
        box.pack_start(hint, False, False, 10)

        return box

    def on_language_changed(self, combo):
        active_id = combo.get_active_id()
        if active_id:
            self.selected_locale = active_id

    def create_account_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(24)
        box.set_margin_start(40)
        box.set_margin_end(40)

        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>Create your user</span>")
        title.set_xalign(0)
        box.pack_start(title, False, False, 0)

        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)

        username_label = Gtk.Label(label="Username")
        username_label.set_xalign(0)
        self.username_entry = Gtk.Entry()
        self.username_entry.set_placeholder_text("e.g. alex")

        password_label = Gtk.Label(label="Password")
        password_label.set_xalign(0)
        self.password_entry = Gtk.Entry()
        self.password_entry.set_visibility(False)

        password2_label = Gtk.Label(label="Repeat password")
        password2_label.set_xalign(0)
        self.password2_entry = Gtk.Entry()
        self.password2_entry.set_visibility(False)

        email_label = Gtk.Label(label="Email (optional)")
        email_label.set_xalign(0)
        self.email_entry = Gtk.Entry()
        self.email_entry.set_placeholder_text("you@example.com")

        grid.attach(username_label, 0, 0, 1, 1)
        grid.attach(self.username_entry, 1, 0, 1, 1)
        grid.attach(password_label, 0, 1, 1, 1)
        grid.attach(self.password_entry, 1, 1, 1, 1)
        grid.attach(password2_label, 0, 2, 1, 1)
        grid.attach(self.password2_entry, 1, 2, 1, 1)
        grid.attach(email_label, 0, 3, 1, 1)
        grid.attach(self.email_entry, 1, 3, 1, 1)

        box.pack_start(grid, False, False, 10)

        note = Gtk.Label(label="This will create a system user and store your profile in a local database.")
        note.set_line_wrap(True)
        note.set_xalign(0)
        box.pack_start(note, False, False, 0)

        return box

    def create_wifi_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(24)
        box.set_margin_start(20)
        box.set_margin_end(20)

        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>Connect to WiFi</span>")
        title.set_xalign(0)
        box.pack_start(title, False, False, 0)

        toolbar = Gtk.Box(spacing=8)
        self.wifi_refresh_btn = Gtk.Button(label="Scan")
        self.wifi_refresh_btn.connect("clicked", self.on_wifi_scan)
        toolbar.pack_start(self.wifi_refresh_btn, False, False, 0)
        toolbar.pack_start(Gtk.Box(), True, True, 0)
        box.pack_start(toolbar, False, False, 0)

        self.wifi_store = Gtk.ListStore(str, int, str)
        wifi_view = Gtk.TreeView(model=self.wifi_store)
        wifi_view.get_selection().connect("changed", self.on_wifi_selected)

        renderer = Gtk.CellRendererText()
        wifi_view.append_column(Gtk.TreeViewColumn("SSID", renderer, text=0))
        wifi_view.append_column(Gtk.TreeViewColumn("Signal", renderer, text=1))
        wifi_view.append_column(Gtk.TreeViewColumn("Security", renderer, text=2))

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(220)
        scrolled.add(wifi_view)
        box.pack_start(scrolled, True, True, 0)

        pw_box = Gtk.Box(spacing=10)
        pw_label = Gtk.Label(label="WiFi password")
        pw_label.set_xalign(0)
        self.wifi_password_entry = Gtk.Entry()
        self.wifi_password_entry.set_visibility(False)
        pw_box.pack_start(pw_label, False, False, 0)
        pw_box.pack_start(self.wifi_password_entry, True, True, 0)
        box.pack_start(pw_box, False, False, 0)

        hint = Gtk.Label(label="Select a network. Leave password empty for open networks.")
        hint.set_xalign(0)
        box.pack_start(hint, False, False, 0)

        GLib.idle_add(self.on_wifi_scan, None)

        return box

    def nmcli(self, args, timeout=12):
        try:
            result = subprocess.run(
                ["nmcli"] + args,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return 1, "", str(e)

    def on_wifi_scan(self, button):
        self.wifi_store.clear()
        code, out, err = self.nmcli(["-t", "--separator", "\t", "-f", "SSID,SIGNAL,SECURITY", "dev", "wifi", "list", "--rescan", "yes"])
        if code != 0:
            return
        seen = set()
        for line in out.splitlines():
            parts = line.split("\t")
            if len(parts) < 3:
                continue
            ssid = parts[0].strip()
            if not ssid or ssid in seen:
                continue
            seen.add(ssid)
            try:
                signal = int(parts[1])
            except ValueError:
                signal = 0
            sec = parts[2].strip() or "OPEN"
            self.wifi_store.append([ssid, signal, sec])

    def on_wifi_selected(self, selection):
        model, it = selection.get_selected()
        if not it:
            self.wifi_ssid = ""
            return
        self.wifi_ssid = model.get_value(it, 0)

    def create_finish_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        box.set_margin_top(40)
        box.set_margin_start(40)
        box.set_margin_end(40)

        title = Gtk.Label()
        title.set_markup("<span size='xx-large' weight='bold'>Ready</span>")
        box.pack_start(title, False, False, 0)

        self.finish_summary = Gtk.Label(label="")
        self.finish_summary.set_line_wrap(True)
        self.finish_summary.set_xalign(0)
        box.pack_start(self.finish_summary, False, False, 0)

        note = Gtk.Label(label="When you click Finish, MuxOS will apply these settings. You may need to log out or reboot to use the new user.")
        note.set_line_wrap(True)
        note.set_xalign(0)
        box.pack_start(note, False, False, 0)

        return box

    def refresh_finish_summary(self):
        ssid = self.wifi_ssid or "(not selected)"
        user = (self.username_entry.get_text() or "").strip()
        lang_name = self.selected_locale
        for name, loc in self.locales:
            if loc == self.selected_locale:
                lang_name = f"{name} ({loc})"
                break
        self.finish_summary.set_text(
            "Language: {lang}\nUser: {user}\nWiFi: {wifi}".format(
                lang=lang_name,
                user=user or "(not set)",
                wifi=ssid,
            )
        )

    def validate_language(self):
        return True

    def validate_account(self):
        username = (self.username_entry.get_text() or "").strip()
        password = self.password_entry.get_text() or ""
        password2 = self.password2_entry.get_text() or ""
        email = (self.email_entry.get_text() or "").strip()

        if not re.fullmatch(r"[a-z_][a-z0-9_-]{0,31}", username):
            self.show_error("Invalid username", "Use lowercase letters/numbers and start with a letter. Max 32 chars.")
            return False
        if len(password) < 4:
            self.show_error("Weak password", "Password must be at least 4 characters.")
            return False
        if password != password2:
            self.show_error("Password mismatch", "Passwords do not match.")
            return False
        if email and "@" not in email:
            self.show_error("Invalid email", "Email must contain @ or be left empty.")
            return False

        self.user_username = username
        self.user_password = password
        self.user_email = email
        return True

    def validate_wifi(self):
        self.wifi_password = self.wifi_password_entry.get_text() or ""
        return True

    def apply_setup(self):
        payload = {
            "locale": self.selected_locale,
            "user": {
                "username": self.user_username,
                "password": self.user_password,
                "email": self.user_email,
            },
            "wifi": {
                "ssid": self.wifi_ssid,
                "password": self.wifi_password,
            },
        }

        helper_path = "/usr/lib/muxos/muxos-firstboot-helper.py"
        if not os.path.exists(helper_path):
            self.show_error("Missing helper", "First-boot helper not found. Please reinstall MuxOS setup tools.")
            return False

        try:
            result = subprocess.run(
                ["pkexec", helper_path],
                input=json.dumps(payload),
                text=True,
                capture_output=True,
            )
        except Exception as e:
            self.show_error("Setup failed", str(e))
            return False

        if result.returncode != 0:
            msg = (result.stderr or result.stdout or "Unknown error").strip()
            self.show_error("Setup failed", msg)
            return False
        return True

    def go_back(self, button):
        if self.current_page > 0:
            self.current_page -= 1
            self.stack.set_visible_child_name(self.pages[self.current_page])
            self.update_nav()

    def go_next(self, button):
        current_name = self.pages[self.current_page]
        if current_name == "language":
            if not self.validate_language():
                return
        if current_name == "account":
            if not self.validate_account():
                return
        if current_name == "wifi":
            if not self.validate_wifi():
                return

        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            self.stack.set_visible_child_name(self.pages[self.current_page])
            self.update_nav()
            if self.pages[self.current_page] == "finish":
                self.refresh_finish_summary()
            return

        if not self.apply_setup():
            return

        self.completed = True
        self.destroy()

    def update_nav(self):
        self.back_btn.set_sensitive(self.current_page > 0)
        if self.current_page == len(self.pages) - 1:
            self.next_btn.set_label("Finish ✓")
        else:
            self.next_btn.set_label("Next →")

    def on_window_close(self, *args):
        Gtk.main_quit()
        return False

if __name__ == "__main__":
    win = WelcomeApp()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
    sys.exit(0 if win.completed else 1)
