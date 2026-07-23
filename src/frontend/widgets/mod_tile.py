# Download
from PyQt5.QtWidgets import (
    QFrame, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout
)

from PyQt5.QtCore import Qt, pyqtSignal, QSize

# Local
from ..styles.theme import circular_pixmap, BG_SECONDARY, BORDER, ACCENT_GREEN, ACCENT_GREEN_HOVER, ACCENT_RED, ACCENT_RED_HOVER

TILE_WIDTH = 350
TILE_HEIGHT = 200


class ModTile(QFrame):
    start_requested = pyqtSignal(str)
    stop_requested = pyqtSignal(str)
    settings_requested = pyqtSignal(str)

    def __init__(self, name, bot_data, parent=None):
        super().__init__(parent)
        self.name = name
        self.bot_data = bot_data
        self.running = False

        self.setFixedSize(TILE_WIDTH, TILE_HEIGHT)
        self.setObjectName('ModTile')
        self.setStyleSheet(f"""
            #ModTile {{
                background-color: {BG_SECONDARY};
                border: 1px solid {BORDER};
                border-radius: 10px;
            }}
        """)

        self._build_ui()

    def sizeHint(self):
        return QSize(TILE_WIDTH, TILE_HEIGHT)

    def _build_ui(self):
        data = self.bot_data['DATA']
        app_name = ' '.join(data['APP_NAME'])
        version = data['APP_VERSION']['VER']
        date = data['APP_VERSION']['DAT']
        dev = data['APP_VERSION']['DEV']

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 12)

        top_row = QHBoxLayout()
        name_label = QLabel(app_name)
        name_label.setStyleSheet('font-size: 16px; font-weight: 600;')
        name_label.setWordWrap(True)
        top_row.addWidget(name_label, stretch=1)

        self.start_btn = QPushButton('▶')
        self.start_btn.setFixedSize(32, 32)
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.clicked.connect(self._on_start_stop_clicked)
        top_row.addWidget(self.start_btn, alignment=Qt.AlignTop)
        root.addLayout(top_row)

        version_label = QLabel(f'v{version} · {date}')
        version_label.setStyleSheet('color: #8b949e; font-size: 12px;')
        root.addWidget(version_label)

        root.addStretch(1)

        bottom_row = QHBoxLayout()
        icon_label = QLabel()
        icon_label.setPixmap(circular_pixmap(self.bot_data['APP']['ICON'], 36))
        icon_label.setFixedSize(36, 36)
        bottom_row.addWidget(icon_label)

        dev_label = QLabel(dev)
        dev_label.setStyleSheet('color: #8b949e; font-size: 12px;')
        bottom_row.addWidget(dev_label)

        bottom_row.addStretch(1)

        self.settings_btn = QPushButton('⚙️')
        self.settings_btn.setFixedSize(32, 32)
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        self.settings_btn.clicked.connect(lambda: self.settings_requested.emit(self.name))
        bottom_row.addWidget(self.settings_btn, alignment=Qt.AlignBottom)

        root.addLayout(bottom_row)
        self._apply_start_btn_style()

    def _apply_start_btn_style(self):
        if self.running:
            bg, hover = ACCENT_RED, ACCENT_RED_HOVER
            symbol = '■'
        else:
            bg, hover = ACCENT_GREEN, ACCENT_GREEN_HOVER
            symbol = '▶'

        self.start_btn.setText(symbol)
        self.start_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                border: none;
                border-radius: 6px;
                color: white;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
        """)

    def _on_start_stop_clicked(self):
        if self.running:
            self.stop_requested.emit(self.name)
        else:
            self.start_requested.emit(self.name)

    def set_running(self, running):
        self.running = running
        self._apply_start_btn_style()
        self.settings_btn.setDisabled(running)
