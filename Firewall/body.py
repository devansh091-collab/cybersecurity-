# body.py
import customtkinter as ctk
import theme
import time

from log_manager import LogManager
from iptables_manager import block_ip, allow_ip, block_port, allow_port, reset_firewall
from packet_monitor import PacketMonitor

try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    _HAS_MPL = True
except Exception:
    _HAS_MPL = False

class Body(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=theme.SECONDARY)

        # core services
        self.logs = LogManager()
        self.event_q = __import__("queue").Queue()
        self.monitor = PacketMonitor(out_queue=self.event_q, poll_sec=1.0)
        self.monitor.start()

        # live state
        self.stats = {"packets": 0, "alerts": 0, "blocked": 0}
        self.last_page = None

        # container (swap pages inside)
        self.page = ctk.CTkFrame(self, fg_color=theme.SECONDARY)
        self.page.pack(fill="both", expand=True, padx=14, pady=14)

        self.show_dashboard()
        self.after(350, self._pump_events)

    def _clear(self):
        for w in self.page.winfo_children():
            w.destroy()

    def _pump_events(self):
        # drain queue and update stats + logs
        while True:
            try:
                ev = self.event_q.get_nowait()
            except Exception:
                break

            if ev["kind"] == "packet":
                self.stats["packets"] += 1
            elif ev["kind"] == "alert":
                self.stats["alerts"] += 1
                self.logs.warn(ev["data"]["message"])
        # refresh dashboard if it is open
        if self.last_page == "dashboard":
            self.show_dashboard()
        self.after(350, self._pump_events)

    # -------------------- Pages --------------------
    def show_dashboard(self):
        self.last_page = "dashboard"
        self._clear()

        ctk.CTkLabel(self.page, text="Dashboard", font=theme.FONT_TITLE, text_color=theme.WHITE).pack(anchor="w")

        # cards
        cards = ctk.CTkFrame(self.page, fg_color=theme.SECONDARY)
        cards.pack(fill="x", pady=10)

        def make_card(title, value, hint):
            f = ctk.CTkFrame(cards, fg_color=theme.CARD, corner_radius=12)
            f.pack(side="left", expand=True, fill="x", padx=6, pady=6)
            ctk.CTkLabel(f, text=title, font=theme.FONT_SUB, text_color=theme.MUTE).pack(anchor="w", padx=10, pady=(10, 0))
            ctk.CTkLabel(f, text=str(value), font=("Arial", 22, "bold"), text_color=theme.WHITE).pack(anchor="w", padx=10)
            ctk.CTkLabel(f, text=hint, font=theme.FONT_SMALL, text_color=theme.MUTE).pack(anchor="w", padx=10, pady=(0,10))

        make_card("Packets (since start)", self.stats["packets"], "Live monitored traffic events")
        make_card("IDS Alerts", self.stats["alerts"], "Heuristic warnings generated")
        make_card("Rules Applied", self.stats["blocked"], "Blocks issued from UI")

        # charts (optional)
        if _HAS_MPL:
            fig = Figure(figsize=(6, 2.2), dpi=100)
            ax = fig.add_subplot(111)
            ax.bar(["packets", "alerts", "blocks"],
                   [self.stats["packets"], self.stats["alerts"], self.stats["blocked"]])
            ax.set_title("Activity snapshot")
            ax.set_ylabel("count")

            canvas = FigureCanvasTkAgg(fig, master=self.page)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="x", pady=10)
        else:
            ctk.CTkLabel(
                self.page,
                text="matplotlib not installed (charts disabled). Install it for graphs.",
                font=theme.FONT_SMALL, text_color=theme.MUTE
            ).pack(anchor="w", pady=6)

    def show_firewall_control(self):
        self.last_page = "fw"
        self._clear()

        ctk.CTkLabel(self.page, text="Firewall Control", font=theme.FONT_TITLE, text_color=theme.WHITE).pack(anchor="w")

        ctk.CTkLabel(self.page, text="IP / Port actions (iptables)", font=theme.FONT_SUB, text_color=theme.MUTE).pack(anchor="w", pady=(0,10))

        ip = ctk.CTkEntry(self.page, placeholder_text="IP (e.g., 192.168.1.100)")
        ip.pack(fill="x", pady=6)
        port = ctk.CTkEntry(self.page, placeholder_text="Port (e.g., 443)")
        port.pack(fill="x", pady=6)

        status = ctk.CTkLabel(self.page, text="Status: idle", font=theme.FONT_SUB, text_color=theme.WHITE)
        status.pack(anchor="w", pady=(8, 12))

        def do(action):
            if action == "block_ip":
                ok, msg = block_ip(ip.get().strip())
                if ok: self.stats["blocked"] += 1
            elif action == "allow_ip":
                ok, msg = allow_ip(ip.get().strip())
            elif action == "block_port":
                ok, msg = block_port(port.get().strip())
                if ok: self.stats["blocked"] += 1
            else:
                ok, msg = allow_port(port.get().strip())

            level = "INFO" if ok else "ERROR"
            self.logs.log(level, f"{action} -> {msg}")
            status.configure(text=f"Status: {msg}")

        ctk.CTkButton(self.page, text="Block IP", command=lambda: do("block_ip"), fg_color=theme.DANGER).pack(fill="x", pady=4)
        ctk.CTkButton(self.page, text="Allow IP", command=lambda: do("allow_ip"), fg_color=theme.ACCENT).pack(fill="x", pady=4)
        ctk.CTkButton(self.page, text="Block Port", command=lambda: do("block_port"), fg_color=theme.DANGER).pack(fill="x", pady=4)
        ctk.CTkButton(self.page, text="Allow Port", command=lambda: do("allow_port"), fg_color=theme.ACCENT).pack(fill="x", pady=4)

        def reset():
            ok, msg = reset_firewall()
            self.logs.log("INFO" if ok else "ERROR", f"reset -> {msg}")
            status.configure(text=f"Status: {msg}")

        ctk.CTkButton(self.page, text="Reset Firewall", command=reset, fg_color=theme.WARNING).pack(fill="x", pady=(10, 0))

    def show_monitor(self):
        self.last_page = "monitor"
        self._clear()

        ctk.CTkLabel(self.page, text="Live Monitor", font=theme.FONT_TITLE, text_color=theme.WHITE).pack(anchor="w")
        ctk.CTkLabel(self.page, text="Incoming events (packets / summaries)", font=theme.FONT_SUB, text_color=theme.MUTE).pack(anchor="w", pady=(0,10))

        txt = ctk.CTkTextbox(self.page, height=280)
        txt.pack(fill="both", expand=True)

        def refresh():
            txt.delete("1.0", "end")
            lines = self.logs.read_last(100)
            if not lines:
                txt.insert("end", "No log entries yet.\n")
            else:
                txt.insert("end", "".join(lines))
        refresh()

        ctk.CTkButton(self.page, text="Refresh", command=refresh, fg_color=theme.ACCENT).pack(pady=8)

    def show_ids(self):
        self.last_page = "ids"
        self._clear()

        ctk.CTkLabel(self.page, text="IDS Alerts", font=theme.FONT_TITLE, text_color=theme.WHITE).pack(anchor="w")
        ctk.CTkLabel(self.page, text="Heuristic alerts generated from monitor events", font=theme.FONT_SUB, text_color=theme.MUTE).pack(anchor="w", pady=(0,10))

        txt = ctk.CTkTextbox(self.page, height=280)
        txt.pack(fill="both", expand=True)

        def refresh():
            txt.delete("1.0", "end")
            lines = [ln for ln in self.logs.read_last(500) if "WARN" in ln or "ERROR" in ln]
            txt.insert("end", "".join(lines) if lines else "No alerts yet.\n")

        ctk.CTkButton(self.page, text="Refresh", command=refresh, fg_color=theme.ACCENT).pack(pady=8)
        refresh()

    def show_logs(self):
        self.last_page = "logs"
        self._clear()

        ctk.CTkLabel(self.page, text="Logs", font=theme.FONT_TITLE, text_color=theme.WHITE).pack(anchor="w")
        ctk.CTkLabel(self.page, text="Search across stored logs", font=theme.FONT_SUB, text_color=theme.MUTE).pack(anchor="w", pady=(0,10))

        search = ctk.CTkEntry(self.page, placeholder_text="Type keyword (e.g., block, alert, ERROR)")
        search.pack(fill="x", pady=6)

        txt = ctk.CTkTextbox(self.page, height=280)
        txt.pack(fill="both", expand=True)

        def do_search():
            kw = search.get().strip()
            txt.delete("1.0", "end")
            lines = self.logs.search(kw, n=200)
            txt.insert("end", "".join(lines) if lines else "No matching log lines.\n")

        ctk.CTkButton(self.page, text="Search", command=do_search, fg_color=theme.ACCENT).pack(pady=8)
        do_search()
