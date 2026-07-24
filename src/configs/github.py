import json
import re
import ssl
import time
import urllib.error
import urllib.request
from os import makedirs, path

from ..backend.debug import Log
from ..backend.constants import base_dir

REPOS_LIST_URL = 'https://raw.githubusercontent.com/EOF-413/AMT-Repos/main/repos.json'
BRANCHES_TO_TRY = ('main', 'master')
USER_AGENT = 'AMT-App/1.0'

RETRY_COUNT = 3
RETRY_DELAY = 1


class RemoteReposError(Exception):
    pass


def _parse_repo_url(github_link):
    match = re.search(
        r'github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$',
        (github_link or '').strip()
    )
    if not match:
        return None
    return match.group(1), match.group(2)


def _urlopen_with_retry(url, timeout=15, retries=RETRY_COUNT):
    last_exc = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
            return urllib.request.urlopen(req, timeout=timeout)
        except urllib.error.URLError as e:
            if 'ssl' in str(e).lower() or 'certificate' in str(e).lower():
                try:
                    context = ssl._create_unverified_context()
                    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
                    return urllib.request.urlopen(req, timeout=timeout, context=context)
                except Exception as ssl_e:
                    last_exc = ssl_e
                    Log.debug(f"SSL ошибка (попытка {attempt+1}): {ssl_e}")
            else:
                last_exc = e
                Log.debug(f"Ошибка соединения (попытка {attempt+1}): {e}")

            if attempt < retries - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
    raise RemoteReposError(f'Не удалось загрузить URL: {url}') from last_exc


def _fetch_repo_manifest(github_link):
    parsed = _parse_repo_url(github_link)
    if parsed is None:
        return None
    owner, repo = parsed

    for branch in BRANCHES_TO_TRY:
        raw_url = f'https://raw.githubusercontent.com/{owner}/{repo}/{branch}/manifest.json'
        try:
            response = _urlopen_with_retry(raw_url)
            with response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError:
            continue
        except (urllib.error.URLError, json.JSONDecodeError) as e:
            Log.debug(f"Не удалось прочитать manifest.json из {github_link}: {e}")
            return None
    return None


def _icons_cache_dir():
    cache_dir = path.join(base_dir(), '_cache', 'catalog_icons')
    makedirs(cache_dir, exist_ok=True)
    return cache_dir


def _fetch_repo_icon(name, github_link):
    parsed = _parse_repo_url(github_link)
    if parsed is None:
        return None
    owner, repo = parsed

    cache_path = path.join(_icons_cache_dir(), f'{name}.ico')

    for branch in BRANCHES_TO_TRY:
        raw_url = f'https://raw.githubusercontent.com/{owner}/{repo}/{branch}/icon.ico'
        try:
            response = _urlopen_with_retry(raw_url)
            data = response.read()
        except urllib.error.HTTPError:
            continue
        except urllib.error.URLError as e:
            Log.debug(f"Не удалось скачать icon.ico из {github_link}: {e}")
            return None

        try:
            with open(cache_path, 'wb') as f:
                f.write(data)
        except OSError as e:
            Log.debug(f"Не удалось сохранить icon.ico модификации [{name}]: {e}")
            return None

        return cache_path

    return None


def fetch_available_repos():
    try:
        response = _urlopen_with_retry(REPOS_LIST_URL)
        with response:
            data = json.loads(response.read().decode('utf-8'))
    except RemoteReposError as e:
        Log.error(f"Не удалось загрузить список доступных модификаций: {e}")
        raise
    except json.JSONDecodeError as e:
        Log.error(f"Некорректный формат repos.json: {e}")
        raise RemoteReposError('Некорректный формат repos.json.')

    bots = data.get('bots', {})
    if not isinstance(bots, dict):
        raise RemoteReposError('Поле "bots" в repos.json заполнено некорректно.')

    enriched_bots = {}
    for name, entry in bots.items():
        merged = dict(entry)
        github_link = entry.get('APP_GITHUB_LINK', '')

        manifest = _fetch_repo_manifest(github_link)
        if manifest:
            merged['DESCRIPTION'] = manifest.get('DESCRIPTION', '')
            version_info = manifest.get('APP_VERSION', {})
            merged['VERSION'] = version_info.get('VER', '')
            merged['DEV'] = version_info.get('DEV', '')
        else:
            merged.setdefault('DESCRIPTION', '')
            merged.setdefault('VERSION', '')
            merged.setdefault('DEV', '')

        merged['ICON'] = _fetch_repo_icon(name, github_link)

        enriched_bots[name] = merged

    Log.info(f"Загружен каталог модификаций: {len(enriched_bots)} шт.")
    return enriched_bots
