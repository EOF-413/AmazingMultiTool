import json
import shutil
from os import path

from ...backend.debug import Log
from ...backend.constants import base_dir


class LocalImportError(Exception):
    pass


def import_local(manifest_path):
    if not path.isfile(manifest_path):
        raise LocalImportError('Файл manifest.json не найден.')

    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    try:
        category, name = manifest['APP']
    except (KeyError, ValueError):
        raise LocalImportError('Поле APP в manifest.json заполнено некорректно.')

    source_dir = path.dirname(manifest_path)
    target_dir = path.join(base_dir(), 'plugins', category, name)

    source_dir_norm = path.normpath(path.abspath(source_dir))
    target_dir_norm = path.normpath(path.abspath(target_dir))

    if source_dir_norm == target_dir_norm:
        Log.info(f"Модификация [{name}] уже находится в целевом каталоге.")
        return category, name

    if not path.exists(source_dir):
        raise LocalImportError(f'Исходная директория не найдена: {source_dir}')

    if path.exists(target_dir):
        Log.info(f"Целевая директория уже существует: {target_dir}")
        raise LocalImportError(
            f'Модификация [{name}] уже существует в {target_dir}. '
            'Удалите её вручную перед повторным импортом.'
        )

    try:
        shutil.copytree(source_dir, target_dir)
        Log.info(f"Модификация [{name}] успешно добавлена локально в категорию [{category}].")
    except Exception as e:
        raise LocalImportError(f'Ошибка копирования: {e}')

    return category, name
