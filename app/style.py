DARK_STYLE = """
QWidget {
    background-color: #1a1a1a;
    color: #e0e0e0;
    font-family: -apple-system, Helvetica Neue, Arial;
    font-size: 13px;
}

QDialog {
    background-color: #1a1a1a;
}

QFrame#card {
    background-color: #242424;
    border-radius: 8px;
}

QLabel#title {
    font-size: 26px;
    font-weight: bold;
    color: #ffffff;
}

QLabel#subtitle {
    font-size: 13px;
    color: #666666;
}

QLabel#section {
    font-size: 12px;
    font-weight: bold;
    color: #666666;
}

QLabel#stage_label {
    font-size: 15px;
    font-weight: bold;
    color: #ffffff;
}

QLineEdit {
    background-color: #2c2c2c;
    border: 1px solid #3a3a3a;
    border-radius: 6px;
    padding: 6px 10px;
    color: #e0e0e0;
    font-size: 13px;
}

QLineEdit:focus {
    border: 1px solid #2196F3;
}

QPushButton {
    background-color: #2196F3;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 13px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #1976D2;
}

QPushButton:disabled {
    background-color: #2a2a2a;
    color: #555555;
}

QPushButton#secondary {
    background-color: #2c2c2c;
    color: #aaaaaa;
}

QPushButton#secondary:hover {
    background-color: #383838;
    color: #ffffff;
}

QPushButton#run_btn {
    background-color: #2c2c2c;
    color: #aaaaaa;
    font-size: 12px;
    font-weight: normal;
    padding: 4px 10px;
}

QPushButton#run_btn:hover {
    background-color: #383838;
    color: #ffffff;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    background: #1a1a1a;
    width: 6px;
    border-radius: 3px;
}

QScrollBar::handle:vertical {
    background: #3a3a3a;
    border-radius: 3px;
    min-height: 20px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""
