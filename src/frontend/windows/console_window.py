# Free
from datetime import datetime

# Download
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QPlainTextEdit, QSizeGrip
)

from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal

# Local
from ..styles.theme import CONSOLE_QSS, circular_pixmap
from ..styles.icons import apply_icon

COLOR_MAP = {
    'red': '#f85149',
    'green': '#3fb950',
    'yellow': '#d29922',
    'blue': '#58a6ff',
    'white': '#c9d1d9',
    'gray': '#8b949e',
    'grey': '#8b949e',
    'orange': '#db6d28',
    'purple': '#bc8cff',
}
DEFAULT_COLOR = COLOR_MAP['green']


class ConsoleWindow(QDialog):
    closed = pyqtSignal(str)

    def __init__(self, name, app_name, icon_path, parent=None):
        super().__init__(parent)
        self.name = name
        self._drag_pos = None

        if icon_path and QPixmap(icon_path).isNull() is False:
            self.setWindowIcon(QIcon(icon_path))

        self.setWindowFlags(
            Qt.Dialog |
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.WindowSystemMenuHint
        )
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.resize(400, 300)
        self.setMinimumSize(400, 300)

        self.setStyleSheet(CONSOLE_QSS)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = QLabel()
        header.setObjectName('ConsoleHeader')
        header.setFixedHeight(36)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 4, 10, 4)

        icon_label = QLabel()
        pix = circular_pixmap(icon_path, 22)
        if pix.isNull():
            pix = QPixmap(22, 22)
            pix.fill(Qt.transparent)
        icon_label.setPixmap(pix)
        header_layout.addWidget(icon_label)

        title_label = QLabel(f'Консоль — {app_name}')
        title_label.setObjectName('ConsoleHeaderLabel')
        header_layout.addWidget(title_label)
        header_layout.addStretch(1)

        close_btn = QPushButton()
        apply_icon(close_btn, 'close', size=14, color='#ffffff')
        close_btn.setFixedSize(28, 28)
        close_btn.setObjectName('ConsoleCloseBtn')
        close_btn.setStyleSheet("""
            QPushButton#ConsoleCloseBtn {
                background-color: transparent;
                border: none;
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton#ConsoleCloseBtn:hover {
                background-color: #e81123;
                color: #ffffff;
            }
        """)

        close_btn.clicked.connect(self.close)
        header_layout.addWidget(close_btn)

        header.mousePressEvent = self._header_mouse_press
        header.mouseMoveEvent = self._header_mouse_move

        root.addWidget(header)

        self.body = QPlainTextEdit()
        self.body.setObjectName('ConsoleBody')
        self.body.setReadOnly(True)
        root.addWidget(self.body, stretch=1)

        grip = QSizeGrip(self)
        grip.setStyleSheet("""
            QSizeGrip {
                background-color: transparent;
                width: 12px;
                height: 12px;
            }
        """)

        root.addWidget(grip, alignment=Qt.AlignBottom | Qt.AlignRight)

    def _header_mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()

    def _header_mouse_move(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos is not None:
            self.move(event.globalPos() - self._drag_pos)

    def append_message(self, text, color=None):
        if not self.body:
            return
        timestamp = datetime.now().strftime('%H:%M:%S')
        hex_color = COLOR_MAP.get((color or '').lower(), DEFAULT_COLOR if color is None else color)
        safe_text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        self.body.appendHtml(
            f'<span style="color:{hex_color};">[{timestamp}] {safe_text}</span>'
        )

    def closeEvent(self, event):
        self.closed.emit(self.name)
        super().closeEvent(event)
