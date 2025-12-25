# iptables_manager.py
import os
import subprocess

def is_root():
    return os.geteuid() == 0

def _run(cmd):
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True, text=True)
        return True, out.strip()
    except subprocess.CalledProcessError as e:
        return False, (e.output or str(e)).strip()

def _ensure_root():
    if not is_root():
        return False, "Requires root (run with sudo)."

    return True, ""

def block_ip(ip):
    ok, msg = _ensure_root()
    if not ok: return False, msg
    return _run(f"iptables -A INPUT -s {ip} -j DROP")

def allow_ip(ip):
    ok, msg = _ensure_root()
    if not ok: return False, msg
    return _run(f"iptables -D INPUT -s {ip} -j DROP")

def block_port(port):
    ok, msg = _ensure_root()
    if not ok: return False, msg
    return _run(f"iptables -A INPUT -p tcp --dport {port} -j DROP")

def allow_port(port):
    ok, msg = _ensure_root()
    if not ok: return False, msg
    return _run(f"iptables -D INPUT -p tcp --dport {port} -j DROP")

def reset_firewall():
    ok, msg = _ensure_root()
    if not ok: return False, msg
    return _run("iptables -F && iptables -X && iptables -Z")
