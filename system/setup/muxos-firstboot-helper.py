#!/usr/bin/env python3

import json
import os
import sys
import subprocess
import sqlite3
import secrets
import hashlib
import time
import pwd


def eprint(msg: str) -> None:
    sys.stderr.write(msg + "\n")


def run(cmd, input_text=None):
    return subprocess.run(cmd, input=input_text, text=True, capture_output=True)


def ensure_dir(path: str, mode: int = 0o755) -> None:
    os.makedirs(path, exist_ok=True)
    try:
        os.chmod(path, mode)
    except Exception:
        pass


def pbkdf2_hash_password(password: str, iterations: int = 200_000):
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return salt.hex(), dk.hex(), iterations


def create_or_update_db(db_path: str, username: str, email: str, locale: str, wifi_ssid: str, password: str) -> None:
    ensure_dir(os.path.dirname(db_path), 0o755)

    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT,
                password_salt TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                password_iterations INTEGER NOT NULL,
                locale TEXT,
                wifi_ssid TEXT,
                created_at INTEGER NOT NULL
            )
            """
        )

        salt_hex, hash_hex, iters = pbkdf2_hash_password(password)

        conn.execute(
            """
            INSERT INTO users(username, email, password_salt, password_hash, password_iterations, locale, wifi_ssid, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET
                email=excluded.email,
                password_salt=excluded.password_salt,
                password_hash=excluded.password_hash,
                password_iterations=excluded.password_iterations,
                locale=excluded.locale,
                wifi_ssid=excluded.wifi_ssid
            """,
            (username, email or None, salt_hex, hash_hex, iters, locale, wifi_ssid or None, int(time.time())),
        )
        conn.commit()
    finally:
        conn.close()

    try:
        os.chmod(db_path, 0o600)
    except Exception:
        pass

    try:
        pw = pwd.getpwnam(username)
        os.chown(db_path, pw.pw_uid, pw.pw_gid)
    except Exception:
        pass


def system_user_exists(username: str) -> bool:
    r = run(["id", username])
    return r.returncode == 0


def create_system_user(username: str, password: str) -> None:
    if system_user_exists(username):
        return

    r = run([
        "useradd",
        "-m",
        "-s",
        "/bin/bash",
        "-G",
        "sudo,audio,video,plugdev,netdev",
        username,
    ])
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout or "useradd failed").strip())

    r = run(["chpasswd"], input_text=f"{username}:{password}\n")
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout or "chpasswd failed").strip())


def set_system_locale(locale: str) -> None:
    # Best-effort: write /etc/default/locale.
    # Actual locale generation depends on locales package/config.
    try:
        ensure_dir("/etc/default", 0o755)
        with open("/etc/default/locale", "w", encoding="utf-8") as f:
            f.write(f"LANG={locale}\n")
    except Exception:
        pass

    # Best-effort locale generation for the selected locale.
    if shutil_which("locale-gen"):
        try:
            ensure_dir("/etc", 0o755)
            locale_gen_path = "/etc/locale.gen"
            existing = ""
            if os.path.exists(locale_gen_path):
                with open(locale_gen_path, "r", encoding="utf-8", errors="ignore") as f:
                    existing = f.read()
            line = f"{locale} UTF-8"
            if line not in existing:
                with open(locale_gen_path, "a", encoding="utf-8") as f:
                    if existing and not existing.endswith("\n"):
                        f.write("\n")
                    f.write(line + "\n")
        except Exception:
            pass
        run(["locale-gen", locale])

    if shutil_which("update-locale"):
        run(["update-locale", f"LANG={locale}"])


def shutil_which(cmd: str):
    for p in os.environ.get("PATH", "").split(os.pathsep):
        full = os.path.join(p, cmd)
        if os.path.isfile(full) and os.access(full, os.X_OK):
            return full
    return None


def connect_wifi(ssid: str, password: str) -> None:
    if not ssid:
        return

    nmcli = shutil_which("nmcli")
    if not nmcli:
        raise RuntimeError("nmcli not found")

    cmd = [nmcli, "dev", "wifi", "connect", ssid]
    if password:
        cmd += ["password", password]

    r = run(cmd)
    if r.returncode != 0:
        msg = (r.stderr or r.stdout or "nmcli connect failed").strip()
        raise RuntimeError(msg)


def main() -> int:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}

        locale = payload.get("locale") or "en_US.UTF-8"
        user = payload.get("user") or {}
        wifi = payload.get("wifi") or {}

        username = (user.get("username") or "").strip()
        password = user.get("password") or ""
        email = (user.get("email") or "").strip()

        ssid = (wifi.get("ssid") or "").strip()
        wifi_password = wifi.get("password") or ""

        if not username:
            eprint("Username is required")
            return 2
        if not password:
            eprint("Password is required")
            return 2

        create_system_user(username, password)
        set_system_locale(locale)
        connect_wifi(ssid, wifi_password)

        db_path = "/var/lib/muxos/muxos.db"
        create_or_update_db(db_path, username, email, locale, ssid, password)

        try:
            ensure_dir("/var/lib/muxos", 0o755)
            with open("/var/lib/muxos/.firstboot_complete", "w", encoding="utf-8") as f:
                f.write("ok\n")
        except Exception:
            pass

        return 0
    except Exception as e:
        eprint(str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())
