from __future__ import annotations
from typing import Callable
import customtkinter as ctk
from config.models import PipelineConfig
from core.session import Session
from core.state_machine import advance_stage, skip_stage, stage_is_complete, pipeline_is_complete
from core.action_runner import run_action
from core.undo_stack import record_action_done, record_stage_advanced, record_stage_skipped, can_undo, undo

STATUS_ICON = {
    "pending": ("○", "#757575"),
    "running": ("◌", "#2196F3"),
    "done":    ("✓", "#4CAF50"),
    "failed":  ("✗", "#F44336"),
    "skipped": ("—", "#9E9E9E"),
}


class ActionList(ctk.CTkFrame):
    def __init__(self, parent, session: Session, pipeline: PipelineConfig, on_change: Callable) -> None:
        super().__init__(parent, fg_color="transparent")
        self.session = session
        self.pipeline = pipeline
        self.on_change = on_change

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Stage label
        self.stage_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=15, weight="bold"))
        self.stage_label.grid(row=0, column=0, sticky="w", pady=(0, 8))

        # Scrollable action rows
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="#1e1e1e", corner_radius=8)
        self.scroll_frame.grid(row=1, column=0, sticky="nsew")
        self.grid_rowconfigure(1, weight=1)

        # Button row
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", pady=(12, 0))

        self.btn_undo = ctk.CTkButton(btn_frame, text="Undo", width=80, command=self._on_undo, fg_color="#424242")
        self.btn_undo.pack(side="left", padx=(0, 8))

        self.btn_skip = ctk.CTkButton(btn_frame, text="Skip Stage", width=100, command=self._on_skip, fg_color="#424242")
        self.btn_skip.pack(side="left", padx=(0, 8))

        self.btn_complete = ctk.CTkButton(btn_frame, text="Complete Stage →", width=140, command=self._on_complete)
        self.btn_complete.pack(side="right")

        self._action_rows: list = []

    def update(self, session: Session) -> None:
        self.session = session
        self._rebuild_rows()
        self._refresh_buttons()

    def _rebuild_rows(self) -> None:
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self._action_rows = []

        stage_state = self.session.get_stage(self.session.current_stage_id)
        stage_config = next((s for s in self.pipeline.stages if s.id == self.session.current_stage_id), None)
        if not stage_state or not stage_config:
            return

        self.stage_label.configure(text=stage_config.label)

        for action_config in stage_config.actions:
            action_state = self.session.get_action(stage_state.stage_id, action_config.id)
            if not action_state:
                continue

            row = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=4)

            icon, color = STATUS_ICON.get(action_state.status, ("○", "#757575"))
            icon_lbl = ctk.CTkLabel(row, text=icon, text_color=color, width=20,
                                    font=ctk.CTkFont(size=14))
            icon_lbl.pack(side="left")

            name_lbl = ctk.CTkLabel(row, text=action_config.label, anchor="w",
                                    font=ctk.CTkFont(size=13))
            name_lbl.pack(side="left", padx=(8, 0), fill="x", expand=True)

            if action_state.status in ("pending", "failed"):
                btn = ctk.CTkButton(
                    row, text="Run", width=60, height=26,
                    font=ctk.CTkFont(size=12),
                    command=lambda ac=action_config, st=action_state: self._on_run(ac, st),
                )
                btn.pack(side="right")

            self._action_rows.append((action_config, action_state, row))

    def _refresh_buttons(self) -> None:
        self.btn_undo.configure(state="normal" if can_undo(self.session) else "disabled")
        complete = stage_is_complete(self.session)
        finished = pipeline_is_complete(self.session)
        self.btn_complete.configure(
            state="normal" if complete and not finished else "disabled",
            text="Pipeline Complete" if finished else "Complete Stage →",
        )

    def _on_run(self, action_config, action_state) -> None:
        stage_config = next((s for s in self.pipeline.stages if s.id == self.session.current_stage_id), None)
        success = run_action(action_config, action_state, self.session)
        if success:
            record_action_done(self.session, self.session.current_stage_id, action_config.id)
        self.on_change()

    def _on_complete(self) -> None:
        from_id = self.session.current_stage_id
        advanced = advance_stage(self.session, self.pipeline)
        if advanced:
            record_stage_advanced(self.session, from_id, self.session.current_stage_id)
        self.on_change()

    def _on_skip(self) -> None:
        stage_id = self.session.current_stage_id
        skip_stage(self.session, self.pipeline)
        record_stage_skipped(self.session, stage_id)
        self.on_change()

    def _on_undo(self) -> None:
        undo(self.session, self.pipeline)
        self.on_change()
