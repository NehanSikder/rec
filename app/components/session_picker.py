from __future__ import annotations
import customtkinter as ctk
from config.loader import load_pipeline
from core.session import create_session, load_session, list_sessions


class SessionPickerWindow(ctk.CTkToplevel):
    def __init__(self, root) -> None:
        super().__init__(root)
        self.root = root
        self.title("rec — Sessions")
        self.geometry("480x520")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._build()

    def _build(self) -> None:
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="rec", font=ctk.CTkFont(size=28, weight="bold")).grid(
            row=0, column=0, pady=(32, 2)
        )
        ctk.CTkLabel(self, text="Production Pipeline Manager", text_color="#888").grid(
            row=1, column=0, pady=(0, 24)
        )

        # New session
        new_frame = ctk.CTkFrame(self, corner_radius=8)
        new_frame.grid(row=2, column=0, padx=32, sticky="ew", pady=(0, 20))
        new_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(new_frame, text="New Session", font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(12, 4)
        )
        self.title_entry = ctk.CTkEntry(new_frame, placeholder_text="Episode title...")
        self.title_entry.grid(row=1, column=0, padx=16, pady=(0, 12), sticky="ew")
        self.title_entry.bind("<Return>", lambda e: self._create())

        ctk.CTkButton(new_frame, text="Create", width=80, command=self._create).grid(
            row=1, column=1, padx=(0, 16), pady=(0, 12)
        )

        # Existing sessions
        sessions = list_sessions()
        if sessions:
            ctk.CTkLabel(self, text="Recent Sessions", font=ctk.CTkFont(size=13, weight="bold"),
                         text_color="#888").grid(row=3, column=0, padx=32, sticky="w", pady=(0, 6))

            scroll = ctk.CTkScrollableFrame(self, corner_radius=8, height=220)
            scroll.grid(row=4, column=0, padx=32, sticky="nsew", pady=(0, 24))
            scroll.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(4, weight=1)

            for i, meta in enumerate(sessions):
                row_frame = ctk.CTkFrame(scroll, fg_color="transparent")
                row_frame.grid(row=i, column=0, sticky="ew", pady=2)
                row_frame.grid_columnconfigure(0, weight=1)

                ctk.CTkLabel(row_frame, text=meta["title"], anchor="w",
                             font=ctk.CTkFont(size=13)).grid(row=0, column=0, sticky="w", padx=8)
                ctk.CTkLabel(row_frame, text=meta["created_at"][:10], anchor="e",
                             text_color="#666", font=ctk.CTkFont(size=11)).grid(row=0, column=1, padx=8)
                ctk.CTkButton(row_frame, text="Open", width=60, height=26,
                              font=ctk.CTkFont(size=12),
                              command=lambda sid=meta["id"]: self._open(sid)).grid(row=0, column=2, padx=(0, 4))
        else:
            ctk.CTkLabel(self, text="No sessions yet.", text_color="#555").grid(
                row=3, column=0, pady=16
            )

    def _create(self) -> None:
        title = self.title_entry.get().strip()
        if not title:
            return
        pipeline = load_pipeline()
        stage_ids = [s.id for s in pipeline.stages]
        action_ids = {s.id: [a.id for a in s.actions] for s in pipeline.stages}
        session = create_session(title, stage_ids, action_ids)
        self._launch(session)

    def _open(self, session_id: str) -> None:
        session = load_session(session_id)
        self._launch(session)

    def _launch(self, session) -> None:
        from app.windows.main_window import MainWindow
        self.destroy()
        MainWindow(session)

    def _on_close(self) -> None:
        self.root.destroy()
