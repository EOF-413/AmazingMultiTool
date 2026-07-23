# Download
from PyQt5.QtGui import QPainter, QPainterPath, QPixmap
from PyQt5.QtCore import Qt

BG_PRIMARY = '#0d1117'
BG_SECONDARY = '#161b22'
BG_TERTIARY = '#21262d'
BORDER = '#30363d'
TEXT_PRIMARY = '#c9d1d9'
TEXT_SECONDARY = '#8b949e'
ACCENT_GREEN = '#238636'
ACCENT_GREEN_HOVER = '#2ea043'
ACCENT_RED = '#da3633'
ACCENT_RED_HOVER = '#f85149'
ACCENT_BLUE = '#58a6ff'
CONSOLE_GREEN = '#3fb950'

GITHUB_DARK_QSS = f"""
QWidget {{
    background-color: {BG_PRIMARY};
    color: {TEXT_PRIMARY};
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
}}

QMainWindow {{
    background-color: {BG_PRIMARY};
}}

QScrollArea {{
    border: none;
    background-color: transparent;
}}

QScrollArea > QWidget > QWidget {{
    background-color: transparent;
}}

QToolTip {{
    background-color: {BG_TERTIARY};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    padding: 4px;
}}

QPushButton {{
    background-color: {BG_TERTIARY};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 6px 12px;
    color: {TEXT_PRIMARY};
}}

QPushButton:hover {{
    background-color: {BORDER};
}}

QPushButton:disabled {{
    color: {TEXT_SECONDARY};
    background-color: {BG_SECONDARY};
}}

QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
    background-color: {BG_SECONDARY};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 4px 8px;
    color: {TEXT_PRIMARY};
}}

QLabel {{
    background-color: transparent;
}}

QDialog {{
    background-color: {BG_PRIMARY};
}}

QMenu {{
    background-color: {BG_SECONDARY};
    border: 1px solid {BORDER};
    padding: 4px;
}}

QMenu::item {{
    padding: 6px 16px;
    border-radius: 4px;
}}

QMenu::item:selected {{
    background-color: {BG_TERTIARY};
}}

QScrollBar:vertical {{
    background: {BG_PRIMARY};
    width: 10px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 5px;
    min-height: 24px;
}}

QScrollBar::handle:vertical:hover {{
    background: {ACCENT_BLUE};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
"""

CONSOLE_QSS = f"""
#ConsoleHeader {{
    background-color: #000000;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}}

#ConsoleHeader QLabel {{
    background-color: transparent;
    color: {CONSOLE_GREEN};
}}

#ConsoleHeaderLabel {{
    color: {CONSOLE_GREEN};
    font-weight: 600;
}}

#ConsoleBody {{
    background-color: #000000;
    color: {CONSOLE_GREEN};
    border: none;
    border-bottom-left-radius: 8px;
    border-bottom-right-radius: 8px;
    font-family: 'Consolas', 'Cascadia Mono', monospace;
    font-size: 12px;
    padding: 6px;
}}

QScrollBar:vertical {{
    background: #000000;
    width: 10px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: {CONSOLE_GREEN};
    border-radius: 5px;
    min-height: 24px;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
"""


def circular_pixmap(source_path, size=40):
    src = QPixmap(source_path)
    if src.isNull():
        src = QPixmap(size, size)
        src.fill(Qt.transparent)

    src = src.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

    target = QPixmap(size, size)
    target.fill(Qt.transparent)

    painter = QPainter(target)
    painter.setRenderHint(QPainter.Antialiasing)
    path = QPainterPath()
    path.addEllipse(0, 0, size, size)
    painter.setClipPath(path)

    x = (src.width() - size) // 2
    y = (src.height() - size) // 2
    painter.drawPixmap(-x, -y, src)
    painter.end()

    return target
