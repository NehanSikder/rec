from __future__ import annotations
import tkinter as tk
import customtkinter as ctk
from config.models import PipelineConfig
from core.session import Session

COLOR_DONE = "#4CAF50"
COLOR_ACTIVE = "#2196F3"
COLOR_SKIPPED = "#9E9E9E"
COLOR_TODO = "#424242"
COLOR_LINE_DONE = "#4CAF50"
COLOR_LINE_TODO = "#424242"
COLOR_LABEL_DONE = "#4CAF50"
COLOR_LABEL_ACTIVE = "#FFFFFF"
COLOR_LABEL_TODO = "#757575"

NODE_R = 10
LINE_H = 3
LABEL_PAD = 8
ROW_H = 48


class ProgressBar(ctk.CTkFrame):
    def __init__(self, parent, pipeline: PipelineConfig) -> None:
        super().__init__(parent, fg_color="transparent")
        self.pipeline = pipeline
        self.canvas = tk.Canvas(self, bg="#1a1a1a", highlightthickness=0, height=ROW_H)
        self.canvas.pack(fill="x", expand=True)
        self.canvas.bind("<Configure>", lambda e: self._draw(None))
        self._session: Session | None = None

    def update(self, session: Session) -> None:
        self._session = session
        self._draw(session)

    def _draw(self, session: Session | None) -> None:
        self.canvas.delete("all")
        if session is None:
            session = self._session
        if session is None:
            return

        stages = self.pipeline.stages
        n = len(stages)
        if n == 0:
            return

        w = self.canvas.winfo_width()
        if w < 2:
            return

        margin = 40
        spacing = (w - 2 * margin) / (n - 1) if n > 1 else 0
        cx_list = [int(margin + i * spacing) for i in range(n)]
        cy = ROW_H // 2 - 6

        status_map = {s.stage_id: s.status for s in session.stages}

        # Draw lines between nodes
        for i in range(n - 1):
            left_status = status_map.get(stages[i].id, "pending")
            color = COLOR_LINE_DONE if left_status in ("done", "skipped") else COLOR_LINE_TODO
            x1, x2 = cx_list[i] + NODE_R, cx_list[i + 1] - NODE_R
            self.canvas.create_rectangle(x1, cy - LINE_H // 2, x2, cy + LINE_H // 2, fill=color, outline="")

        # Draw nodes and labels
        for i, stage in enumerate(stages):
            cx = cx_list[i]
            status = status_map.get(stage.id, "pending")
            is_active = stage.id == session.current_stage_id

            if status == "done":
                fill, outline, lw = COLOR_DONE, COLOR_DONE, 2
            elif status == "skipped":
                fill, outline, lw = COLOR_SKIPPED, COLOR_SKIPPED, 2
            elif is_active:
                fill, outline, lw = "#1a1a1a", COLOR_ACTIVE, 3
            else:
                fill, outline, lw = COLOR_TODO, COLOR_TODO, 2

            self.canvas.create_oval(
                cx - NODE_R, cy - NODE_R,
                cx + NODE_R, cy + NODE_R,
                fill=fill, outline=outline, width=lw,
            )

            # Checkmark inside done nodes
            if status == "done":
                self.canvas.create_text(cx, cy, text="✓", fill="white", font=("Helvetica", 9, "bold"))
            elif status == "skipped":
                self.canvas.create_text(cx, cy, text="—", fill="white", font=("Helvetica", 9, "bold"))

            label_color = COLOR_LABEL_DONE if status == "done" else (COLOR_LABEL_ACTIVE if is_active else COLOR_LABEL_TODO)
            self.canvas.create_text(
                cx, cy + NODE_R + LABEL_PAD,
                text=stage.label, fill=label_color,
                font=("Helvetica", 10, "bold" if is_active else "normal"),
                anchor="n",
            )
