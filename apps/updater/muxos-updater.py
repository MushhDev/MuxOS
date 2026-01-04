#!/usr/bin/env python3
"""MuxOS Update Center - GitHub-based update system with notifications"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk, GLib, Notify
import subprocess
import os
import json
import threading
import urllib.request
import hashlib
from datetime import datetime
import re
import hmac
import secrets

class UpdateCenter(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="MuxOS Update Center")
        self.set_default_size(800, 600)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        Notify.init("MuxOS Update Center")
        
        self.config_file = os.path.expanduser("~/.config/muxos/updates.json")
        self.github_repo = "MushhDev/MuxOS"
        self.remote_version_url = f"https://raw.githubusercontent.com/{self.github_repo}/main/config/muxos.conf"
        self.load_config()

        local_version = self.get_local_os_version() or self.config.get('current_version', '1.0.0')
        self.config['current_version'] = local_version
        self.save_config()
        
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = "🔄 Update Center"
        header.props.subtitle = f"MuxOS v{self.config.get('current_version', '1.0.0')}"
        self.set_titlebar(header)
        
        check_btn = Gtk.Button(label="🔍 Check Now")
        check_btn.connect("clicked", self.check_updates)
        header.pack_end(check_btn)
        
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_top(20)
        main_box.set_margin_bottom(20)
        main_box.set_margin_start(20)
        main_box.set_margin_end(20)
        self.add(main_box)
        
        status_frame = Gtk.Frame(label="System Status")
        status_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        status_box.set_margin_top(15)
        status_box.set_margin_bottom(15)
        status_box.set_margin_start(15)
        status_box.set_margin_end(15)
        
        self.status_label = Gtk.Label()
        self.status_label.set_markup("<span size='large' color='#4CAF50'>✓ System is up to date</span>")
        status_box.pack_start(self.status_label, False, False, 0)
        
        self.version_label = Gtk.Label()
        self.version_label.set_text(f"Current Version: {self.config.get('current_version', '1.0.0')}")
        status_box.pack_start(self.version_label, False, False, 0)
        
        self.last_check_label = Gtk.Label()
        last_check = self.config.get('last_check', 'Never')
        self.last_check_label.set_text(f"Last Check: {last_check}")
        status_box.pack_start(self.last_check_label, False, False, 0)
        
        status_frame.add(status_box)
        main_box.pack_start(status_frame, False, False, 0)
        
        updates_frame = Gtk.Frame(label="Available Updates")
        updates_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        updates_box.set_margin_top(10)
        updates_box.set_margin_bottom(10)
        updates_box.set_margin_start(10)
        updates_box.set_margin_end(10)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_size_request(-1, 200)
        
        self.updates_store = Gtk.ListStore(bool, str, str, str, str)
        self.updates_tree = Gtk.TreeView(model=self.updates_store)
        
        toggle_renderer = Gtk.CellRendererToggle()
        toggle_renderer.connect("toggled", self.on_update_toggled)
        col_toggle = Gtk.TreeViewColumn("Install", toggle_renderer, active=0)
        self.updates_tree.append_column(col_toggle)
        
        for i, title in enumerate(["Component", "Current", "New", "Size"], 1):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(title, renderer, text=i)
            self.updates_tree.append_column(column)
        
        scrolled.add(self.updates_tree)
        updates_box.pack_start(scrolled, True, True, 0)
        
        updates_frame.add(updates_box)
        main_box.pack_start(updates_frame, True, True, 0)
        
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        self.progress_bar.set_text("Ready")
        main_box.pack_start(self.progress_bar, False, False, 0)
        
        btn_box = Gtk.Box(spacing=10)
        
        install_btn = Gtk.Button(label="⬇️ Install Selected")
        install_btn.connect("clicked", self.install_updates)
        btn_box.pack_start(install_btn, False, False, 0)
        
        all_btn = Gtk.Button(label="⬇️ Install All")
        all_btn.connect("clicked", self.install_all_updates)
        btn_box.pack_start(all_btn, False, False, 0)

        rollback_btn = Gtk.Button(label="↩️ Rollback Last")
        rollback_btn.connect("clicked", self.rollback_last_update)
        btn_box.pack_start(rollback_btn, False, False, 0)
        
        changelog_btn = Gtk.Button(label="📋 View Changelog")
        changelog_btn.connect("clicked", self.view_changelog)
        btn_box.pack_start(changelog_btn, False, False, 0)
        
        main_box.pack_start(btn_box, False, False, 0)
        
        settings_frame = Gtk.Frame(label="Update Settings")
        settings_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        settings_box.set_margin_top(10)
        settings_box.set_margin_bottom(10)
        settings_box.set_margin_start(10)
        settings_box.set_margin_end(10)
        
        settings = [
            ("Check for updates automatically", "auto_check", True),
            ("Show notification when updates available", "notify", True),
            ("Download updates in background", "auto_download", False),
            ("Install security updates automatically", "auto_security", True),
            ("Include beta/testing updates", "include_beta", False)
        ]
        
        for name, key, default in settings:
            hbox = Gtk.Box(spacing=10)
            label = Gtk.Label(label=name)
            label.set_xalign(0)
            hbox.pack_start(label, True, True, 0)
            switch = Gtk.Switch()
            switch.set_active(self.config.get(key, default))
            switch.connect("notify::active", lambda s, p, k=key: self.on_setting_changed(k, s.get_active()))
            hbox.pack_start(switch, False, False, 0)
            settings_box.pack_start(hbox, False, False, 0)
        
        settings_frame.add(settings_box)
        main_box.pack_start(settings_frame, False, False, 0)
        
        if self.config.get("auto_check", True):
            GLib.timeout_add_seconds(3600, self.auto_check_updates)

    def _journal_paths(self):
        if os.geteuid() == 0:
            base = "/var/lib/muxos/updates"
        else:
            base = os.path.expanduser("~/.config/muxos")
        return os.path.join(base, "updates-journal.key"), os.path.join(base, "updates-journal.log")

    def _journal_key(self):
        key_path, _ = self._journal_paths()
        os.makedirs(os.path.dirname(key_path), exist_ok=True)
        if os.path.exists(key_path):
            with open(key_path, "rb") as f:
                return f.read()
        key = secrets.token_bytes(32)
        with open(key_path, "wb") as f:
            f.write(key)
        try:
            os.chmod(key_path, 0o600)
        except Exception:
            pass
        return key

    def _journal_append(self, event: dict):
        try:
            _, log_path = self._journal_paths()
            os.makedirs(os.path.dirname(log_path), exist_ok=True)

            prev_hash = ""
            if os.path.exists(log_path):
                try:
                    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            line = line.strip()
                            if line:
                                prev_hash = json.loads(line).get("hash", "")
                except Exception:
                    prev_hash = ""

            ev = dict(event)
            ev["ts"] = datetime.utcnow().isoformat() + "Z"
            ev["prev_hash"] = prev_hash
            payload = json.dumps(ev, sort_keys=True, separators=(",", ":")).encode("utf-8")
            key = self._journal_key()
            ev["hash"] = hmac.new(key, payload, hashlib.sha256).hexdigest()
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(ev, sort_keys=True) + "\n")
        except Exception:
            pass
    
    def load_config(self):
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            if os.path.exists(self.config_file):
                with open(self.config_file) as f:
                    self.config = json.load(f)
            else:
                self.config = {
                    "current_version": "1.0.0",
                    "auto_check": True,
                    "notify": True,
                    "auto_download": False,
                    "auto_security": True,
                    "include_beta": False,
                    "last_check": None
                }
                self.save_config()
        except:
            self.config = {"current_version": "1.0.0"}
    
    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get_local_os_version(self):
        candidates = [
            "/etc/muxos.conf",
            "/usr/share/muxos/muxos.conf",
        ]
        for path in candidates:
            try:
                if not os.path.exists(path):
                    continue
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    data = f.read()
                m = re.search(r'^OS_VERSION\s*=\s*"?([^"\n]+)"?\s*$', data, re.MULTILINE)
                if m:
                    return m.group(1).strip()
            except Exception:
                continue
        return None

    def get_remote_os_version(self):
        req = urllib.request.Request(
            self.remote_version_url,
            headers={"User-Agent": "MuxOS-Updater"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            text = resp.read().decode("utf-8", errors="ignore")
        m = re.search(r'^OS_VERSION\s*=\s*"?([^"\n]+)"?\s*$', text, re.MULTILINE)
        if not m:
            raise RuntimeError("Could not parse OS_VERSION from upstream")
        return m.group(1).strip()
    
    def on_setting_changed(self, key, value):
        self.config[key] = value
        self.save_config()
    
    def on_update_toggled(self, widget, path):
        self.updates_store[path][0] = not self.updates_store[path][0]
    
    def check_updates(self, button=None):
        self.progress_bar.set_text("Checking for updates...")
        self.progress_bar.set_fraction(0.2)
        threading.Thread(target=self._check_updates_thread).start()
    
    def _check_updates_thread(self):
        try:
            GLib.idle_add(self.progress_bar.set_fraction, 0.5)

            local_version = self.get_local_os_version() or self.config.get('current_version', '1.0.0')
            remote_version = self.get_remote_os_version()

            self._journal_append({
                "type": "check",
                "local_version": local_version,
                "remote_version": remote_version,
                "source": "gui",
            })

            self.config['current_version'] = local_version
            self.config['last_seen_remote_version'] = remote_version
            self.save_config()

            updates = []
            if remote_version != local_version:
                updates.append((True, "MuxOS", local_version, remote_version, "-"))

            GLib.idle_add(self._update_ui_with_updates, updates)
            
        except Exception as e:
            GLib.idle_add(self.progress_bar.set_text, f"Error: {str(e)}")
    
    def _update_ui_with_updates(self, updates):
        self.updates_store.clear()
        for update in updates:
            self.updates_store.append(list(update))
        
        self.config["last_check"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.save_config()
        self.last_check_label.set_text(f"Last Check: {self.config['last_check']}")
        
        if updates:
            self.status_label.set_markup(f"<span size='large' color='#FF9800'>⬆️ Update available</span>")
            if self.config.get("notify", True):
                self.show_notification("Update available", "A newer MuxOS version is available")
        else:
            self.status_label.set_markup("<span size='large' color='#4CAF50'>✓ System is up to date</span>")
        
        self.progress_bar.set_fraction(1.0)
        self.progress_bar.set_text("Check complete")

    def _run_update_helper(self, payload):
        try:
            result = subprocess.run(
                ["pkexec", "/usr/lib/muxos/muxos-update-helper.py"],
                input=json.dumps(payload),
                text=True,
                capture_output=True,
            )
            return result.returncode, (result.stdout or "").strip(), (result.stderr or "").strip()
        except Exception as e:
            return 1, "", str(e)
    
    def auto_check_updates(self):
        threading.Thread(target=self._check_updates_thread).start()
        return True
    
    def show_notification(self, title, message):
        notification = Notify.Notification.new("MuxOS Updates", f"{title}\n{message}", "system-software-update")
        notification.show()
    
    def install_updates(self, button):
        selected = [row for row in self.updates_store if row[0]]
        if not selected:
            dialog = Gtk.MessageDialog(transient_for=self, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="No Updates Selected")
            dialog.run()
            dialog.destroy()
            return
        threading.Thread(target=self._install_updates_thread, args=(selected,)).start()
    
    def install_all_updates(self, button):
        for row in self.updates_store:
            row[0] = True
        self.install_updates(button)
    
    def _install_updates_thread(self, updates):
        # Currently we only support real installs for the MuxOS core entry.
        muxos = None
        for upd in updates:
            if len(upd) > 1 and upd[1] == "MuxOS":
                muxos = upd
                break

        if not muxos:
            GLib.idle_add(self.progress_bar.set_text, "Nothing installable selected")
            return

        GLib.idle_add(self.progress_bar.set_text, "Downloading and applying update...")
        GLib.idle_add(self.progress_bar.set_fraction, 0.3)

        self._journal_append({"type": "install", "status": "start", "target": "MuxOS"})

        # Install from immutable tag vX.Y.Z (no moving main branch)
        ref = None
        try:
            ref = "v" + str(muxos[3]).strip()
        except Exception:
            ref = None
        if not ref or ref == "v":
            ref = "v" + (self.config.get("last_seen_remote_version") or "")
        if not ref or ref == "v":
            GLib.idle_add(self._show_error_dialog, "Update failed", "Missing target version")
            return

        code, out, err = self._run_update_helper({"action": "install", "repo": "MushhDev/MuxOS", "ref": ref})
        if code != 0:
            self._journal_append({"type": "install", "status": "error", "error": err or out or "Unknown"})
            GLib.idle_add(self.progress_bar.set_text, "Install failed")
            GLib.idle_add(self._show_error_dialog, "Update failed", err or out or "Unknown error")
            return

        try:
            data = json.loads(out) if out else {}
        except Exception:
            data = {}

        update_id = data.get("update_id")
        if update_id:
            self.config["last_update_id"] = update_id
            self.config["last_update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            self.save_config()

        self._journal_append({"type": "install", "status": "ok", "update_id": update_id})

        GLib.idle_add(self.progress_bar.set_fraction, 1.0)
        GLib.idle_add(self.progress_bar.set_text, f"Update installed (id: {update_id}). Restart recommended.")
        GLib.idle_add(self._show_restart_dialog)

    def _show_error_dialog(self, title, message):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=title,
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def rollback_last_update(self, button):
        update_id = self.config.get("last_update_id")
        if not update_id:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="No rollback available",
            )
            dialog.format_secondary_text("No last_update_id found. Install an update first.")
            dialog.run()
            dialog.destroy()
            return

        self.progress_bar.set_text(f"Rolling back {update_id}...")
        self.progress_bar.set_fraction(0.2)

        def worker():
            self._journal_append({"type": "rollback", "status": "start", "update_id": update_id})
            code, out, err = self._run_update_helper({"action": "rollback", "update_id": update_id})
            if code != 0:
                self._journal_append({"type": "rollback", "status": "error", "update_id": update_id, "error": err or out or "Unknown"})
                GLib.idle_add(self.progress_bar.set_text, "Rollback failed")
                GLib.idle_add(self._show_error_dialog, "Rollback failed", err or out or "Unknown error")
                return
            self._journal_append({"type": "rollback", "status": "ok", "update_id": update_id})
            GLib.idle_add(self.progress_bar.set_fraction, 1.0)
            GLib.idle_add(self.progress_bar.set_text, f"Rollback complete ({update_id}). Restart recommended.")
            GLib.idle_add(self._show_restart_dialog)

        threading.Thread(target=worker, daemon=True).start()
    
    def _show_restart_dialog(self):
        dialog = Gtk.MessageDialog(transient_for=self, message_type=Gtk.MessageType.QUESTION,
                                   buttons=Gtk.ButtonsType.YES_NO, text="Restart Required")
        dialog.format_secondary_text("Updates have been installed. Restart now?")
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.YES:
            subprocess.run(["systemctl", "reboot"])
    
    def view_changelog(self, button):
        dialog = Gtk.Dialog(title="Changelog", transient_for=self, flags=0)
        dialog.add_buttons(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
        dialog.set_default_size(600, 400)
        
        content = dialog.get_content_area()
        scrolled = Gtk.ScrolledWindow()
        
        textview = Gtk.TextView()
        textview.set_editable(False)
        textview.get_buffer().set_text("""# MuxOS Changelog

