from __future__ import annotations
import customtkinter as ctk
from config.loader import load_pipeline
from core.session import Session
from app.components.progress_bar import ProgressBar
from app.components.action_list import ActionList


class MainWindow(ctk.CTkToplevel):
    def __init__(self, session: Session) -> None:
        super().__init__()
        self.session = session
        self.pipeline = load_pipeline()

        self.title(f"rec — {session.title}")
        self.geometry("820x560")
        self.minsize(700, 480)
        self.resizable(True, True)

        self._build()
        self.refresh()

    def _build(self) -> None:
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Top: progress bar
        self.progress_bar = ProgressBar(self, self.pipeline)
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 0))

        # Center: action list
        self.action_list = ActionList(self, self.session, self.pipeline, on_change=self.refresh)
        self.action_list.grid(row=1, column=0, sticky="nsew", padx=24, pady=16)

    def refresh(self) -> None:
        self.progress_bar.update(self.session)
        self.action_list.update(self.session)
