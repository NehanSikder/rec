from __future__ import annotations
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QFont, QPen
from PySide6.QtCore import Qt
from config.models import PipelineConfig
from core.session import Session

COLOR_DONE    = QColor("#4CAF50")
COLOR_ACTIVE  = QColor("#2196F3")
COLOR_SKIPPED = QColor("#9E9E9E")
COLOR_TODO    = QColor("#3a3a3a")
COLOR_BG      = QColor("#1a1a1a")

NODE_R   = 10
LINE_H   = 3
LABEL_Y_OFFSET = 18


class ProgressBar(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedHeight(56)
        self._session: Session | None = None
        self._pipeline: PipelineConfig | None = None

    def update_state(self, session: Session, pipeline: PipelineConfig) -> None:
        self._session = session
        self._pipeline = pipeline
        self.update()

    def paintEvent(self, _event) -> None:
        if not self._session or not self._pipeline:
            return

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        stages = self._pipeline.stages
        n = len(stages)
        if n == 0:
            return

        w, h = self.width(), self.height()
        margin = 40
        spacing = (w - 2 * margin) / (n - 1) if n > 1 else 0
        cx_list = [int(margin + i * spacing) for i in range(n)]
        cy = (h - LABEL_Y_OFFSET - 8) // 2

        status_map = {s.stage_id: s.status for s in self._session.stages}

        # Lines
        for i in range(n - 1):
            left_status = status_map.get(stages[i].id, "pending")
            color = COLOR_DONE if left_status in ("done", "skipped") else COLOR_TODO
            p.setPen(Qt.NoPen)
            p.setBrush(color)
            x1, x2 = cx_list[i] + NODE_R, cx_list[i + 1] - NODE_R
            p.drawRect(x1, cy - LINE_H // 2, x2 - x1, LINE_H)

        # Nodes + labels
        font_normal = QFont("-apple-system", 10)
        font_bold   = QFont("-apple-system", 10, QFont.Bold)

        for i, stage in enumerate(stages):
            cx = cx_list[i]
            status = status_map.get(stage.id, "pending")
            is_active = stage.id == self._session.current_stage_id

            if status == "done":
                fill, border = COLOR_DONE, COLOR_DONE
            elif status == "skipped":
                fill, border = COLOR_SKIPPED, COLOR_SKIPPED
            elif is_active:
                fill, border = COLOR_BG, COLOR_ACTIVE
            else:
                fill, border = COLOR_TODO, COLOR_TODO

            pen = QPen(border, 2 if not is_active else 3)
            p.setPen(pen)
            p.setBrush(fill)
            p.drawEllipse(cx - NODE_R, cy - NODE_R, NODE_R * 2, NODE_R * 2)

            # Icon inside node
            if status in ("done", "skipped"):
                p.setPen(QColor("white"))
                p.setFont(QFont("-apple-system", 8, QFont.Bold))
                symbol = "✓" if status == "done" else "—"
                p.drawText(cx - NODE_R, cy - NODE_R, NODE_R * 2, NODE_R * 2, Qt.AlignCenter, symbol)

            # Label below node
            label_color = COLOR_DONE if status == "done" else (QColor("white") if is_active else QColor("#666666"))
            p.setPen(label_color)
            p.setFont(font_bold if is_active else font_normal)
            p.drawText(cx - 50, cy + NODE_R + 4, 100, 20, Qt.AlignCenter, stage.label)

        p.end()
