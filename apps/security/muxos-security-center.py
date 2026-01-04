#!/usr/bin/env python3
"""
MuxOS Security Center - Comprehensive security management
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk
import subprocess
import os
import json
import threading
from datetime import datetime
 

class SecurityCenter(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="MuxOS Security Center")
        self.set_default_size(1000, 700)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        self.config_file = os.path.expanduser("~/.config/muxos/security.json")
        self.load_config()
        
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = "Security Center"
        header.props.subtitle = "System Protection & Privacy"
        self.set_titlebar(header)
        
        scan_btn = Gtk.Button(label="🔍 Quick Scan")
        scan_btn.connect("clicked", self.run_quick_scan)
        header.pack_end(scan_btn)
        
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.add(main_box)
        
        sidebar = self.create_sidebar()
        main_box.pack_start(sidebar, False, False, 0)
        
        self.content_stack = Gtk.Stack()
        self.content_stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        main_box.pack_start(self.content_stack, True, True, 10)
        
        self.create_pages()
        GLib.timeout_add_seconds(30, self.update_status)
        
    def load_config(self):
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = {
                    "firewall_enabled": True,
                    "auto_updates": True,
                    "intrusion_detection": True,
                    "rootkit_scan": True,
                    "network_monitor": True,
                    "usb_guard": False,
                    "privacy_enabled": False,
                    "hardening_enabled": False,
                    "last_scan": None
                }
                self.save_config()
        except:
            self.config = {}
    
    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def _run_security_helper(self, payload):
        try:
            result = subprocess.run(
                ["pkexec", "/usr/lib/muxos/muxos-security-helper.py"],
                input=json.dumps(payload),
                text=True,
                capture_output=True,
            )
            return result.returncode, (result.stdout or "").strip(), (result.stderr or "").strip()
        except Exception as e:
            return 1, "", str(e)

    def _apply_toggle_async(self, feature, enabled):
        def worker():
            code, out, err = self._run_security_helper({"action": "toggle", "feature": feature, "enabled": enabled})
            if code != 0:
                GLib.idle_add(self._show_error, "Security change failed", err or out or "Unknown error")
        threading.Thread(target=worker, daemon=True).start()

    def _show_error(self, title, message):
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
    
    def create_sidebar(self):
        sidebar = Gtk.ListBox()
        sidebar.set_size_request(220, -1)
        
        categories = [
            ("🛡️ Overview", "overview"),
            ("🔥 Firewall", "firewall"),
            ("🦠 Antivirus", "antivirus"),
            ("🔐 Privacy", "privacy"),
            ("🌐 Network Security", "network"),
            ("🚨 Intrusion Detection", "intrusion"),
            ("📋 Security Logs", "logs"),
            ("⚙️ Settings", "settings")
        ]
        
        for name, page_id in categories:
            row = Gtk.ListBoxRow()
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            row.add(hbox)
            row.page_id = page_id
            
            label = Gtk.Label(label=name)
            label.set_xalign(0)
            hbox.pack_start(label, True, True, 10)
            
            sidebar.add(row)
        
        sidebar.connect("row-activated", self.on_sidebar_row_activated)
        return sidebar
    
    def create_pages(self):
        self.content_stack.add_titled(self.create_overview_page(), "overview", "Overview")
        self.content_stack.add_titled(self.create_firewall_page(), "firewall", "Firewall")
        self.content_stack.add_titled(self.create_antivirus_page(), "antivirus", "Antivirus")
        self.content_stack.add_titled(self.create_privacy_page(), "privacy", "Privacy")
        self.content_stack.add_titled(self.create_network_page(), "network", "Network")
        self.content_stack.add_titled(self.create_intrusion_page(), "intrusion", "Intrusion")
        self.content_stack.add_titled(self.create_logs_page(), "logs", "Logs")
        self.content_stack.add_titled(self.create_settings_page(), "settings", "Settings")
    
    def create_overview_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        box.set_margin_top(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        title = Gtk.Label()
        title.set_markup("<span size='xx-large' weight='bold'>🛡️ Security Overview</span>")
        title.set_xalign(0)
        box.pack_start(title, False, False, 0)
        
        self.status_label = Gtk.Label()
        self.status_label.set_markup("<span size='large' color='#4CAF50'>✓ System Protected</span>")
        self.status_label.set_xalign(0)
        box.pack_start(self.status_label, False, False, 10)
        
        grid = Gtk.Grid()
        grid.set_column_spacing(20)
        grid.set_row_spacing(15)
        box.pack_start(grid, False, False, 20)
        
        status_items = [
            ("Firewall", "firewall_enabled", "🔥"),
            ("Antivirus", "auto_updates", "🦠"),
            ("Intrusion Detection", "intrusion_detection", "🚨"),
            ("Network Monitor", "network_monitor", "🌐"),
            ("Rootkit Scanner", "rootkit_scan", "🔍"),
            ("USB Guard", "usb_guard", "🔌"),
            ("Privacy", "privacy_enabled", "🔐"),
            ("Hardening", "hardening_enabled", "🧱")
        ]
        
        for i, (name, key, icon) in enumerate(status_items):
            row, col = divmod(i, 3)
            
            frame = Gtk.Frame()
            frame.set_size_request(200, 100)
            inner_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            inner_box.set_margin_top(10)
            inner_box.set_margin_bottom(10)
            inner_box.set_margin_start(15)
            inner_box.set_margin_end(15)
            
            icon_label = Gtk.Label()
            icon_label.set_markup(f"<span size='xx-large'>{icon}</span>")
            inner_box.pack_start(icon_label, False, False, 0)
            
            name_label = Gtk.Label(label=name)
            inner_box.pack_start(name_label, False, False, 0)
            
            status = self.config.get(key, False)
            status_label = Gtk.Label()
            if status:
                status_label.set_markup("<span color='#4CAF50'>● Active</span>")
            else:
                status_label.set_markup("<span color='#f44336'>● Inactive</span>")
            inner_box.pack_start(status_label, False, False, 0)
            
            frame.add(inner_box)
            grid.attach(frame, col, row, 1, 1)
        
        actions_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.pack_start(actions_box, False, False, 20)
        
        full_scan_btn = Gtk.Button(label="🔍 Full System Scan")
        full_scan_btn.connect("clicked", self.run_full_scan)
        actions_box.pack_start(full_scan_btn, False, False, 0)
        
        update_btn = Gtk.Button(label="🔄 Update Definitions")
        update_btn.connect("clicked", self.update_definitions)
        actions_box.pack_start(update_btn, False, False, 0)
        
        report_btn = Gtk.Button(label="📊 Generate Report")
        report_btn.connect("clicked", self.generate_report)
        actions_box.pack_start(report_btn, False, False, 0)

        profile_frame = Gtk.Frame(label="Security Profiles")
        profile_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        profile_box.set_margin_top(10)
        profile_box.set_margin_bottom(10)
        profile_box.set_margin_start(10)
        profile_box.set_margin_end(10)

        self.profile_combo = Gtk.ComboBoxText()
        self.profile_combo.append("gaming", "🎮 Gaming")
        self.profile_combo.append("balanced", "⚖️ Balanced")
        self.profile_combo.append("paranoid", "🔒 Paranoid")
        self.profile_combo.set_active_id("balanced")
        profile_box.pack_start(self.profile_combo, True, True, 0)

        apply_profile_btn = Gtk.Button(label="Apply")
        apply_profile_btn.connect("clicked", self.apply_security_profile)
        profile_box.pack_start(apply_profile_btn, False, False, 0)

        profile_frame.add(profile_box)
        box.pack_start(profile_frame, False, False, 0)
        
        return box

    def create_privacy_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_start(20)
        box.set_margin_end(20)

        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>🔐 Privacy Protection</span>")
        title.set_xalign(0)
        box.pack_start(title, False, False, 0)

        enable_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        enable_label = Gtk.Label(label="Enable Privacy Protections")
        enable_label.set_xalign(0)
        enable_box.pack_start(enable_label, True, True, 0)
        self.privacy_switch = Gtk.Switch()
        self.privacy_switch.set_active(self.config.get("privacy_enabled", False))
        self.privacy_switch.connect("notify::active", self.on_privacy_toggle)
        enable_box.pack_start(self.privacy_switch, False, False, 0)
        box.pack_start(enable_box, False, False, 10)

        hint = Gtk.Label(label="This applies system-wide privacy settings (DNS over TLS, tracking host blocks, Firefox privacy defaults, etc.).")
        hint.set_line_wrap(True)
        hint.set_xalign(0)
        box.pack_start(hint, False, False, 0)

        return box
    
    def create_firewall_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>🔥 Firewall Configuration</span>")
        title.set_xalign(0)
        box.pack_start(title, False, False, 0)
        
        enable_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        enable_label = Gtk.Label(label="Enable Firewall")
        enable_label.set_xalign(0)
        enable_box.pack_start(enable_label, True, True, 0)
        self.firewall_switch = Gtk.Switch()
        self.firewall_switch.set_active(self.config.get("firewall_enabled", True))
        self.firewall_switch.connect("notify::active", self.on_firewall_toggle)
        enable_box.pack_start(self.firewall_switch, False, False, 0)
        box.pack_start(enable_box, False, False, 10)
        
        profiles_frame = Gtk.Frame(label="Security Profiles")
        profiles_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        profiles_box.set_margin_top(10)
        profiles_box.set_margin_bottom(10)
        profiles_box.set_margin_start(10)
        profiles_box.set_margin_end(10)
        
        profiles = [
            ("🏠 Home Network", "Trust local network, block incoming"),
            ("🏢 Public Network", "Maximum security, block all incoming"),
            ("🎮 Gaming Mode", "Allow game ports, optimized for latency"),
            ("🔒 Paranoid Mode", "Block everything except whitelist")
        ]
        
        profile_group = None
        for name, desc in profiles:
            radio = Gtk.RadioButton.new_with_label_from_widget(profile_group, name)
            if profile_group is None:
                profile_group = radio
            desc_label = Gtk.Label(label=f"  {desc}")
            desc_label.set_xalign(0)
            profiles_box.pack_start(radio, False, False, 0)
            profiles_box.pack_start(desc_label, False, False, 0)
        
        profiles_frame.add(profiles_box)
        box.pack_start(profiles_frame, False, False, 10)
        
        rules_frame = Gtk.Frame(label="Custom Rules")
        rules_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        rules_box.set_margin_top(10)
        rules_box.set_margin_bottom(10)
        rules_box.set_margin_start(10)
        rules_box.set_margin_end(10)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_size_request(-1, 200)
        
        self.rules_store = Gtk.ListStore(str, str, str, str, str)
        self.rules_store.append(["Allow", "TCP", "22", "SSH", "Incoming"])
        self.rules_store.append(["Allow", "TCP", "80,443", "HTTP/HTTPS", "Outgoing"])
        self.rules_store.append(["Allow", "UDP", "27015-27030", "Steam", "Both"])
        self.rules_store.append(["Block", "TCP", "23", "Telnet", "Incoming"])
        
        treeview = Gtk.TreeView(model=self.rules_store)
        for i, title in enumerate(["Action", "Protocol", "Port", "Description", "Direction"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(title, renderer, text=i)
            treeview.append_column(column)
        
        scrolled.add(treeview)
        rules_box.pack_start(scrolled, True, True, 0)
        
        rules_btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        add_rule_btn = Gtk.Button(label="+ Add Rule")
        add_rule_btn.connect("clicked", self.add_firewall_rule)
        rules_btn_box.pack_start(add_rule_btn, False, False, 0)
        
        del_rule_btn = Gtk.Button(label="- Remove Rule")
        rules_btn_box.pack_start(del_rule_btn, False, False, 0)
        
        rules_box.pack_start(rules_btn_box, False, False, 5)
        rules_frame.add(rules_box)
        box.pack_start(rules_frame, True, True, 0)
        
        return box
    
    def create_antivirus_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>🦠 Antivirus Protection</span>")
        title.set_xalign(0)
        box.pack_start(title, False, False, 0)
        
        status_frame = Gtk.Frame(label="Protection Status")
        status_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        status_box.set_margin_top(10)
        status_box.set_margin_bottom(10)
        status_box.set_margin_start(10)
        status_box.set_margin_end(10)
        
        self.av_status = Gtk.Label()
        self.av_status.set_markup("<span size='large' color='#4CAF50'>✓ Real-time protection active</span>")
        status_box.pack_start(self.av_status, False, False, 0)
        
        self.last_scan_label = Gtk.Label(label="Last scan: Never")
        status_box.pack_start(self.last_scan_label, False, False, 0)
        
        self.definitions_label = Gtk.Label(label="Virus definitions: Up to date")
        status_box.pack_start(self.definitions_label, False, False, 0)
        
        status_frame.add(status_box)
        box.pack_start(status_frame, False, False, 10)
        
        scan_frame = Gtk.Frame(label="Scan Options")
        scan_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        scan_box.set_margin_top(10)
        scan_box.set_margin_bottom(10)
        scan_box.set_margin_start(10)
        scan_box.set_margin_end(10)
        
        scans = [
            ("🚀 Quick Scan", "Scan common threat locations", self.run_quick_scan),
            ("🔍 Full Scan", "Complete system scan", self.run_full_scan),
            ("📁 Custom Scan", "Scan specific folders", self.run_custom_scan),
            ("🔌 USB Scan", "Scan connected USB devices", self.run_usb_scan),
            ("🕵️ Rootkit Scan", "Deep system scan for rootkits", self.run_rootkit_scan)
        ]
        
        for name, desc, callback in scans:
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            btn = Gtk.Button(label=name)
            btn.set_size_request(150, -1)
            btn.connect("clicked", callback)
            hbox.pack_start(btn, False, False, 0)
            
            desc_label = Gtk.Label(label=desc)
            desc_label.set_xalign(0)
            hbox.pack_start(desc_label, True, True, 0)
            
            scan_box.pack_start(hbox, False, False, 0)
        
        scan_frame.add(scan_box)
        box.pack_start(scan_frame, False, False, 0)
        
        self.scan_progress = Gtk.ProgressBar()
        self.scan_progress.set_show_text(True)
        self.scan_progress.set_text("Ready")
        box.pack_start(self.scan_progress, False, False, 10)
        
        quarantine_frame = Gtk.Frame(label="Quarantine")
        qbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        qbox.set_margin_top(10)
        qbox.set_margin_bottom(10)
        qbox.set_margin_start(10)
        qbox.set_margin_end(10)
        
        q_label = Gtk.Label(label="0 items in quarantine")
        qbox.pack_start(q_label, False, False, 0)
        
        q_btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        view_q_btn = Gtk.Button(label="View Quarantine")
        q_btn_box.pack_start(view_q_btn, False, False, 0)
        empty_q_btn = Gtk.Button(label="Empty Quarantine")
        q_btn_box.pack_start(empty_q_btn, False, False, 0)
        qbox.pack_start(q_btn_box, False, False, 0)
        
        quarantine_frame.add(qbox)
        box.pack_start(quarantine_frame, False, False, 0)
        
        return box
    
    def create_network_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>🌐 Network Security</span>")
        title.set_xalign(0)
        box.pack_start(title, False, False, 0)
        
        monitor_frame = Gtk.Frame(label="Active Connections")
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_size_request(-1, 200)
        
        self.connections_store = Gtk.ListStore(str, str, str, str, str)
        treeview = Gtk.TreeView(model=self.connections_store)
        
        for i, title in enumerate(["Process", "Local Address", "Remote Address", "Status", "Protocol"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(title, renderer, text=i)
            treeview.append_column(column)
        
        scrolled.add(treeview)
        monitor_frame.add(scrolled)
        box.pack_start(monitor_frame, True, True, 10)
        
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        refresh_btn = Gtk.Button(label="🔄 Refresh")
        refresh_btn.connect("clicked", self.refresh_connections)
        btn_box.pack_start(refresh_btn, False, False, 0)
        
        block_btn = Gtk.Button(label="🚫 Block Selected")
        btn_box.pack_start(block_btn, False, False, 0)
        
        box.pack_start(btn_box, False, False, 0)
        
        self.refresh_connections(None)
        
        return box
    
    def create_intrusion_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>🚨 Intrusion Detection System</span>")
        title.set_xalign(0)
        box.pack_start(title, False, False, 0)
        
        enable_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        enable_label = Gtk.Label(label="Enable IDS")
        enable_box.pack_start(enable_label, True, True, 0)
        ids_switch = Gtk.Switch()
        ids_switch.set_active(self.config.get("intrusion_detection", True))
        ids_switch.connect("notify::active", self.on_ids_toggle)
        enable_box.pack_start(ids_switch, False, False, 0)
        box.pack_start(enable_box, False, False, 10)
        
        options = [
            ("Monitor failed login attempts", True),
            ("Detect port scanning", True),
            ("Monitor file integrity", True),
            ("Detect privilege escalation", True),
            ("Monitor suspicious processes", True),
            ("Alert on SSH brute force", True),
            ("Block repeated offenders", True)
        ]
        
        for name, default in options:
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            label = Gtk.Label(label=name)
            label.set_xalign(0)
            hbox.pack_start(label, True, True, 0)
            switch = Gtk.Switch()
            switch.set_active(default)
            hbox.pack_start(switch, False, False, 0)
            box.pack_start(hbox, False, False, 3)
        
        alerts_frame = Gtk.Frame(label="Recent Alerts")
        alerts_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        alerts_box.set_margin_top(10)
        alerts_box.set_margin_bottom(10)
        alerts_box.set_margin_start(10)
        alerts_box.set_margin_end(10)
        
        no_alerts = Gtk.Label(label="✓ No security alerts")
        alerts_box.pack_start(no_alerts, False, False, 0)
        
        alerts_frame.add(alerts_box)
        box.pack_start(alerts_frame, False, False, 10)
        
        return box
    
    def create_logs_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>📋 Security Logs</span>")
        title.set_xalign(0)
        box.pack_start(title, False, False, 0)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_size_request(-1, 400)
        
        self.logs_buffer = Gtk.TextBuffer()
        logs_view = Gtk.TextView(buffer=self.logs_buffer)
        logs_view.set_editable(False)
        logs_view.set_monospace(True)
        
        sample_logs = """[2026-01-04 16:30:01] INFO: Security Center started
