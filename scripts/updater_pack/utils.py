import os
from .exc import PathException, OtherException



class RemotePaths:
    """Клас для получения путей к удалённым файлам"""

    __URL = 'https://cloud-api.yandex.net/v1/disk/resources/download'

    @classmethod
    def get_path_version_remote(cls) -> str:
        return f'{cls.__URL}?path=/game/version.txt'

    @classmethod
    def get_path_update_remote(cls)-> str:
        return f'{cls.__URL}?path=/game/update.zip'


class GameDirPaths:
    """Методы для получения различных путей к проекту игры"""

    __path_scripts_updater_pack = str(
            os.path.abspath(__file__).replace(
                os.path.basename(__file__),
                ''
            )
        )

    @classmethod
    def get_path_project_game_dir(cls) -> str:
        """Возвращает путь к папке игры game"""
        path = cls.__path_scripts_updater_pack.split('\\')
        try:
            i = path.index('game')
        except ValueError:
            raise PathException(
                message='dir game/ not found, or updater_pack/ directory is located in the non-game folder'
            )
        except Exception as e:
            raise OtherException(f'Error: \n\t{e}')
        return '\\'.join(path[:i])


    @classmethod
    def get_path_scripts_dir(cls) -> str:
        """Возвращает путь к папке, где лежат скрипты модуля обновления"""
        return cls.__path_scripts_updater_pack


class ExistsVersion:
    """Класс для работы с текущей версией"""

    __path = GameDirPaths.get_path_project_game_dir() + '/game/version.txt'

    @classmethod
    def get_path_version(cls) -> str:
        """Возвращает путь к файлу с текущей версией игры"""
        return cls.__path


    @classmethod
    def get_exist_version(cls) -> str:
        """Получение текущей версии игры"""
        try:
            with open(cls.__path, "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            raise PathException(
                message='file version.txt not found in game/ directory'
            )
        except Exception as e:
            raise OtherException(
                message=f'Error: \n\t{e}'
            )

    @classmethod
    def update_exist_version(cls, new_version: str) -> bool:
        """Обновление текущей версии игры"""
        try:
            with open(cls.__path, "w") as f:
                f.write(new_version)
        except FileNotFoundError:
            raise PathException(
                message='file version.txt not found in game/ directory'
            )
        except Exception as e:
            raise OtherException(
                message=f'Error: \n\t{e}'
            )


def get_decode_key() -> str:
    """Возвращает ключ для декодирования токена"""
    try:
        with open(GameDirPaths.get_path_scripts_dir() + '/key.enc', 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        raise PathException(
            message='file key.enc not found in updater_pack/ directory'
        )


__all__ = [
    'RemotePaths',
    'GameDirPaths',
    'ExistsVersion',
    'get_decode_key'
]
