from os import listdir, path
from json import load
from subprocess import check_call, CalledProcessError

from .debug import Log
from .constants import base_dir, is_frozen, get_python_executable


class GetFiles:
    @staticmethod
    def get_path(*upath):
        return path.join(base_dir(), *upath)

    @staticmethod
    def get_bl(bl=None):
        if bl is None:
            bl = [
                '__init__.py',
                '.git'
            ]
        return bl

    @staticmethod
    def is_exe():
        return is_frozen()

    @classmethod
    def download(cls, name, requirements):
        mode = "скомпилированное" if cls.is_exe() else "исходное"
        Log.debug(f"Приложение запущено как {mode}.")

        python_exe = get_python_executable()
        if python_exe is None:
            Log.error(
                f"Не найден интерпретатор Python для установки зависимостей модификации [{name}]. "
                "Укажите путь к python.exe в настройках приложения."
            )
            return

        cmd = [python_exe, '-m', 'pip', 'install', '-r', requirements]
        Log.info(f"Установка зависимостей для модификации [{name}] интерпретатором [{python_exe}].")
        try:
            check_call(cmd)
            Log.info(f"Все зависимости для модификации [{name}] установлены!")
        except CalledProcessError as e:
            Log.error("Ошибка:", e)

    @classmethod
    def get_files(cls, *sdir, bl=None):
        full_path = path.join(base_dir(), *sdir)
        if not path.exists(full_path):
            Log.debug(f"Каталог не найден: {full_path}")
            return []

        dir = listdir(full_path)

        bl = cls.get_bl(bl)
        log_bl = ['\n-> ' + f for f in bl]
        Log.debug(f"Черный список файлов для каталога [{'/'.join(sdir)}]: {''.join(log_bl)}\n")

        return [
            file
            for file in dir
            if file not in bl
        ]

    @classmethod
    def get_bot(cls):
        bots_dir = path.join(base_dir(), 'plugins', 'bots')
        if not path.exists(bots_dir):
            Log.debug(f"Каталог модификаций не найден: {bots_dir}")
            return {}

        bots_names = cls.get_files('plugins', 'bots')
        log_bots_names = ['\n-> ' + f for f in bots_names]
        Log.debug(f"Найдено {len(bots_names)} модификации(-ий, -я): {''.join(log_bots_names)}\n")

        bots = {}
        for name in bots_names:
            try:
                Log.debug(f"Обработка модификации {name}.\n")
                mod_path = path.join(base_dir(), 'plugins', 'bots', name)
                if not path.isdir(mod_path):
                    Log.error(f"Путь {mod_path} не является директорией.")
                    continue

                files = cls.get_files('plugins', 'bots', name)
                log_files = ['\n-> ' + f for f in files]
                Log.debug(f"Найдено {len(files)} файл(-a, -ов) внутри модификации [{name}]: {''.join(log_files)}\n")

                if 'manifest.json' not in files:
                    Log.error(f"Не найден manifest.json для модификации [{name}].")
                    continue

                man_path = cls.get_path('plugins', 'bots', name, 'manifest.json')
                with open(man_path, 'r', encoding='utf-8') as file:
                    config = load(file)

                if 'requirements.txt' in files:
                    req = cls.get_path('plugins', 'bots', name, 'requirements.txt')
                else:
                    Log.error(f'Не найден файл requirements.txt в модификации [{name}].')
                    continue

                if 'main.py' in files:
                    main = cls.get_path('plugins', 'bots', name, 'main.py')
                else:
                    Log.error(f'Не найден файл main.py в модификации [{name}].')
                    continue

                if 'icon.ico' in files:
                    icon = cls.get_path('plugins', 'bots', name, 'icon.ico')
                else:
                    Log.error(f'Не найден файл icon.ico в модификации [{name}].')
                    continue

                bots[name] = {
                    'DATA': {
                        'APP': config['APP'],
                        'APP_NAME': config['APP_NAME'],
                        'APP_VERSION': config['APP_VERSION'],
                        'APP_GITHUB_LINK': config['APP_GITHUB_LINK']
                    },
                    'APP': {
                        'MAIN': main,
                        'ICON': icon,
                        'REQUIREMENTS': req
                    }
                }

                Log.debug(f"Модификация [{name}] успешно загружена.")
                cls.download(name, req)

            except Exception as e:
                Log.error(f"Возникла ошибка при обработке модификации [{name}]:\n{e}")
                continue

        Log.info("Загрузка модификаций завершена.")
        return bots
