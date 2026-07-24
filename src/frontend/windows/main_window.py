from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QScrollArea,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QInputDialog, QMessageBox, QProgressBar, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import os
import shutil

from ...backend.plugins import GetFiles
from ...backend.debug import Log
from ..widgets.flow_layout import FlowLayout
from ..widgets.mod_tile import ModTile, TILE_WIDTH, TILE_HEIGHT
from ..widgets.add_tile import AddModTile
from .console_window import ConsoleWindow
from .settings_window import ModSettingsWindow
from .app_window import AppSettingsWindow
from ..core.process_manager import ProcessManager
from ..core.github_importer import import_from_github, GithubImportError
from ..core.local_importer import import_local, LocalImportError
from ..core.workers import FetchReposWorker, InstallWorker
from ..styles.icons import apply_icon
from ...backend.constants import resource_path
from ..styles.theme import BG_SECONDARY, BG_TERTIARY, BORDER, ACCENT_BLUE


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('AMAZING MULTI TOOL')
        self.resize(765, 565)
        self.setMinimumSize(765, 565)

        icon_path = resource_path('icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.process_manager = ProcessManager(self)
        self.process_manager.message.connect(self._on_process_message)
        self.process_manager.stopped.connect(self._on_process_stopped)

        self.bots = {}
        self.available_repos = {}
        self.tiles = {}
        self.consoles = {}
        self.settings_windows = {}

        self._fetch_worker = None
        self._install_workers = {}
        self.loading_tile = None

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

        refresh_catalog_btn = QPushButton()
        apply_icon(refresh_catalog_btn, 'refresh')
        refresh_catalog_btn.setFixedSize(32, 32)
        refresh_catalog_btn.setCursor(Qt.PointingHandCursor)
        refresh_catalog_btn.setToolTip('Обновить каталог модификаций')
        refresh_catalog_btn.clicked.connect(self._refresh_available_repos)
        top_bar_layout.addWidget(refresh_catalog_btn)

        app_settings_btn = QPushButton()
        apply_icon(app_settings_btn, 'settings')
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
        self._rebuild_tiles()
        self._refresh_available_repos()

    def _show_loading(self):
        if self.loading_tile is not None:
            return

        tile = QFrame()
        tile.setFixedSize(TILE_WIDTH, TILE_HEIGHT)
        tile.setObjectName('LoadingTile')
        tile.setStyleSheet(f"""
            #LoadingTile {{
                background-color: {BG_SECONDARY};
                border: 1px solid {BORDER};
                border-radius: 10px;
            }}
        """)

        layout = QVBoxLayout(tile)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)

        label = QLabel('Загрузка каталога модификаций...')
        label.setStyleSheet('color: #8b949e; font-size: 14px;')
        layout.addWidget(label, alignment=Qt.AlignCenter)

        progress = QProgressBar()
        progress.setRange(0, 0)
        progress.setFixedWidth(200)
        progress.setFixedHeight(16)
        progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: {BG_TERTIARY};
                border: 1px solid {BORDER};
                border-radius: 4px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {ACCENT_BLUE};
                border-radius: 4px;
            }}
        """)
        layout.addWidget(progress, alignment=Qt.AlignCenter)

        self.loading_tile = tile
        self.flow_layout.addWidget(tile)

    def _hide_loading(self):
        if self.loading_tile is None:
            return
        index = self.flow_layout.indexOf(self.loading_tile)
        if index != -1:
            item = self.flow_layout.takeAt(index)
            if item and item.widget():
                item.widget().deleteLater()
        self.loading_tile = None

    def _refresh_available_repos(self):
        if self._fetch_worker is not None and self._fetch_worker.isRunning():
            return
        self._show_loading()
        self._fetch_worker = FetchReposWorker(self)
        self._fetch_worker.finished_ok.connect(self._on_repos_fetched)
        self._fetch_worker.finished_error.connect(self._on_repos_fetch_error)
        self._fetch_worker.start()

    def _on_repos_fetched(self, repos):
        self._hide_loading()
        self.available_repos = repos
        self._rebuild_tiles()

    def _on_repos_fetch_error(self, message):
        self._hide_loading()
        Log.error(f"Не удалось загрузить каталог модификаций: {message}")

    def _rebuild_tiles(self):
        while self.flow_layout.count():
            item = self.flow_layout.takeAt(0)
            widget = item.widget()
            if widget and widget is not self.loading_tile:
                widget.deleteLater()
        self.tiles = {}

        for name, bot_data in self.bots.items():
            tile = ModTile(name, bot_data, installed=True)
            tile.start_requested.connect(self._on_start_requested)
            tile.stop_requested.connect(self._on_stop_requested)
            tile.settings_requested.connect(self._on_settings_requested)
            tile.update_requested.connect(self._on_update_requested)
            tile.delete_requested.connect(self._on_delete_requested)
            tile.set_running(self.process_manager.is_running(name))
            self.flow_layout.addWidget(tile)
            self.tiles[name] = tile

        for name, entry in self.available_repos.items():
            if name in self.bots:
                continue
            bot_data = {
                'DATA': {
                    'APP_NAME': entry.get('APP_NAME', [name]),
                    'APP_VERSION': {
                        'VER': entry.get('VERSION', ''),
                        'DAT': '',
                        'DEV': entry.get('DEV', ''),
                    },
                    'DESCRIPTION': entry.get('DESCRIPTION', ''),
                    'APP_GITHUB_LINK': entry.get('APP_GITHUB_LINK', ''),
                },
                'APP': {'ICON': entry.get('ICON')},
            }
            tile = ModTile(name, bot_data, installed=False)
            tile.install_requested.connect(self._on_install_requested)
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

    def _on_install_requested(self, name):
        entry = self.available_repos.get(name)
        if entry is None or not entry.get('APP_GITHUB_LINK'):
            QMessageBox.critical(self, 'Ошибка установки', 'Не найдена ссылка GitHub для этой модификации.')
            return
        self._run_install_worker(name, entry['APP_GITHUB_LINK'], allow_update=False)

    def _on_update_requested(self, name):
        bot_data = self.bots.get(name)
        link = bot_data['DATA'].get('APP_GITHUB_LINK') if bot_data else None
        if not link and name in self.available_repos:
            link = self.available_repos[name].get('APP_GITHUB_LINK')
        if not link:
            QMessageBox.warning(self, 'Обновление', 'Не удалось определить ссылку GitHub для обновления.')
            return
        self._run_install_worker(name, link, allow_update=True)

    def _run_install_worker(self, name, link, allow_update):
        if name in self._install_workers:
            return

        tile = self.tiles.get(name)
        if tile is not None:
            tile.start_progress()

        worker = InstallWorker(name, link, allow_update=allow_update, parent=self)
        worker.progress.connect(self._on_install_progress)
        worker.finished_ok.connect(self._on_install_finished)
        worker.finished_error.connect(self._on_install_failed)
        self._install_workers[name] = worker
        worker.start()

    def _on_install_progress(self, name, percent):
        tile = self.tiles.get(name)
        if tile is not None:
            tile.set_progress(percent)

    def _on_install_finished(self, name, mode):
        self._install_workers.pop(name, None)
        verb = 'обновлена' if mode == 'update' else 'установлена'
        Log.info(f"Модификация [{name}] успешно {verb} из каталога.")
        self.refresh()

    def _on_install_failed(self, name, message):
        self._install_workers.pop(name, None)
        tile = self.tiles.get(name)
        if tile is not None:
            tile.finish_progress()
        QMessageBox.critical(self, 'Ошибка', message)

    def _on_delete_requested(self, name):
        if self.process_manager.is_running(name):
            QMessageBox.warning(self, 'Удаление', 'Остановите модификацию перед удалением.')
            return

        confirm = QMessageBox.question(
            self, 'Удаление модификации',
            f'Удалить модификацию [{name}]? Это действие необратимо.',
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return

        bot_data = self.bots.get(name)
        if bot_data is None:
            return

        mod_dir = os.path.dirname(bot_data['APP']['MAIN'])
        try:
            shutil.rmtree(mod_dir)
        except OSError as e:
            QMessageBox.critical(self, 'Ошибка удаления', str(e))
            return

        Log.info(f"Модификация [{name}] удалена вручную из интерфейса.")

        self.consoles.pop(name, None)
        self.settings_windows.pop(name, None)
        self.refresh()

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
