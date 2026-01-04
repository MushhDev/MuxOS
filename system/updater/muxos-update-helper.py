#!/usr/bin/env python3

import json
import os
import sys
import tempfile
import urllib.request
import urllib.error
import tarfile
import shutil
import time
import hashlib


def eprint(msg: str) -> None:
    sys.stderr.write(msg + "\n")


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def copy_with_backup(src: str, dst: str, backup_root: str, rel: str) -> None:
    backup_path = os.path.join(backup_root, rel)
    ensure_dir(os.path.dirname(backup_path))
    ensure_dir(os.path.dirname(dst))

    if os.path.exists(dst):
        shutil.copy2(dst, backup_path)

    shutil.copy2(src, dst)


def chmod_if_exists(path: str, mode: int) -> None:
    try:
        if os.path.exists(path):
            os.chmod(path, mode)
    except Exception:
        pass


def download_tarball(repo: str, ref: str, dest_path: str) -> None:
    url = f"https://codeload.github.com/{repo}/tar.gz/{ref}"
    req = urllib.request.Request(url, headers={"User-Agent": "MuxOS-Updater"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Failed to download {repo}@{ref}: HTTP {e.code}")
    with open(dest_path, "wb") as f:
        f.write(data)


def extract_tarball(tar_path: str, dest_dir: str) -> str:
    with tarfile.open(tar_path, "r:gz") as tf:
        members = tf.getmembers()
        top = None
        for m in members:
            name = m.name.split("/")[0]
            if name:
                top = name
                break
        tf.extractall(dest_dir)
    if not top:
        raise RuntimeError("Invalid tarball")
    return os.path.join(dest_dir, top)


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def apply_update(repo_root: str, backup_root: str) -> dict:
    copied = []

    mapping = []

    src = os.path.join(repo_root, "apps", "welcome", "muxos-welcome.py")
    if os.path.exists(src):
        mapping.append((src, "/usr/bin/muxos-welcome", "usr/bin/muxos-welcome"))

    apps_bin = [
        ("apps/control-panel/muxos-control-panel-v2.py", "/usr/bin/muxos-control-panel", "usr/bin/muxos-control-panel"),
        ("apps/system-monitor/muxos-monitor.py", "/usr/bin/muxos-monitor", "usr/bin/muxos-monitor"),
        ("apps/system-monitor/muxos-hardware-detector.py", "/usr/bin/muxos-hardware-detector", "usr/bin/muxos-hardware-detector"),
        ("apps/system-monitor/muxos-enhanced-monitor.py", "/usr/bin/muxos-enhanced-monitor", "usr/bin/muxos-enhanced-monitor"),
        ("apps/security/muxos-security-center.py", "/usr/bin/muxos-security-center", "usr/bin/muxos-security-center"),
        ("apps/storage/muxos-disk-manager.py", "/usr/bin/muxos-disk-manager", "usr/bin/muxos-disk-manager"),
        ("apps/gaming/muxos-game-center.py", "/usr/bin/muxos-game-center", "usr/bin/muxos-game-center"),
        ("apps/utilities/muxos-task-manager.py", "/usr/bin/muxos-task-manager", "usr/bin/muxos-task-manager"),
        ("apps/utilities/muxos-screenshot.py", "/usr/bin/muxos-screenshot", "usr/bin/muxos-screenshot"),
        ("apps/utilities/muxos-notes.py", "/usr/bin/muxos-notes", "usr/bin/muxos-notes"),
        ("apps/utilities/muxos-calculator.py", "/usr/bin/muxos-calculator", "usr/bin/muxos-calculator"),
        ("apps/updater/muxos-updater.py", "/usr/bin/muxos-updater", "usr/bin/muxos-updater"),
    ]

    for rel_src, dst, rel_backup in apps_bin:
        p = os.path.join(repo_root, rel_src)
        if os.path.exists(p):
            mapping.append((p, dst, rel_backup))

    for desktop in [
        "apps/desktop-entries/muxos-hardware-detector.desktop",
        "apps/desktop-entries/muxos-enhanced-monitor.desktop",
        "apps/desktop-entries/muxos-welcome.desktop",
        "apps/desktop-entries/muxos-security-center.desktop",
        "apps/desktop-entries/muxos-task-manager.desktop",
        "apps/desktop-entries/muxos-disk-manager.desktop",
        "apps/desktop-entries/muxos-game-center.desktop",
        "apps/desktop-entries/muxos-screenshot.desktop",
        "apps/desktop-entries/muxos-notes.desktop",
        "apps/desktop-entries/muxos-calculator.desktop",
    ]:
        p = os.path.join(repo_root, desktop)
        if os.path.exists(p):
            bn = os.path.basename(p)
            mapping.append((p, f"/usr/share/applications/{bn}", f"usr/share/applications/{bn}"))

    for script in [
        ("system/drivers/detect-hardware.sh", "/usr/share/muxos/drivers/detect-hardware.sh", "usr/share/muxos/drivers/detect-hardware.sh"),
        ("system/drivers/detect-hardware-complete.sh", "/usr/share/muxos/drivers/detect-hardware-complete.sh", "usr/share/muxos/drivers/detect-hardware-complete.sh"),
        ("system/security/firewall-rules.sh", "/usr/share/muxos/security/firewall-rules.sh", "usr/share/muxos/security/firewall-rules.sh"),
        ("system/security/intrusion-detection.sh", "/usr/share/muxos/security/intrusion-detection.sh", "usr/share/muxos/security/intrusion-detection.sh"),
        ("system/security/privacy-settings.sh", "/usr/share/muxos/security/privacy-settings.sh", "usr/share/muxos/security/privacy-settings.sh"),
        ("system/security/system-hardening.sh", "/usr/share/muxos/security/system-hardening.sh", "usr/share/muxos/security/system-hardening.sh"),
        ("system/security/muxos-security-helper.py", "/usr/lib/muxos/muxos-security-helper.py", "usr/lib/muxos/muxos-security-helper.py"),
        ("system/setup/muxos-firstboot-helper.py", "/usr/lib/muxos/muxos-firstboot-helper.py", "usr/lib/muxos/muxos-firstboot-helper.py"),
        ("system/polkit/com.muxos.firstboot.policy", "/usr/share/polkit-1/actions/com.muxos.firstboot.policy", "usr/share/polkit-1/actions/com.muxos.firstboot.policy"),
        ("system/polkit/com.muxos.security.policy", "/usr/share/polkit-1/actions/com.muxos.security.policy", "usr/share/polkit-1/actions/com.muxos.security.policy"),
        ("system/polkit/com.muxos.updater.policy", "/usr/share/polkit-1/actions/com.muxos.updater.policy", "usr/share/polkit-1/actions/com.muxos.updater.policy"),
        ("system/updater/muxos-update-helper.py", "/usr/lib/muxos/muxos-update-helper.py", "usr/lib/muxos/muxos-update-helper.py"),
    ]:
        p = os.path.join(repo_root, script[0])
        if os.path.exists(p):
            mapping.append((p, script[1], script[2]))

    conf = os.path.join(repo_root, "config", "muxos.conf")
    if os.path.exists(conf):
        mapping.append((conf, "/etc/muxos.conf", "etc/muxos.conf"))
        mapping.append((conf, "/usr/share/muxos/muxos.conf", "usr/share/muxos/muxos.conf"))

    for src_path, dst_path, rel_backup in mapping:
        copy_with_backup(src_path, dst_path, backup_root, rel_backup)
        copied.append({"src": src_path, "dst": dst_path, "sha256": sha256_file(dst_path)})

    for p in [
        "/usr/bin/muxos-welcome",
        "/usr/bin/muxos-updater",
        "/usr/bin/muxos-control-panel",
        "/usr/bin/muxos-monitor",
        "/usr/bin/muxos-hardware-detector",
        "/usr/bin/muxos-enhanced-monitor",
        "/usr/bin/muxos-security-center",
        "/usr/bin/muxos-disk-manager",
        "/usr/bin/muxos-game-center",
        "/usr/bin/muxos-task-manager",
        "/usr/bin/muxos-screenshot",
        "/usr/bin/muxos-notes",
        "/usr/bin/muxos-calculator",
        "/usr/lib/muxos/muxos-firstboot-helper.py",
        "/usr/lib/muxos/muxos-security-helper.py",
        "/usr/lib/muxos/muxos-update-helper.py",
        "/usr/share/muxos/drivers/detect-hardware.sh",
        "/usr/share/muxos/drivers/detect-hardware-complete.sh",
        "/usr/share/muxos/security/firewall-rules.sh",
        "/usr/share/muxos/security/intrusion-detection.sh",
        "/usr/share/muxos/security/privacy-settings.sh",
        "/usr/share/muxos/security/system-hardening.sh",
    ]:
        chmod_if_exists(p, 0o755)

    return {"copied": copied}


def rollback(update_id: str) -> dict:
    base = "/var/lib/muxos/updates"
    backup_root = os.path.join(base, "backups", update_id)
    state_path = os.path.join(base, "state", f"{update_id}.json")
    if not os.path.exists(state_path):
        raise RuntimeError("Unknown update id")

    with open(state_path, "r", encoding="utf-8") as f:
        state = json.load(f)

    restored = []
    for item in state.get("copied", []):
        dst = item.get("dst")
        rel = item.get("dst", "").lstrip("/")
        src = os.path.join(backup_root, rel)
        if dst and os.path.exists(src):
            ensure_dir(os.path.dirname(dst))
            shutil.copy2(src, dst)
            restored.append(dst)

    return {"restored": restored}


def main() -> int:
    if os.geteuid() != 0:
        eprint("Must run as root")
        return 2

    payload = json.loads(sys.stdin.read() or "{}")
    action = payload.get("action")

    ensure_dir("/var/lib/muxos/updates")
    ensure_dir("/var/lib/muxos/updates/state")
    ensure_dir("/var/lib/muxos/updates/backups")

    if action == "rollback":
        update_id = payload.get("update_id")
        if not update_id:
            eprint("update_id required")
            return 2
        result = rollback(update_id)
        sys.stdout.write(json.dumps({"ok": True, "result": result}))
        return 0

    if action != "install":
        eprint("Unknown action")
        return 2

    repo = payload.get("repo") or "MushhDev/MuxOS"
    ref = payload.get("ref")
    if not ref:
        eprint("ref required (use immutable tag like v1.0.0)")
        return 2

    update_id = time.strftime("%Y%m%d-%H%M%S")
    backup_root = os.path.join("/var/lib/muxos/updates/backups", update_id)

    with tempfile.TemporaryDirectory() as td:
        tar_path = os.path.join(td, "src.tar.gz")
        download_tarball(repo, ref, tar_path)
        src_root = extract_tarball(tar_path, td)

        result = apply_update(src_root, backup_root)
        state_path = os.path.join("/var/lib/muxos/updates/state", f"{update_id}.json")
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump({"update_id": update_id, **result}, f, indent=2)

    sys.stdout.write(json.dumps({"ok": True, "update_id": update_id, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
