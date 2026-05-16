from __future__ import annotations
import sys
from PySide6.QtWidgets import QApplication
from app.style import DARK_STYLE


def start() -> None:
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLE)

    from app.components.session_picker import SessionPickerDialog
    picker = SessionPickerDialog()
    picker.exec()

    if picker.selected_session:
        from app.windows.main_window import MainWindow
        window = MainWindow(picker.selected_session)
        window.show()
        sys.exit(app.exec())
