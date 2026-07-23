from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QScrollArea,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QInputDialog, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import os

from ...backend.plugins import GetFiles
from ..widgets.flow_layout import FlowLayout
from ..widgets.mod_tile import ModTile
from ..widgets.add_tile import AddModTile
from .console_window import ConsoleWindow
from .settings_window import ModSettingsWindow
from .app_window import AppSettingsWindow
from ..core.process_manager import ProcessManager
from ..core.github_importer import import_from_github, GithubImportError
from ..core.local_importer import import_local, LocalImportError
from ...backend.constants import resource_path


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('AMAZING MULTI TOOL')
        self.resize(1100, 700)
        self.setMinimumSize(800, 600)

        icon_path = resource_path('icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.process_manager = ProcessManager(self)
        self.process_manager.message.connect(self._on_process_message)
        self.process_manager.stopped.connect(self._on_process_stopped)

        self.bots = {}
        self.tiles = {}
        self.consoles = {}
        self.settings_windows = {}

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        top_bar = QWidget()
        top_bar.setFixedHeight(44)
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(12, 6, 12, 6)

        title_label = QLabel('AMAZING MULTI TOOL')
        title_label.setStyleSheet('font-size: 15px; font-weight: 600;')
        top_bar_layout.addWidget(title_label)
        top_bar_layout.addStretch(1)

        app_settings_btn = QPushButton('⚙️')
        app_settings_btn.setFixedSize(32, 32)
        app_settings_btn.setCursor(Qt.PointingHandCursor)
        app_settings_btn.clicked.connect(self._open_app_settings)
        top_bar_layout.addWidget(app_settings_btn)

        root.addWidget(top_bar)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.tiles_container = QWidget()
        self.flow_layout = FlowLayout(self.tiles_container, margin=20, spacing=24)
        self.tiles_container.setLayout(self.flow_layout)

        self.scroll_area.setWidget(self.tiles_container)
        root.addWidget(self.scroll_area, stretch=1)

    def refresh(self):
        self.bots = GetFiles.get_bot() or {}

        while self.flow_layout.count():
            item = self.flow_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.tiles = {}

        for name, bot_data in self.bots.items():
            tile = ModTile(name, bot_data)
            tile.start_requested.connect(self._on_start_requested)
            tile.stop_requested.connect(self._on_stop_requested)
            tile.settings_requested.connect(self._on_settings_requested)
            tile.set_running(self.process_manager.is_running(name))
            self.flow_layout.addWidget(tile)
            self.tiles[name] = tile

        add_tile = AddModTile()
        add_tile.import_github_requested.connect(self._on_import_github)
        add_tile.add_local_requested.connect(self._on_add_local)
        self.flow_layout.addWidget(add_tile)

        self.tiles_container.updateGeometry()

    def _open_app_settings(self):
        dialog = AppSettingsWindow(self)
        dialog.exec_()

    def _on_console_closed(self, name):
        if self.process_manager.is_running(name):
            self.process_manager.stop(name)
        self.consoles.pop(name, None)
        tile = self.tiles.get(name)
        if tile is not None:
            tile.set_running(False)

    def _on_start_requested(self, name):
        settings_win = self.settings_windows.pop(name, None)
        if settings_win is not None:
            settings_win.close()

        bot_data = self.bots[name]
        app_name = ' '.join(bot_data['DATA']['APP_NAME'])
        icon_path = bot_data['APP']['ICON']

        console = self.consoles.get(name)
        if console is None:
            console = ConsoleWindow(name, app_name, icon_path, self)
            console.closed.connect(self._on_console_closed)
            self.consoles[name] = console

        if console.body is not None:
            console.body.clear()

        console.show()
        console.raise_()

        self.process_manager.start(name, bot_data['APP']['MAIN'])
        self.tiles[name].set_running(True)

    def _on_stop_requested(self, name):
        self.process_manager.stop(name)
        self.tiles[name].set_running(False)

        console = self.consoles.get(name)
        if console is not None:
            console.close()
            self.consoles.pop(name, None)

    def _on_process_message(self, name, text, color):
        console = self.consoles.get(name)
        if console is not None and console.body is not None:
            console.append_message(text, color)

    def _on_process_stopped(self, name):
        tile = self.tiles.get(name)
        if tile is not None:
            tile.set_running(False)

    def _on_settings_requested(self, name):
        if self.process_manager.is_running(name):
            return

        existing = self.settings_windows.get(name)
        if existing is not None:
            existing.raise_()
            return

        bot_data = self.bots[name]
        app_name = ' '.join(bot_data['DATA']['APP_NAME'])
        dialog = ModSettingsWindow(
            name,
            bot_data['DATA']['APP'],
            app_name,
            bot_data['APP']['ICON'],
            self
        )
        self.settings_windows[name] = dialog
        dialog.finished.connect(lambda *_: self.settings_windows.pop(name, None))
        dialog.exec_()

    def _on_add_local(self):
        manifest_path, _ = QFileDialog.getOpenFileName(
            self, 'Выберите manifest.json', '', 'manifest.json (manifest.json)'
        )
        if not manifest_path:
            return
        try:
            import_local(manifest_path)
        except LocalImportError as e:
            QMessageBox.critical(self, 'Ошибка добавления', str(e))
            return
        self.refresh()

    def _on_import_github(self):
        url, ok = QInputDialog.getText(
            self, 'Импорт из GitHub', 'Ссылка на репозиторий (https://github.com/owner/repo):'
        )
        if not ok or not url.strip():
            return
        try:
            import_from_github(url.strip())
        except GithubImportError as e:
            QMessageBox.critical(self, 'Ошибка импорта', str(e))
            return
        self.refresh()

    def closeEvent(self, event):
        for name in list(self.tiles.keys()):
            if self.process_manager.is_running(name):
                self.process_manager.stop(name)

        for console in self.consoles.values():
            if console is not None:
                console.close()

        super().closeEvent(event)
