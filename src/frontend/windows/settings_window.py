from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QHBoxLayout,
    QLabel, QLineEdit, QCheckBox, QSpinBox, QDoubleSpinBox,
    QPushButton
)
from PyQt5.QtGui import QIcon
from os import path, getenv, makedirs
import json


class ModSettingsWindow(QDialog):
    def __init__(self, name, app_id, app_name, icon_path, parent=None):
        super().__init__(parent)
        self.name = name
        self.app_id = app_id
        self._fields = {}

        self.setWindowTitle(f'Настройки — {app_name}')
        self.setWindowIcon(QIcon(icon_path))
        self.setMinimumWidth(360)

        self.config = self._load_mod_config()

        root = QVBoxLayout(self)

        if not self.config:
            root.addWidget(QLabel('У этой модификации пока нет настроек.'))
            root.addWidget(QLabel('Нажмите "Сохранить" для создания настроек по умолчанию.'))
        else:
            form = QFormLayout()
            for key, value in self.config.items():
                field = self._build_field(value)
                self._fields[key] = field
                form.addRow(key, field)
            root.addLayout(form)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        cancel_btn = QPushButton('Отмена')
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton('Сохранить')
        save_btn.clicked.connect(self._on_save)
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        root.addLayout(buttons)

    def _get_mod_config_path(self):
        app_data = getenv('APPDATA')
        if app_data is None:
            app_data = path.expanduser('~')
        config_dir = path.join(app_data, 'EOF413', 'AMT', 'plugins', self.app_id[0], self.app_id[1])
        makedirs(config_dir, exist_ok=True)
        return path.join(config_dir, 'config.json')

    def _load_mod_config(self):
        config_path = self._get_mod_config_path()
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def _save_mod_config(self, data):
        config_path = self._get_mod_config_path()
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def _build_field(self, value):
        if isinstance(value, bool):
            field = QCheckBox()
            field.setChecked(value)
        elif isinstance(value, int):
            field = QSpinBox()
            field.setRange(-1000000000, 1000000000)
            field.setValue(value)
        elif isinstance(value, float):
            field = QDoubleSpinBox()
            field.setRange(-1000000000, 1000000000)
            field.setValue(value)
        else:
            field = QLineEdit(str(value))
        return field

    def _on_save(self):
        if self.config is None:
            updated = {
                "HOLD": 1.25,
                "COOLDOWN": 0.75,
                "MIN_MATCH": 0.40
            }
        else:
            updated = dict(self.config)

        for key, field in self._fields.items():
            if isinstance(field, QCheckBox):
                updated[key] = field.isChecked()
            elif isinstance(field, (QSpinBox, QDoubleSpinBox)):
                updated[key] = field.value()
            else:
                updated[key] = field.text()

        self._save_mod_config(updated)
        self.accept()
