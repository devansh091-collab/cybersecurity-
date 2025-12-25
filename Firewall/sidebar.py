# sidebar.py
import customtkinter as ctk
import theme

class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, callback):
        super().__init__(parent, width=220, fg_color=theme.SECONDARY)
        self.pack_propagate(False)

        ctk.CTkLabel(self, text="⚙️ Controls", font=("Arial", 16, "bold"), text_color=theme.WHITE).pack(pady=(12, 6))

        items = [
            "Dashboard",
            "Firewall Control",
            "Live Monitor",
            "IDS Alerts",
            "Logs",
            "Settings",
        ]
        for name in items:
            self._btn(name, callback)

    def _btn(self, text, cb):
        ctk.CTkButton(
            self, text=text, command=lambda: cb(text),
            corner_radius=8, fg_color=theme.CARD, text_color=theme.WHITE
        ).pack(fill="x", padx=12, pady=6)
