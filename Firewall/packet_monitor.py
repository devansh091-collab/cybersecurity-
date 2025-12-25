# packet_monitor.py
import threading
import time
from queue import Queue, Empty

class PacketMonitor(threading.Thread):
    """
    Lightweight monitor.
    Best case: user installs scapy -> we can sniff.
    Fallback: we still run and emit 'simulation' events (no privileges needed).
    """
    def __init__(self, iface=None, out_queue=None, poll_sec=1.0):
        super().__init__(daemon=True)
        self.iface = iface
        self.out = out_queue or Queue()
        self.poll_sec = poll_sec
        self._stop = threading.Event()

        # Try importing scapy (optional)
        try:
            from scapy.all import sniff, IP, TCP, UDP  # type: ignore
            self._scapy = (sniff, IP, TCP, UDP)
        except Exception:
            self._scapy = None

        # IDS state (very simple heuristics)
        self._src_counts = {}   # src -> count in window
        self._last_reset = time.time()

    def stop(self):
        self._stop.set()

    def _push(self, kind, data):
        self.out.put({"ts": time.time(), "kind": kind, "data": data})

    def _reset_window(self):
        self._src_counts.clear()
        self._last_reset = time.time()

    def _ids_check(self, src, dst_port):
        now = time.time()
        if now - self._last_reset > 10:   # 10 sec window
            self._reset_window()

        self._src_counts[src] = self._src_counts.get(src, 0) + 1

        # alert rules (simple + safe)
        if dst_port in {22, 23, 3389, 445}:
            self._push("alert", {
                "level": "WARN",
                "message": f"Suspicious target port {dst_port} reached from {src}"
            })

        if self._src_counts[src] >= 15:
            self._push("alert", {
                "level": "DANGER",
                "message": f"High rate from {src} ({self._src_counts[src]} events / 10s)"
            })

    def run(self):
        if self._scapy is None:
            # No scapy: emit periodic synthetic events (still useful for UI flow)
            i = 0
            while not self._stop.is_set():
                i += 1
                self._push("packet", {"src": "0.0.0.0", "dst": "127.0.0.1", "proto": "SIM", "info": f"sample {i}"})
                time.sleep(self.poll_sec)
            return

        sniff, IP, TCP, UDP = self._scapy

        def handler(pkt):
            if not pkt.haslayer(IP):
                return
            src = pkt[IP].src
            dst = pkt[IP].dst
            proto = "TCP" if pkt.haslayer(TCP) else ("UDP" if pkt.haslayer(UDP) else "IP")
            port = None
            if pkt.haslayer(TCP):
                port = pkt[TCP].dport
            elif pkt.haslayer(UDP):
                port = pkt[UDP].dport

            self._push("packet", {"src": src, "dst": dst, "proto": proto, "dport": port})
            if port is not None:
                self._ids_check(src, port)

        try:
            sniff(iface=self.iface, prn=handler, store=False, stop_filter=lambda _: self._stop.is_set())
        except Exception as e:
            self._push("alert", {"level":"ERROR", "message": f"Monitor error: {e}"})
