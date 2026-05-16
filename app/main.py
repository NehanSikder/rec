from __future__ import annotations
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QEventLoop
from app.style import DARK_STYLE


def start() -> None:
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLE)

    while True:
        from app.components.session_picker import SessionPickerDialog
        picker = SessionPickerDialog()
        picker.exec()

        if not picker.selected_session:
            break

        from app.windows.main_window import MainWindow
        window = MainWindow(picker.selected_session)
        window.show()

        # Block until this window closes, then check if user wants home
        loop = QEventLoop()
        window.window_closed.connect(loop.quit)
        loop.exec()

        if not window.go_home:
            break

    sys.exit(0)
