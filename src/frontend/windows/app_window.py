# Download
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QHBoxLayout,
    QLabel, QComboBox, QLineEdit, QPushButton, QFileDialog
)

# Local
from ...configs.managed import Config
from ...backend.constants import get_python_executable

LOG_LEVELS = {
    'DEBUG (10)': 10,
    'INFO (20)': 20,
    'WARNING (30)': 30,
    'ERROR (40)': 40,
    'CRITICAL (50)': 50,
}


class AppSettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Настройки приложения')
        self.setMinimumWidth(420)

        self.config = Config.load()

        root = QVBoxLayout(self)
        form = QFormLayout()

        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(LOG_LEVELS.keys())
        current_label = next(
            (label for label, value in LOG_LEVELS.items() if value == self.config.get('LOG_LEVEL')),
            'DEBUG (10)'
        )
        self.log_level_combo.setCurrentText(current_label)
        form.addRow('Уровень логирования', self.log_level_combo)

        python_row = QHBoxLayout()
        self.python_path_edit = QLineEdit(self.config.get('PYTHON_PATH', ''))
        auto_detected = get_python_executable()
        self.python_path_edit.setPlaceholderText(
            f'Автоопределение: {auto_detected}' if auto_detected else 'Python не найден автоматически'
        )
        python_browse_btn = QPushButton('Обзор...')
        python_browse_btn.clicked.connect(self._on_browse_python)
        python_row.addWidget(self.python_path_edit, stretch=1)
        python_row.addWidget(python_browse_btn)
        form.addRow('Интерпретатор Python', python_row)

        root.addLayout(form)
        root.addWidget(QLabel(
            'Оставьте поле пустым для автоопределения. Укажите путь к python.exe\n'
            'вручную, если модификации не запускаются в собранном приложении.'
        ))

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        cancel_btn = QPushButton('Отмена')
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton('Сохранить')
        save_btn.clicked.connect(self._on_save)
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        root.addLayout(buttons)

    def _on_browse_python(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Укажите python.exe', '', 'Исполняемые файлы (*.exe);;Все файлы (*)'
        )
        if file_path:
            self.python_path_edit.setText(file_path)

    def _on_save(self):
        updated = dict(self.config)
        updated['LOG_LEVEL'] = LOG_LEVELS[self.log_level_combo.currentText()]
        updated['PYTHON_PATH'] = self.python_path_edit.text().strip()
        Config.save(None, updated)
        self.accept()
