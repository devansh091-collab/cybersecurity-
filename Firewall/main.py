# main.py
import customtkinter as ctk
from header import Header
from footer import Footer
from sidebar import Sidebar
from body import Body

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class DevilFirewallApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("DevilFirewall — Indian Modern Firewall")
        self.geometry("1200x720")

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.header = Header(self)
        self.header.grid(row=0, column=0, columnspan=2, sticky="nsew")

        self.sidebar = Sidebar(self, self.change_page)
        self.sidebar.grid(row=1, column=0, sticky="nsw")

        self.body = Body(self)
        self.body.grid(row=1, column=1, sticky="nsew")

        self.footer = Footer(self)
        self.footer.grid(row=2, column=0, columnspan=2, sticky="nsew")

    def change_page(self, page_name: str):
        if page_name == "Dashboard":
            self.body.show_dashboard()
        elif page_name == "Firewall Control":
            self.body.show_firewall_control()
        elif page_name == "Live Monitor":
            self.body.show_monitor()
        elif page_name == "IDS Alerts":
            self.body.show_ids()
        elif page_name == "Logs":
            self.body.show_logs()
        else:
            self.body.show_dashboard()

if __name__ == "__main__":
    app = DevilFirewallApp()
    app.mainloop()
