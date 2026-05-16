from __future__ import annotations
import customtkinter as ctk
from app.windows.session_picker import SessionPickerWindow

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def start() -> None:
    root = ctk.CTk()
    root.withdraw()
    SessionPickerWindow(root)
    root.mainloop()
