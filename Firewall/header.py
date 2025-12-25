# header.py
import customtkinter as ctk
import theme

class Header(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=theme.PRIMARY, height=60)
        self.pack_propagate(False)

        ctk.CTkLabel(self, text="🔥 DevilFirewall", font=theme.FONT_TITLE, text_color=theme.WHITE).pack(
            side="left", padx=18
        )
        ctk.CTkLabel(
            self, text="Personal security • Traffic monitor • IDS (lightweight)",
            font=theme.FONT_SUB, text_color=theme.MUTE
        ).pack(side="left", padx=10)
