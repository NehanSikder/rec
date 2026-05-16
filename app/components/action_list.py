from __future__ import annotations
from typing import Callable
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QSizePolicy,
)
from PySide6.QtCore import Qt
from config.models import PipelineConfig
from core.session import Session
from core.state_machine import advance_stage, skip_stage, stage_is_complete, pipeline_is_complete
from core.action_runner import run_action
from core.undo_stack import (
    record_action_done, record_stage_advanced,
    record_stage_skipped, can_undo, undo,
)

STATUS_ICON = {
    "pending": ("○", "#666666"),
    "running": ("◌", "#2196F3"),
    "done":    ("✓", "#4CAF50"),
    "failed":  ("✗", "#F44336"),
    "skipped": ("—", "#9E9E9E"),
}


class ActionList(QWidget):
    def __init__(self, session: Session, pipeline: PipelineConfig, on_change: Callable, parent=None) -> None:
        super().__init__(parent)
        self.session = session
        self.pipeline = pipeline
        self.on_change = on_change
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.stage_label = QLabel()
        self.stage_label.setObjectName("stage_label")
        layout.addWidget(self.stage_label)

        # Scroll area for actions
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)

        self.action_container = QWidget()
        self.action_container.setStyleSheet("background-color: #222222; border-radius: 8px;")
        self.action_layout = QVBoxLayout(self.action_container)
        self.action_layout.setContentsMargins(12, 12, 12, 12)
        self.action_layout.setSpacing(4)
        self.action_layout.addStretch()

        self.scroll.setWidget(self.action_container)
        layout.addWidget(self.scroll)

        # Button row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self.btn_undo = QPushButton("Undo")
        self.btn_undo.setObjectName("secondary")
        self.btn_undo.setFixedWidth(80)
        self.btn_undo.clicked.connect(self._on_undo)

        self.btn_skip = QPushButton("Skip Stage")
        self.btn_skip.setObjectName("secondary")
        self.btn_skip.setFixedWidth(100)
        self.btn_skip.clicked.connect(self._on_skip)

        self.btn_complete = QPushButton("Complete Stage →")
        self.btn_complete.setFixedWidth(160)
        self.btn_complete.clicked.connect(self._on_complete)

        btn_row.addWidget(self.btn_undo)
        btn_row.addWidget(self.btn_skip)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_complete)
        layout.addLayout(btn_row)

    def update_state(self, session: Session) -> None:
        self.session = session
        self._rebuild_rows()
        self._refresh_buttons()

    def _rebuild_rows(self) -> None:
        # Clear existing rows (keep the trailing stretch)
        while self.action_layout.count() > 1:
            item = self.action_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        stage_state = self.session.get_stage(self.session.current_stage_id)
        stage_config = next((s for s in self.pipeline.stages if s.id == self.session.current_stage_id), None)
        if not stage_state or not stage_config:
            return

        self.stage_label.setText(stage_config.label)

        for action_config in stage_config.actions:
            action_state = self.session.get_action(stage_state.stage_id, action_config.id)
            if not action_state:
                continue

            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(4, 6, 4, 6)
            row_layout.setSpacing(10)

            icon, color = STATUS_ICON.get(action_state.status, ("○", "#666666"))
            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet(f"color: {color}; font-size: 15px; background: transparent;")
            icon_lbl.setFixedWidth(20)
            icon_lbl.setAlignment(Qt.AlignCenter)

            name_lbl = QLabel(action_config.label)
            name_lbl.setStyleSheet("color: #e0e0e0; background: transparent;")
            name_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

            row_layout.addWidget(icon_lbl)
            row_layout.addWidget(name_lbl)

            if action_state.status in ("pending", "failed"):
                btn = QPushButton("Run")
                btn.setObjectName("run_btn")
                btn.setFixedSize(60, 28)
                btn.clicked.connect(
                    lambda checked=False, ac=action_config, st=action_state: self._on_run(ac, st)
                )
                row_layout.addWidget(btn)

            self.action_layout.insertWidget(self.action_layout.count() - 1, row)

    def _refresh_buttons(self) -> None:
        self.btn_undo.setEnabled(can_undo(self.session))
        complete = stage_is_complete(self.session)
        finished = pipeline_is_complete(self.session)
        self.btn_complete.setEnabled(complete and not finished)
        self.btn_complete.setText("Pipeline Complete" if finished else "Complete Stage →")

    def _on_run(self, action_config, action_state) -> None:
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
