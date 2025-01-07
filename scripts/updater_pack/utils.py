from os import path
import sys
from exc import PathException, OtherException



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

    def __init__(self):
        self.path_to_project_game_dir = self.get_path_to_project_game(with_project_game=False) # Путь к проекту игры без папки проекта
        self.path_to_update_data_dir_name = path.join(
            self.get_path_to_project_game(with_project_game=True), # Путь к проекту игры включая папку проекта
            'game',
            'update_data'
        )


    @classmethod
    def get_path_to_project_game(cls, with_project_game: bool):
        """Возвращает путь до папки проекта игры, но не включительно самой папки"""
        if getattr(sys, 'frozen', False):
            # Если скрипт был скомпилирован с помощью PyInstaller
            ph = path.dirname(sys.executable)
        else:
            ph = str(
                path.abspath(__file__).replace(
                    path.basename(__file__),
                    ''
                )
            )
        return ph if with_project_game else '/'.join(*ph.split('//')[0:-1:0]) # Из пути удаляем папку проекта игры


game_dir_paths = GameDirPaths()


class ExistsVersion:
    """Класс для работы с текущей версией"""

    __file_name ='version.enc'
    __path = path.join(
        game_dir_paths.path_to_update_data_dir_name,
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
    path_to_key = path.join(
        game_dir_paths.path_to_update_data_dir_name,
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


__all__ = [
    'remote_paths',
    'exists_version',
    'game_dir_paths',
    'get_encode_key',
]