## Version 1.1.0 (Latest)
- Added new Security Center
- Improved gaming performance
- New disk management tools
- GitHub-based update system
- Bug fixes and improvements

## Version 1.0.0
- Initial release
- Gaming optimizations
- Custom desktop environment
- Driver management
""")
        scrolled.add(textview)
        content.pack_start(scrolled, True, True, 0)
        
        dialog.show_all()
        dialog.run()
        dialog.destroy()

class UpdateDaemon:
    """Background daemon for checking updates"""
    def __init__(self):
        self.config_file = os.path.expanduser("~/.config/muxos/updates.json")
        self.check_interval = 3600
        Notify.init("MuxOS Updates")
    
    def run(self):
        while True:
            self.check_for_updates()
            import time
            time.sleep(self.check_interval)
    
    def check_for_updates(self):
        try:
            config = {}
            if os.path.exists(self.config_file):
                with open(self.config_file) as f:
                    config = json.load(f)

            local_version = self._get_local_os_version() or config.get('current_version', '1.0.0')
            remote_version = self._get_remote_os_version()

            self._journal_append({
                "type": "check",
                "local_version": local_version,
                "remote_version": remote_version,
                "source": "daemon",
            })

            can_notify = bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY") or os.environ.get("DBUS_SESSION_BUS_ADDRESS"))
            if can_notify and remote_version != local_version and config.get("notify", True):
                notification = Notify.Notification.new(
                    "MuxOS Updates",
                    f"New version available: {remote_version} (current: {local_version})",
                    "system-software-update"
                )
                notification.show()
        except:
            pass

    def _journal_paths(self):
        if os.geteuid() == 0:
            base = "/var/lib/muxos/updates"
        else:
            base = os.path.expanduser("~/.config/muxos")
        return os.path.join(base, "updates-journal.key"), os.path.join(base, "updates-journal.log")

    def _journal_key(self):
        key_path, _ = self._journal_paths()
        os.makedirs(os.path.dirname(key_path), exist_ok=True)
        if os.path.exists(key_path):
            with open(key_path, "rb") as f:
                return f.read()
        key = secrets.token_bytes(32)
        with open(key_path, "wb") as f:
            f.write(key)
        try:
            os.chmod(key_path, 0o600)
        except Exception:
            pass
        return key

    def _journal_append(self, event: dict):
        try:
            _, log_path = self._journal_paths()
            os.makedirs(os.path.dirname(log_path), exist_ok=True)

            prev_hash = ""
            if os.path.exists(log_path):
                try:
                    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            line = line.strip()
                            if line:
                                prev_hash = json.loads(line).get("hash", "")
                except Exception:
                    prev_hash = ""

            ev = dict(event)
            ev["ts"] = datetime.utcnow().isoformat() + "Z"
            ev["prev_hash"] = prev_hash
            payload = json.dumps(ev, sort_keys=True, separators=(",", ":")).encode("utf-8")
            key = self._journal_key()
            ev["hash"] = hmac.new(key, payload, hashlib.sha256).hexdigest()
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(ev, sort_keys=True) + "\n")
        except Exception:
            pass

    def _get_local_os_version(self):
        for path in ["/etc/muxos.conf", "/usr/share/muxos/muxos.conf"]:
            try:
                if not os.path.exists(path):
                    continue
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    data = f.read()
                m = re.search(r'^OS_VERSION\s*=\s*"?([^"\n]+)"?\s*$', data, re.MULTILINE)
                if m:
                    return m.group(1).strip()
            except Exception:
                continue
        return None

    def _get_remote_os_version(self):
        url = "https://raw.githubusercontent.com/MushhDev/MuxOS/main/config/muxos.conf"
        req = urllib.request.Request(url, headers={"User-Agent": "MuxOS-Updater"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            text = resp.read().decode("utf-8", errors="ignore")
        m = re.search(r'^OS_VERSION\s*=\s*"?([^"\n]+)"?\s*$', text, re.MULTILINE)
        if not m:
            raise RuntimeError("OS_VERSION not found")
        return m.group(1).strip()

if __name__ == "__main__":
    import sys
    if "--daemon" in sys.argv:
        daemon = UpdateDaemon()
        daemon.run()
    else:
        win = UpdateCenter()
        win.connect("destroy", Gtk.main_quit)
        win.show_all()
        Gtk.main()
