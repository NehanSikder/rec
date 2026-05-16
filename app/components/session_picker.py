from __future__ import annotations
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QScrollArea,
    QWidget, QSizePolicy,
)
from PySide6.QtCore import Qt
from config.loader import load_pipeline
from core.session import Session, create_session, load_session, list_sessions


class SessionPickerDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.selected_session: Session | None = None
        self.setWindowTitle("rec")
        self.setFixedSize(460, 520)
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(0)

        title = QLabel("rec")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Production Pipeline Manager")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        layout.addSpacing(28)

        # New session card
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 14, 16, 14)
        card_layout.setSpacing(8)

        card_layout.addWidget(QLabel("New Session"))

        input_row = QHBoxLayout()
        self.title_entry = QLineEdit()
        self.title_entry.setPlaceholderText("Episode title...")
        self.title_entry.returnPressed.connect(self._create)
        input_row.addWidget(self.title_entry)

        create_btn = QPushButton("Create")
        create_btn.setFixedWidth(80)
        create_btn.clicked.connect(self._create)
        input_row.addWidget(create_btn)
        card_layout.addLayout(input_row)

        layout.addWidget(card)
        layout.addSpacing(20)

        # Recent sessions
        sessions = list_sessions()
        if sessions:
            section = QLabel("Recent Sessions")
            section.setObjectName("section")
            layout.addWidget(section)
            layout.addSpacing(6)

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.NoFrame)

            container = QWidget()
            container.setStyleSheet("background-color: #222222; border-radius: 8px;")
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(12, 8, 12, 8)
            container_layout.setSpacing(2)

            for meta in sessions:
                row = QWidget()
                row.setStyleSheet("background: transparent;")
                row_layout = QHBoxLayout(row)
                row_layout.setContentsMargins(4, 6, 4, 6)

                name_lbl = QLabel(meta["title"])
                name_lbl.setStyleSheet("background: transparent;")
                name_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

                date_lbl = QLabel(meta["created_at"][:10])
                date_lbl.setStyleSheet("color: #555555; font-size: 11px; background: transparent;")

                open_btn = QPushButton("Open")
                open_btn.setObjectName("run_btn")
                open_btn.setFixedSize(60, 28)
                open_btn.clicked.connect(lambda checked=False, sid=meta["id"]: self._open(sid))

                row_layout.addWidget(name_lbl)
                row_layout.addWidget(date_lbl)
                row_layout.addSpacing(8)
                row_layout.addWidget(open_btn)
                container_layout.addWidget(row)

            container_layout.addStretch()
            scroll.setWidget(container)
            layout.addWidget(scroll)
        else:
            no_sessions = QLabel("No sessions yet.")
            no_sessions.setObjectName("subtitle")
            no_sessions.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_sessions)
            layout.addStretch()

    def _create(self) -> None:
        title = self.title_entry.text().strip()
        if not title:
            return
        pipeline = load_pipeline()
        stage_ids = [s.id for s in pipeline.stages]
        action_ids = {s.id: [a.id for a in s.actions] for s in pipeline.stages}
        self.selected_session = create_session(title, stage_ids, action_ids)
        self.accept()

    def _open(self, session_id: str) -> None:
        self.selected_session = load_session(session_id)
        self.accept()
