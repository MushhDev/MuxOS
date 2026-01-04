#!/usr/bin/env python3

import json
import os
import sys
import subprocess
import time
import hashlib
import hmac
import secrets
import shutil


def run(cmd, input_text=None):
    return subprocess.run(cmd, input=input_text, text=True, capture_output=True)


def ensure_dir(path: str, mode: int = 0o755) -> None:
    os.makedirs(path, exist_ok=True)
    try:
        os.chmod(path, mode)
    except Exception:
        pass


def eprint(msg: str) -> None:
    sys.stderr.write(msg + "\n")


def _read_file(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def _write_file(path: str, data: bytes, mode: int = 0o600) -> None:
    ensure_dir(os.path.dirname(path), 0o755)
    with open(path, "wb") as f:
        f.write(data)
    try:
        os.chmod(path, mode)
    except Exception:
        pass


def _backup_path(feature: str, rel: str) -> str:
    safe_rel = rel.lstrip("/")
    return os.path.join("/var/lib/muxos/security/backups", feature, safe_rel)


def backup_file(feature: str, path: str) -> None:
    if not os.path.exists(path):
        return
    dest = _backup_path(feature, path)
    ensure_dir(os.path.dirname(dest), 0o755)
    shutil.copy2(path, dest)


def restore_file(feature: str, path: str) -> None:
    src = _backup_path(feature, path)
    if not os.path.exists(src):
        return
    ensure_dir(os.path.dirname(path), 0o755)
    shutil.copy2(src, path)


def get_key() -> bytes:
    key_path = "/var/lib/muxos/security/journal.key"
    if os.path.exists(key_path):
        return _read_file(key_path)
    ensure_dir("/var/lib/muxos/security", 0o755)
    key = secrets.token_bytes(32)
    _write_file(key_path, key, 0o600)
    return key


def journal(event: dict) -> None:
    ensure_dir("/var/lib/muxos/security", 0o755)
    log_path = "/var/lib/muxos/security/journal.log"

    prev = ""
    if os.path.exists(log_path):
        try:
            with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    prev = line
        except Exception:
            prev = ""

    prev_hash = ""
    try:
        if prev:
            prev_obj = json.loads(prev)
            prev_hash = prev_obj.get("hash", "")
    except Exception:
        prev_hash = ""

    event = dict(event)
    event["ts"] = int(time.time())
    event["prev_hash"] = prev_hash

    payload = json.dumps(event, sort_keys=True, separators=(",", ":")).encode("utf-8")
    key = get_key()
    digest = hmac.new(key, payload, hashlib.sha256).hexdigest()
    event["hash"] = digest

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, sort_keys=True) + "\n")


