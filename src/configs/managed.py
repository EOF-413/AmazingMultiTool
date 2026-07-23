from os import getenv, makedirs, path
from json import load, dump, JSONDecodeError

DEFAULT = {
    'LOG_LEVEL': 10,
    'PYTHON_PATH': ''
}


class Config:
    @staticmethod
    def path(APP=None):
        app_data = getenv('APPDATA')
        config_dir = path.join(app_data, 'EOF413', 'AMT')

        if APP:
            config_dir = path.join(app_data, 'EOF413', 'AMT', 'plugins', APP[0], APP[1])

        if not path.exists(config_dir):
            makedirs(config_dir)

        return path.join(config_dir, 'config.json')

    @staticmethod
    def load(APP=None):
        if APP:
            try:
                with open(Config.path(APP), 'r', encoding='utf-8') as f:
                    config = load(f)
                    for key, val in DEFAULT.items():
                        if key not in config:
                            config[key] = val
                    return config
            except (FileNotFoundError, JSONDecodeError):
                Config.save(APP, DEFAULT)
                return DEFAULT.copy()
        else:
            try:
                with open(Config.path(), 'r', encoding='utf-8') as f:
                    config = load(f)
                    for key, val in DEFAULT.items():
                        if key not in config:
                            config[key] = val
                    return config
            except (FileNotFoundError, JSONDecodeError):
                Config.save(None, DEFAULT)
                return DEFAULT.copy()

    @staticmethod
    def save(APP, data):
        if APP:
            with open(Config.path(APP), 'w', encoding='utf-8') as f:
                dump(data, f, indent=4, ensure_ascii=False)
        else:
            with open(Config.path(), 'w', encoding='utf-8') as f:
                dump(data, f, indent=4, ensure_ascii=False)
