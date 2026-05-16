from __future__ import annotations
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from config.loader import load_pipeline
from core.session import Session
from app.components.progress_bar import ProgressBar
from app.components.action_list import ActionList


class MainWindow(QMainWindow):
    def __init__(self, session: Session) -> None:
        super().__init__()
        self.session = session
        self.pipeline = load_pipeline()

        self.setWindowTitle(f"rec — {session.title}")
        self.setMinimumSize(700, 480)
        self.resize(820, 560)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        self.progress_bar = ProgressBar()
        layout.addWidget(self.progress_bar)

        self.action_list = ActionList(session, self.pipeline, on_change=self.refresh)
        layout.addWidget(self.action_list)

        self.refresh()

    def refresh(self) -> None:
        self.progress_bar.update_state(self.session, self.pipeline)
        self.action_list.update_state(self.session)