def verify_journal() -> dict:
    log_path = "/var/lib/muxos/security/journal.log"
    key_path = "/var/lib/muxos/security/journal.key"
    if not os.path.exists(log_path):
        return {"ok": True, "entries": 0}
    if not os.path.exists(key_path):
        return {"ok": False, "error": "journal.key missing"}

    key = _read_file(key_path)
    prev_hash = ""
    entries = 0
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entries += 1
            try:
                obj = json.loads(line)
            except Exception:
                return {"ok": False, "entries": entries, "error": "invalid json", "line": entries}

            expected_prev = obj.get("prev_hash", "")
            if expected_prev != prev_hash:
                return {"ok": False, "entries": entries, "error": "prev_hash mismatch", "line": entries}

            provided_hash = obj.get("hash", "")
            if not provided_hash:
                return {"ok": False, "entries": entries, "error": "missing hash", "line": entries}

            check_obj = dict(obj)
            check_obj.pop("hash", None)
            payload = json.dumps(check_obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
            computed = hmac.new(key, payload, hashlib.sha256).hexdigest()
            if computed != provided_hash:
                return {"ok": False, "entries": entries, "error": "hmac mismatch", "line": entries}

            prev_hash = provided_hash

    return {"ok": True, "entries": entries}


def _service(action: str, name: str):
    if shutil.which("systemctl"):
        run(["systemctl", action, name])


def enable_firewall():
    if shutil.which("ufw"):
        run(["ufw", "--force", "enable"])


def disable_firewall():
    if shutil.which("ufw"):
        run(["ufw", "--force", "disable"])


def enable_ids():
    script = "/usr/share/muxos/security/intrusion-detection.sh"
    if os.path.exists(script):
        r = run(["bash", script])
        if r.returncode != 0:
            raise RuntimeError((r.stderr or r.stdout or "IDS enable failed").strip())


def disable_ids():
    try:
        if os.path.exists("/etc/cron.d/muxos-security"):
            os.remove("/etc/cron.d/muxos-security")
    except Exception:
        pass

    _service("stop", "auditd")
    _service("disable", "auditd")


def enable_privacy():
    feature = "privacy"
    for p in [
        "/etc/hosts",
        "/etc/sysctl.d/99-muxos-privacy.conf",
        "/etc/bash.bashrc",
        "/etc/systemd/resolved.conf.d/dns-over-tls.conf",
        "/etc/NetworkManager/conf.d/30-mac-randomization.conf",
        "/etc/firefox-esr/firefox-esr.js",
    ]:
        backup_file(feature, p)

    script = "/usr/share/muxos/security/privacy-settings.sh"
    if os.path.exists(script):
        r = run(["bash", script])
        if r.returncode != 0:
            raise RuntimeError((r.stderr or r.stdout or "Privacy enable failed").strip())


def disable_privacy():
    feature = "privacy"
    for p in [
        "/etc/hosts",
        "/etc/sysctl.d/99-muxos-privacy.conf",
        "/etc/bash.bashrc",
        "/etc/systemd/resolved.conf.d/dns-over-tls.conf",
        "/etc/NetworkManager/conf.d/30-mac-randomization.conf",
        "/etc/firefox-esr/firefox-esr.js",
    ]:
        restore_file(feature, p)

    if shutil.which("sysctl"):
        run(["sysctl", "--system"])

    _service("restart", "NetworkManager")
    _service("restart", "systemd-resolved")


def enable_hardening():
    feature = "hardening"
    for p in [
        "/etc/sysctl.d/99-muxos-security.conf",
        "/etc/login.defs",
        "/etc/fail2ban/jail.local",
        "/etc/apt/apt.conf.d/50unattended-upgrades",
        "/etc/fstab",
    ]:
        backup_file(feature, p)

    script = "/usr/share/muxos/security/system-hardening.sh"
    if os.path.exists(script):
        r = run(["bash", script])
        if r.returncode != 0:
            raise RuntimeError((r.stderr or r.stdout or "Hardening enable failed").strip())


def disable_hardening():
    feature = "hardening"
    for p in [
        "/etc/sysctl.d/99-muxos-security.conf",
        "/etc/login.defs",
        "/etc/fail2ban/jail.local",
        "/etc/apt/apt.conf.d/50unattended-upgrades",
        "/etc/fstab",
    ]:
        restore_file(feature, p)

    if shutil.which("sysctl"):
        run(["sysctl", "--system"])

    _service("stop", "fail2ban")
    _service("disable", "fail2ban")


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
        action = payload.get("action") or "toggle"
        feature = payload.get("feature")
        enabled = bool(payload.get("enabled"))

        if os.geteuid() != 0:
            eprint("This helper must run as root")
            return 2

        if action == "verify":
            result = verify_journal()
            sys.stdout.write(json.dumps(result))
            return 0 if result.get("ok") else 1

        actions = {
            "firewall": (enable_firewall, disable_firewall),
            "ids": (enable_ids, disable_ids),
            "privacy": (enable_privacy, disable_privacy),
            "hardening": (enable_hardening, disable_hardening),
        }

        if action == "batch":
            toggles = payload.get("toggles")
            if not isinstance(toggles, list):
                eprint("Invalid toggles")
                return 2

            summary = {"ok": True, "results": []}
            journal({"type": "security_batch", "status": "start", "count": len(toggles)})
            for item in toggles:
                try:
                    if not isinstance(item, dict):
                        raise RuntimeError("Invalid toggle item")
                    f = item.get("feature")
                    en = bool(item.get("enabled"))
                    if f not in actions:
                        raise RuntimeError("Unknown feature")

                    journal({"type": "security_toggle", "feature": f, "enabled": en, "status": "start"})
                    fn_on, fn_off = actions[f]
                    if en:
                        fn_on()
                    else:
                        fn_off()
                    journal({"type": "security_toggle", "feature": f, "enabled": en, "status": "ok"})
                    summary["results"].append({"feature": f, "enabled": en, "ok": True})
                except Exception as e:
                    summary["ok"] = False
                    summary["results"].append({"feature": item.get("feature") if isinstance(item, dict) else None, "enabled": item.get("enabled") if isinstance(item, dict) else None, "ok": False, "error": str(e)})
                    journal({"type": "security_toggle", "feature": item.get("feature") if isinstance(item, dict) else None, "enabled": item.get("enabled") if isinstance(item, dict) else None, "status": "error", "error": str(e)})

            journal({"type": "security_batch", "status": "ok" if summary["ok"] else "error"})
            sys.stdout.write(json.dumps(summary))
            return 0 if summary["ok"] else 1

        if action != "toggle":
            eprint("Unknown action")
            return 2

        if feature not in actions:
            eprint("Unknown feature")
            return 2

        journal({"type": "security_toggle", "feature": feature, "enabled": enabled, "status": "start"})

        fn_on, fn_off = actions[feature]
        if enabled:
            fn_on()
        else:
            fn_off()

        journal({"type": "security_toggle", "feature": feature, "enabled": enabled, "status": "ok"})
        return 0
    except Exception as e:
        try:
            journal({"type": "security_toggle", "feature": payload.get("feature") if isinstance(payload, dict) else None, "enabled": payload.get("enabled") if isinstance(payload, dict) else None, "status": "error", "error": str(e)})
        except Exception:
            pass
        eprint(str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())
