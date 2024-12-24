import os
from .log import logger

_URL = 'https://cloud-api.yandex.net/v1/disk/resources/download'

def get_path_version_remote() -> str:
    return f'{_URL}?path=/game/version.txt'


def get_path_update_remote()-> str:
    return f'{_URL}?path=/game/update.zip'


def get_path_game_dir() -> str:
    """Возвращает путь к папке игры game"""
    full_path = str(
        os.path.abspath(__file__).replace(
            os.path.basename(__file__),
            ''
        )
    ).split('\\')
    try:
        i = full_path.index('game')
    except ValueError:
        logger.critical(msg='<game> directory not found')
    else:
        return '\\'.join(full_path[:i])


def get_path_scripts_dir() -> str:
    """Возвращает путь к папке, где лежат скрипты модуля обновления"""
    return str(
        os.path.abspath(__file__).replace(
            os.path.basename(__file__),
            ''
        )
    )


def get_path_version() -> str:
    """Возвращает путь к файлу с текущей версией игры"""
    return get_path_game_dir() + '/game/version.txt'


__all__ = [
    'get_path_version_remote',
    'get_path_update_remote',
    'get_path_game_dir',
    'get_path_scripts_dir',
    'get_path_version'
]
