from __future__ import annotations
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal
from config.loader import load_pipeline
from core.session import Session
from app.components.progress_bar import ProgressBar
from app.components.action_list import ActionList


class MainWindow(QMainWindow):
    window_closed = Signal()

    def __init__(self, session: Session) -> None:
        super().__init__()
        self.session = session
        self.pipeline = load_pipeline()
        self.go_home = False

        self.setWindowTitle(f"rec — {session.title}")
        self.setMinimumSize(700, 480)
        self.resize(820, 560)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(24, 16, 24, 20)
        layout.setSpacing(16)

        # Header row: home button + session title
        header = QHBoxLayout()
        home_btn = QPushButton("←")
        home_btn.setObjectName("secondary")
        home_btn.setFixedWidth(100)
        home_btn.clicked.connect(self._on_home)

        session_title = QLabel(session.title)
        session_title.setStyleSheet("color: #666666; font-size: 13px;")
        session_title.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        header.addWidget(home_btn)
        header.addStretch()
        header.addWidget(session_title)
        layout.addLayout(header)

        self.progress_bar = ProgressBar()
        layout.addWidget(self.progress_bar)

        self.action_list = ActionList(session, self.pipeline, on_change=self.refresh)
        layout.addWidget(self.action_list)

        self.refresh()

    def _on_home(self) -> None:
        self.go_home = True
        self.close()

    def closeEvent(self, event) -> None:
        self.window_closed.emit()
        super().closeEvent(event)

    def refresh(self) -> None:
        self.progress_bar.update_state(self.session, self.pipeline)
        self.action_list.update_state(self.session)
