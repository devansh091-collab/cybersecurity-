# footer.py
import customtkinter as ctk
import theme
import datetime

class Footer(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=theme.PRIMARY, height=30)
        self.pack_propagate(False)

        year = datetime.datetime.now().year
        ctk.CTkLabel(
            self,
            text=f"© {year} DevilFirewall — Secure India",
            font=theme.FONT_SMALL,
            text_color=theme.WHITE
        ).pack(pady=3)
