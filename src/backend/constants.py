import sys
import shutil
from os import path, makedirs

from ..configs.managed import Config

MARKER = '%%COLOR:'

AMT_API_SOURCE = '''MARKER = '%%COLOR:'


def log(text, color=None):
    if color:
        print(f'{MARKER}{color}%%{text}', flush=True)
    else:
        print(text, flush=True)
'''


def is_frozen():
    return getattr(sys, 'frozen', False)


def base_dir():
    if is_frozen():
        return path.dirname(sys.executable)
    return path.abspath(path.join(path.dirname(__file__), '..', '..'))


def resource_path(relative_path):
    if is_frozen():
        base_path = sys._MEIPASS
    else:
        base_path = path.abspath(path.join(path.dirname(__file__), '..', '..'))
    return path.join(base_path, relative_path)


def ensure_amt_api_written():
    shared_dir = path.join(base_dir(), '_shared')
    makedirs(shared_dir, exist_ok=True)
    api_path = path.join(shared_dir, 'amt_api.py')
    with open(api_path, 'w', encoding='utf-8') as f:
        f.write(AMT_API_SOURCE)
    return shared_dir


def _auto_detect_python():
    if not is_frozen():
        return sys.executable
    for candidate in ('python', 'python3', 'py'):
        found = shutil.which(candidate)
        if found:
            return found
    return None


def get_python_executable():
    config = Config.load()
    manual = config.get('PYTHON_PATH')
    if manual and path.isfile(manual):
        return manual
    return _auto_detect_python()