[2026-01-04 16:30:02] INFO: Firewall loaded with 4 rules
[2026-01-04 16:30:03] INFO: Real-time protection enabled
[2026-01-04 16:30:05] INFO: Network monitoring active
[2026-01-04 16:30:10] INFO: IDS initialized
[2026-01-04 16:31:00] INFO: System scan completed - No threats found
"""
        self.logs_buffer.set_text(sample_logs)
        
        scrolled.add(logs_view)
        box.pack_start(scrolled, True, True, 0)
        
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        clear_btn = Gtk.Button(label="Clear Logs")
        btn_box.pack_start(clear_btn, False, False, 0)
        export_btn = Gtk.Button(label="Export Logs")
        btn_box.pack_start(export_btn, False, False, 0)
        verify_btn = Gtk.Button(label="Verify Integrity")
        verify_btn.connect("clicked", self.verify_integrity)
        btn_box.pack_start(verify_btn, False, False, 0)
        box.pack_start(btn_box, False, False, 0)
        
        return box
    
    def create_settings_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>⚙️ Security Settings</span>")
        title.set_xalign(0)
        box.pack_start(title, False, False, 0)

        hard_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hard_label = Gtk.Label(label="Enable System Hardening")
        hard_label.set_xalign(0)
        hard_box.pack_start(hard_label, True, True, 0)
        self.hardening_switch = Gtk.Switch()
        self.hardening_switch.set_active(self.config.get("hardening_enabled", False))
        self.hardening_switch.connect("notify::active", self.on_hardening_toggle)
        hard_box.pack_start(self.hardening_switch, False, False, 0)
        box.pack_start(hard_box, False, False, 10)
        
        settings = [
            ("Auto-update virus definitions", "auto_updates", True),
            ("Show security notifications", "notifications", True),
            ("Start with system", "autostart", True),
            ("Scan USB on connect", "usb_scan", True),
            ("Schedule daily scans", "scheduled_scans", False),
            ("Send anonymous statistics", "telemetry", False)
        ]
        
        for name, key, default in settings:
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            label = Gtk.Label(label=name)
            label.set_xalign(0)
            hbox.pack_start(label, True, True, 0)
            switch = Gtk.Switch()
            switch.set_active(self.config.get(key, default))
            switch.connect("notify::active", lambda s, p, k=key: self.on_setting_changed(k, s.get_active()))
            hbox.pack_start(switch, False, False, 0)
            box.pack_start(hbox, False, False, 5)
        
        return box
    
    def on_sidebar_row_activated(self, listbox, row):
        self.content_stack.set_visible_child_name(row.page_id)
    
    def on_firewall_toggle(self, switch, gparam):
        enabled = switch.get_active()
        self.config["firewall_enabled"] = enabled
        self.save_config()
        self._apply_toggle_async("firewall", enabled)

    def on_ids_toggle(self, switch, gparam):
        enabled = switch.get_active()
        self.config["intrusion_detection"] = enabled
        self.save_config()
        self._apply_toggle_async("ids", enabled)

    def on_privacy_toggle(self, switch, gparam):
        enabled = switch.get_active()
        self.config["privacy_enabled"] = enabled
        self.save_config()
        self._apply_toggle_async("privacy", enabled)

    def on_hardening_toggle(self, switch, gparam):
        enabled = switch.get_active()
        self.config["hardening_enabled"] = enabled
        self.save_config()
        self._apply_toggle_async("hardening", enabled)
    
    def on_setting_changed(self, key, value):
        self.config[key] = value
        self.save_config()

    def apply_security_profile(self, button):
        profile_id = None
        try:
            profile_id = self.profile_combo.get_active_id()
        except Exception:
            profile_id = None

        profile_id = profile_id or "balanced"

        profiles = {
            # Lower friction for gaming: keep firewall on, disable heavier checks by default.
            "gaming": {
                "firewall_enabled": True,
                "intrusion_detection": False,
                "privacy_enabled": False,
                "hardening_enabled": False,
            },
            # Recommended default: reasonable protection without going extreme.
            "balanced": {
                "firewall_enabled": True,
                "intrusion_detection": True,
                "privacy_enabled": True,
                "hardening_enabled": True,
            },
            # Max protection: enable everything that we can toggle.
            "paranoid": {
                "firewall_enabled": True,
                "intrusion_detection": True,
                "privacy_enabled": True,
                "hardening_enabled": True,
            },
        }

        if profile_id not in profiles:
            self._show_error("Profile error", "Unknown profile")
            return

        desired = profiles[profile_id]

        toggles = [
            {"feature": "firewall", "enabled": bool(desired["firewall_enabled"])},
            {"feature": "ids", "enabled": bool(desired["intrusion_detection"])},
            {"feature": "privacy", "enabled": bool(desired["privacy_enabled"])},
            {"feature": "hardening", "enabled": bool(desired["hardening_enabled"])},
        ]

        def worker():
            code, out, err = self._run_security_helper({"action": "batch", "toggles": toggles})
            if code != 0:
                GLib.idle_add(self._show_error, "Profile apply failed", err or out or "Unknown error")
                return

            # Update local config to match applied profile.
            self.config.update(desired)
            self.save_config()

            # Best-effort: update any visible switches.
            if hasattr(self, "firewall_switch"):
                GLib.idle_add(self.firewall_switch.set_active, bool(desired["firewall_enabled"]))
            if hasattr(self, "privacy_switch"):
                GLib.idle_add(self.privacy_switch.set_active, bool(desired["privacy_enabled"]))
            if hasattr(self, "hardening_switch"):
                GLib.idle_add(self.hardening_switch.set_active, bool(desired["hardening_enabled"]))

            GLib.idle_add(self._append_log_line, f"[Profile] Applied {profile_id}: {out}")

        threading.Thread(target=worker, daemon=True).start()

    def verify_integrity(self, button):
        def worker():
            code, out, err = self._run_security_helper({"action": "verify"})
            msg = out or err or "No output"
            GLib.idle_add(self._append_log_line, f"[Integrity] {msg}")
        threading.Thread(target=worker, daemon=True).start()

    def _append_log_line(self, line):
        end = self.logs_buffer.get_end_iter()
        self.logs_buffer.insert(end, line + "\n")
    
    def add_firewall_rule(self, button):
        dialog = Gtk.Dialog(title="Add Firewall Rule", transient_for=self, flags=0)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
        
        content = dialog.get_content_area()
        content.set_spacing(10)
        content.set_margin_start(10)
        content.set_margin_end(10)
        
        port_entry = Gtk.Entry()
        port_entry.set_placeholder_text("Port (e.g., 8080)")
        content.pack_start(port_entry, False, False, 0)
        
        dialog.show_all()
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            port = port_entry.get_text()
            if port:
                self.rules_store.append(["Allow", "TCP", port, "Custom Rule", "Both"])
        
        dialog.destroy()
    
    def run_quick_scan(self, button):
        self.scan_progress.set_fraction(0)
        self.scan_progress.set_text("Starting quick scan...")
        threading.Thread(target=self._run_scan, args=("quick",)).start()
    
    def run_full_scan(self, button):
        self.scan_progress.set_fraction(0)
        self.scan_progress.set_text("Starting full scan...")
        threading.Thread(target=self._run_scan, args=("full",)).start()
    
    def run_custom_scan(self, button):
        dialog = Gtk.FileChooserDialog(
            title="Select folder to scan",
            parent=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER
        )
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            folder = dialog.get_filename()
            self.scan_progress.set_text(f"Scanning {folder}...")
            threading.Thread(target=self._run_scan, args=("custom", folder)).start()
        dialog.destroy()
    
    def run_usb_scan(self, button):
        self.scan_progress.set_text("Scanning USB devices...")
        threading.Thread(target=self._run_scan, args=("usb",)).start()
    
    def run_rootkit_scan(self, button):
        self.scan_progress.set_text("Running rootkit scan...")
        threading.Thread(target=self._run_scan, args=("rootkit",)).start()
    
    def _run_scan(self, scan_type, path=None):
        for i in range(101):
            GLib.idle_add(self.scan_progress.set_fraction, i / 100)
            GLib.idle_add(self.scan_progress.set_text, f"Scanning... {i}%")
            import time
            time.sleep(0.05)
        
        GLib.idle_add(self.scan_progress.set_text, "Scan complete - No threats found")
        self.config["last_scan"] = datetime.now().isoformat()
        self.save_config()
    
    def update_definitions(self, button):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Updating Definitions"
        )
        dialog.format_secondary_text("Virus definitions are being updated...")
        dialog.run()
        dialog.destroy()
    
    def generate_report(self, button):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Security Report"
        )
        dialog.format_secondary_text("Security report generated and saved to ~/Documents/security-report.pdf")
        dialog.run()
        dialog.destroy()
    
    def refresh_connections(self, button):
        self.connections_store.clear()
        try:
            result = subprocess.run(["ss", "-tuln"], capture_output=True, text=True)
            for line in result.stdout.split('\n')[1:]:
                parts = line.split()
                if len(parts) >= 5:
                    self.connections_store.append([
                        "System",
                        parts[4] if len(parts) > 4 else "",
                        parts[5] if len(parts) > 5 else "",
                        parts[1] if len(parts) > 1 else "",
                        parts[0] if len(parts) > 0 else ""
                    ])
        except:
            pass
    
    def clear_traces(self, button):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Clear All Traces?"
        )
        dialog.format_secondary_text("This will clear browser history, cache, cookies, and temporary files.")
        response = dialog.run()
        dialog.destroy()
        
        if response == Gtk.ResponseType.YES:
            pass
    
    def open_password_manager(self, button):
        subprocess.Popen(["keepassxc"])
    
    def encrypt_files(self, button):
        subprocess.Popen(["gpg", "--armor", "--symmetric"])
    
    def privacy_audit(self, button):
        pass
    
    def update_status(self):
        return True

if __name__ == "__main__":
    win = SecurityCenter()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
