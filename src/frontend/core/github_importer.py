import re
import json
import shutil
import tempfile
import zipfile
import urllib.request
import urllib.error
from os import path, listdir

from ...backend.debug import Log
from ...backend.constants import base_dir

BRANCHES_TO_TRY = ('main', 'master')


class GithubImportError(Exception):
    pass


def _parse_repo_url(url):
    match = re.search(r'github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$', url.strip())
    if not match:
        raise GithubImportError('Не удалось распознать ссылку на репозиторий GitHub.')
    return match.group(1), match.group(2)


def _fetch_manifest(owner, repo):
    for branch in BRANCHES_TO_TRY:
        raw_url = f'https://raw.githubusercontent.com/{owner}/{repo}/{branch}/manifest.json'
        try:
            with urllib.request.urlopen(raw_url, timeout=15) as response:
                manifest = json.loads(response.read().decode('utf-8'))
                return manifest, branch
        except urllib.error.HTTPError:
            continue
        except urllib.error.URLError as e:
            raise GithubImportError(f'Ошибка сети: {e}')
    raise GithubImportError(
        'Не удалось найти manifest.json в ветках main/master репозитория.'
    )


def _make_reporthook(progress_callback):
    if progress_callback is None:
        return None

    def _reporthook(block_num, block_size, total_size):
        if total_size > 0:
            percent = int(block_num * block_size * 100 / total_size)
        else:
            percent = -1
        progress_callback(max(-1, min(100, percent)))

    return _reporthook


def import_from_github(url, allow_update=False, progress_callback=None):
    owner, repo = _parse_repo_url(url)
    Log.info(f"Импорт модификации из GitHub: {owner}/{repo}.")

    manifest, branch = _fetch_manifest(owner, repo)

    try:
        category, name = manifest['APP']
    except (KeyError, ValueError):
        raise GithubImportError('Поле APP в manifest.json репозитория заполнено некорректно.')

    target_dir = path.join(base_dir(), 'plugins', category, name)

    if path.exists(target_dir):
        if not allow_update:
            Log.info(f"Целевая директория уже существует: {target_dir}")
            raise GithubImportError(
                f'Модификация [{name}] уже существует в {target_dir}. '
                'Удалите её вручную перед повторным импортом.'
            )
        Log.info(f"Обновление существующей модификации: {target_dir}")
        shutil.rmtree(target_dir)

    zip_url = f'https://codeload.github.com/{owner}/{repo}/zip/refs/heads/{branch}'

    with tempfile.TemporaryDirectory() as tmp_dir:
        zip_path = path.join(tmp_dir, 'repo.zip')
        try:
            urllib.request.urlretrieve(zip_url, zip_path, reporthook=_make_reporthook(progress_callback))
        except urllib.error.URLError as e:
            raise GithubImportError(f'Не удалось скачать репозиторий: {e}')

        if progress_callback is not None:
            progress_callback(100)

        with zipfile.ZipFile(zip_path, 'r') as archive:
            archive.extractall(tmp_dir)

        extracted_root = next(
            path.join(tmp_dir, d)
            for d in listdir(tmp_dir)
            if path.isdir(path.join(tmp_dir, d))
        )

        shutil.copytree(extracted_root, target_dir)

    verb = 'обновлена' if allow_update else 'импортирована'
    Log.info(f"Модификация [{name}] успешно {verb} из GitHub в категорию [{category}].")
    return category, name
