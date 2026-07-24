# Download
import webbrowser

from PyQt5.QtWidgets import (
    QFrame, QLabel, QPushButton, QProgressBar,
    QVBoxLayout, QHBoxLayout
)

from PyQt5.QtCore import Qt, pyqtSignal, QSize

# Local
from ..styles.theme import (
    circular_pixmap, BG_SECONDARY, BG_TERTIARY, BORDER,
    ACCENT_GREEN, ACCENT_GREEN_HOVER, ACCENT_RED, ACCENT_RED_HOVER, ACCENT_BLUE
)
from ..styles.icons import apply_icon

TILE_WIDTH = 350
TILE_HEIGHT = 224


class ModTile(QFrame):
    start_requested = pyqtSignal(str)
    stop_requested = pyqtSignal(str)
    settings_requested = pyqtSignal(str)
    install_requested = pyqtSignal(str)
    update_requested = pyqtSignal(str)
    delete_requested = pyqtSignal(str)

    def __init__(self, name, bot_data, installed, parent=None):
        super().__init__(parent)
        self.name = name
        self.bot_data = bot_data
        self.installed = installed
        self.running = False

        self.settings_btn = None
        self.update_btn = None
        self.delete_btn = None

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
        version_info = data.get('APP_VERSION', {})
        version = version_info.get('VER', '')
        date = version_info.get('DAT', '')
        dev = version_info.get('DEV', '')
        description = data.get('DESCRIPTION') or 'Описание отсутствует.'
        github_link = data.get('APP_GITHUB_LINK', '')
        icon_path = self.bot_data.get('APP', {}).get('ICON') or ''

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 12)

        top_row = QHBoxLayout()
        name_label = QLabel(app_name)
        name_label.setStyleSheet('font-size: 16px; font-weight: 600;')
        name_label.setWordWrap(True)
        top_row.addWidget(name_label, stretch=1)

        self.primary_btn = QPushButton()
        self.primary_btn.setFixedSize(32, 32)
        self.primary_btn.setCursor(Qt.PointingHandCursor)
        self.primary_btn.clicked.connect(self._on_primary_clicked)
        top_row.addWidget(self.primary_btn, alignment=Qt.AlignTop)
        root.addLayout(top_row)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedHeight(14)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {BG_TERTIARY};
                border: 1px solid {BORDER};
                border-radius: 4px;
                text-align: center;
                font-size: 10px;
                color: white;
            }}
            QProgressBar::chunk {{
                background-color: {ACCENT_BLUE};
                border-radius: 4px;
            }}
        """)
        root.addWidget(self.progress_bar)

        meta_bits = [b for b in (f'v{version}' if version else '', date) if b]
        meta_text = ' · '.join(meta_bits) if meta_bits else ('Доступна для установки' if not self.installed else '')
        self.meta_label = QLabel(meta_text)
        self.meta_label.setStyleSheet('color: #8b949e; font-size: 12px;')
        root.addWidget(self.meta_label)

        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet('color: #c9d1d9; font-size: 12px;')
        desc_label.setMaximumHeight(52)
        root.addWidget(desc_label)

        root.addStretch(1)

        bottom_row = QHBoxLayout()
        icon_label = QLabel()
        icon_label.setPixmap(circular_pixmap(icon_path, 36))
        icon_label.setFixedSize(36, 36)
        bottom_row.addWidget(icon_label)

        dev_label = QLabel(dev)
        dev_label.setStyleSheet('color: #8b949e; font-size: 12px;')
        bottom_row.addWidget(dev_label)

        bottom_row.addStretch(1)

        if github_link:
            github_btn = QPushButton()
            apply_icon(github_btn, 'globe')
            github_btn.setFixedSize(32, 32)
            github_btn.setCursor(Qt.PointingHandCursor)
            github_btn.setToolTip('Открыть репозиторий на GitHub')
            github_btn.clicked.connect(lambda: webbrowser.open(github_link))
            bottom_row.addWidget(github_btn)

        if self.installed:
            self.update_btn = QPushButton()
            apply_icon(self.update_btn, 'refresh')
            self.update_btn.setFixedSize(32, 32)
            self.update_btn.setCursor(Qt.PointingHandCursor)
            self.update_btn.setToolTip('Обновить модификацию')
            self.update_btn.clicked.connect(lambda: self.update_requested.emit(self.name))
            bottom_row.addWidget(self.update_btn)

            self.delete_btn = QPushButton()
            apply_icon(self.delete_btn, 'trash')
            self.delete_btn.setFixedSize(32, 32)
            self.delete_btn.setCursor(Qt.PointingHandCursor)
            self.delete_btn.setToolTip('Удалить модификацию')
            self.delete_btn.clicked.connect(lambda: self.delete_requested.emit(self.name))
            bottom_row.addWidget(self.delete_btn)

            self.settings_btn = QPushButton()
            apply_icon(self.settings_btn, 'settings')
            self.settings_btn.setFixedSize(32, 32)
            self.settings_btn.setCursor(Qt.PointingHandCursor)
            self.settings_btn.setToolTip('Настройки модификации')
            self.settings_btn.clicked.connect(lambda: self.settings_requested.emit(self.name))
            bottom_row.addWidget(self.settings_btn)

        root.addLayout(bottom_row)
        self._apply_primary_btn_style()

    def _apply_primary_btn_style(self):
        if not self.installed:
            bg, hover, kind, tooltip = ACCENT_BLUE, ACCENT_BLUE, 'download', 'Скачать модификацию'
        elif self.running:
            bg, hover, kind, tooltip = ACCENT_RED, ACCENT_RED_HOVER, 'stop', 'Остановить'
        else:
            bg, hover, kind, tooltip = ACCENT_GREEN, ACCENT_GREEN_HOVER, 'play', 'Запустить'

        apply_icon(self.primary_btn, kind, size=16, color='#ffffff')
        self.primary_btn.setToolTip(tooltip)
        self.primary_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                border: none;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
        """)

    def _on_primary_clicked(self):
        if not self.installed:
            self.install_requested.emit(self.name)
        elif self.running:
            self.stop_requested.emit(self.name)
        else:
            self.start_requested.emit(self.name)

    def set_running(self, running):
        self.running = running
        self._apply_primary_btn_style()
        if self.settings_btn is not None:
            self.settings_btn.setDisabled(running)
        if self.update_btn is not None:
            self.update_btn.setDisabled(running)
        if self.delete_btn is not None:
            self.delete_btn.setDisabled(running)

    def start_progress(self):
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat('Загрузка... %p%')
        self.progress_bar.setVisible(True)
        self.meta_label.setVisible(False)
        self.primary_btn.setDisabled(True)
        if self.update_btn is not None:
            self.update_btn.setDisabled(True)
        if self.delete_btn is not None:
            self.delete_btn.setDisabled(True)

    def set_progress(self, percent):
        if percent < 0:
            self.progress_bar.setRange(0, 0)
            self.progress_bar.setFormat('Загрузка...')
        else:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(percent)
            self.progress_bar.setFormat('Загрузка... %p%')

    def finish_progress(self):
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setVisible(False)
        self.meta_label.setVisible(True)
        self.primary_btn.setDisabled(False)
        if self.update_btn is not None:
            self.update_btn.setDisabled(False)
        if self.delete_btn is not None:
            self.delete_btn.setDisabled(False)
