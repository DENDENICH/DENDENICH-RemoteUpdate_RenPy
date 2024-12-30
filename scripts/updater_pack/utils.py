import os
import sys
from .exc import PathException, OtherException



class RemotePaths:
    """Клас для получения путей к удалённым файлам"""

    __URL = 'https://cloud-api.yandex.net/v1/disk/resources/download'

    @property
    def get_path_version_remote(self) -> str:
        return f'{self.__URL}?path=/game/version.txt'

    @property
    def get_path_update_remote(self)-> str:
        return f'{self.__URL}?path=/game/update.zip'


remote_paths = RemotePaths()


class GameDirPaths:
    """Методы для получения различных путей к проекту игры"""

    if getattr(sys, 'frozen', False):
        # Если скрипт был скомпилирован с помощью PyInstaller
        __path_to_project_game_dir = os.path.dirname(sys.executable)
    else:
        __path_to_project_game_dir = str(
            os.path.abspath(__file__).replace(
                os.path.basename(__file__),
                ''
            )
        )
    __update_data_dir_name = 'update_data'
    __game_name_dir_name = 'game'

    @property
    def get_path_project_game_dir(self) -> str:
        """Возвращает путь к папке игры game"""
        return self.__path_to_project_game_dir


    @property
    def get_path_data_update_dir(self) -> str:
        """Возвращает путь к папке, где лежат скрипты модуля обновления"""
        path = os.path.join(
                self.__path_to_project_game_dir,
                self.__game_name_dir_name,
                self.__update_data_dir_name
        )
        return path


game_dir_paths = GameDirPaths()


class ExistsVersion:
    """Класс для работы с текущей версией"""

    __file_name ='version.enc'
    __path = os.path.join(
        game_dir_paths.get_path_data_update_dir,
        __file_name
    )

    @property
    def get_path_version(self) -> str:
        """Возвращает путь к файлу с текущей версией игры"""
        return self.__path


    @property
    def get_exist_version(self) -> str:
        """Получение текущей версии игры"""
        try:
            with open(self.__path, "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            raise PathException(
                message='file version.enc not found in update_data directory'
            )
        except Exception as e:
            raise OtherException(
                message=f'Error: \n\t{e}'
            )


    def update_exist_version(self, new_version: str) -> None:
        """Обновление текущей версии игры"""
        try:
            with open(self.__path, "w") as f:
                f.write(new_version)
        except FileNotFoundError:
            raise PathException(
                message='file version.enc not found in update_data directory'
            )
        except Exception as e:
            raise OtherException(
                message=f'Error: \n\t{e}'
            )


exists_version = ExistsVersion()


def get_encode_key() -> str:
    """Возвращает ключ для декодирования токена"""
    path_to_key = os.path.join(
        game_dir_paths.get_path_data_update_dir,
        'key.enc'
    )
    try:
        with open(path_to_key, 'r') as file:
            value = file.read().strip()
        return value
    except FileNotFoundError:
        raise PathException(
            message='file key.enc not found in update_data directory'
        )

def get_log_path() -> str:
    path = os.path.join(
        game_dir_paths.get_path_data_update_dir,
        'update_log.txt'
    )
    if not os.path.exists(path):
        raise PathException(
            message='file update_log.txt not found in update_data directory'
        )
    return path


__all__ = [
    'remote_paths',
    'exists_version',
    'game_dir_paths',
    'get_encode_key',
    'get_log_path'
]
