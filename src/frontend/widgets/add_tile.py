# Download
from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout, QMenu, QAction
from PyQt5.QtCore import Qt, pyqtSignal, QSize

# Local
from ..styles.theme import BG_SECONDARY, BORDER
from .mod_tile import TILE_WIDTH, TILE_HEIGHT


class AddModTile(QFrame):
    import_github_requested = pyqtSignal()
    add_local_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(TILE_WIDTH, TILE_HEIGHT)
        self.setObjectName('AddModTile')
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            #AddModTile {{
                background-color: {BG_SECONDARY};
                border: 2px dashed {BORDER};
                border-radius: 10px;
            }}
            #AddModTile:hover {{
                border-color: #58a6ff;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        plus_label = QLabel('+')
        plus_label.setAlignment(Qt.AlignCenter)
        plus_label.setStyleSheet('font-size: 48px; color: #8b949e;')
        layout.addWidget(plus_label)

        text_label = QLabel('Добавить модификацию')
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setStyleSheet('color: #8b949e; font-size: 13px;')
        layout.addWidget(text_label)

    def sizeHint(self):
        return QSize(TILE_WIDTH, TILE_HEIGHT)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._show_menu(event.globalPos())
        super().mousePressEvent(event)

    def _show_menu(self, pos):
        menu = QMenu(self)
        action_github = QAction('Импортировать из GitHub', self)
        action_local = QAction('Добавить локально', self)
        menu.addAction(action_github)
        menu.addAction(action_local)

        chosen = menu.exec_(pos)
        if chosen == action_github:
            self.import_github_requested.emit()
        elif chosen == action_local:
            self.add_local_requested.emit()
