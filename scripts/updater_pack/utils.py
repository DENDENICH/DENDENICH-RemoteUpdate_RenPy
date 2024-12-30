import os
import sys


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
        __path_game_project = os.path.dirname(sys.executable)
    else:
        __path_game_project = str(
            os.path.abspath(__file__).replace(
                os.path.basename(__file__),
                ''
            )
        )
    __game_dir_name = 'game'
    __update_data_dir_name = 'update_data'

    @property
    def get_path_project_game_dir(self) -> str:
        """Возвращает путь к папке игры game"""
        return os.path.join(
            self.__path_game_project,
            self.__game_dir_name
        )

    @property
    def get_path_data_update_dir(self) -> str:
        """Возвращает путь к папке update_data, где лежат данные обновления"""
        return os.path.join(
            self.__path_game_project,
            self.__game_dir_name,
            self.__update_data_dir_name
        )

game_dir_paths = GameDirPaths()


class ExistsVersion:
    """Класс для работы с текущей версией"""

    __file_name = 'version.enc'
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
        with open(self.__path, "r") as f:
            return f.read().strip()


    def update_exist_version(self, new_version: str) -> None:
        """Обновление текущей версии игры"""
        with open(self.__path, "w") as f:
            f.write(new_version)

exists_version = ExistsVersion()


def get_decode_key() -> str:
    """Возвращает ключ для декодирования токена"""
    path_to_key = os.path.join(
        game_dir_paths.get_path_data_update_dir,
        'key.enc'
    )
    with open(path_to_key, 'r') as file:
        return file.read().strip()


__all__ = [
    'remote_paths',
    'exists_version',
    'game_dir_paths',
    'get_decode_key'
]
