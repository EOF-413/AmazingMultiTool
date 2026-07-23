# Free
from logging import (
    basicConfig,
    getLogger
)
from os import path, getenv, makedirs

# Local
from ..configs.managed import Config
from .constants import base_dir

logger = getLogger()
config = Config.load()


def _resolve_log_path():
    log_path = path.join(base_dir(), 'debug.log')
    try:
        with open(log_path, 'a', encoding='utf-8'):
            pass
        return log_path
    except OSError:
        fallback_dir = path.join(getenv('APPDATA'), 'EOF413', 'AMT')
        makedirs(fallback_dir, exist_ok=True)
        return path.join(fallback_dir, 'debug.log')


basicConfig(
    level=config["LOG_LEVEL"],
    filemode='w',
    filename=_resolve_log_path(),
    format='[%(asctime)s] [%(levelname)s] [%(filename)s] [%(lineno)d] -> %(message)s',
    datefmt='%d.%m.%Y %H:%M:%S',
    encoding='utf-8'
)


class Log:
    @staticmethod
    def debug(*msg):
        logger.debug(*msg)

    @staticmethod
    def info(*msg):
        logger.info(*msg)

    @staticmethod
    def warning(*msg):
        logger.warning(*msg)

    @staticmethod
    def error(*msg):
        logger.error(*msg)

    @staticmethod
    def critical(*msg):
        logger.critical(*msg)
