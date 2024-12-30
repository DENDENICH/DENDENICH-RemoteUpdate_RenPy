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
        __path_scripts_updater_pack = os.path.dirname(sys.executable)
    else:
        __path_scripts_updater_pack = str(
            os.path.abspath(__file__).replace(
                os.path.basename(__file__),
                ''
            )
        )

    @property
    def get_path_project_game_dir(self) -> str:
        """Возвращает путь к папке игры game"""
        path = self.__path_scripts_updater_pack.split('\\')
        try:
            i = path.index('game')
        except ValueError:
            raise PathException(
                message='dir game/ not found, or updater_pack/ directory is located in the non-game folder'
            )
        except Exception as e:
            raise OtherException(f'Error: \n\t{e}')
        return '\\'.join(path[:i])


    @property
    def get_path_scripts_dir(self) -> str:
        """Возвращает путь к папке, где лежат скрипты модуля обновления"""
        return self.__path_scripts_updater_pack + '/updater_pack'


game_dir_paths = GameDirPaths()


class ExistsVersion:
    """Класс для работы с текущей версией"""

    __path = game_dir_paths.get_path_project_game_dir + '/game/version.txt'

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
                message='file version.txt not found in game/ directory'
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
                message='file version.txt not found in game/ directory'
            )
        except Exception as e:
            raise OtherException(
                message=f'Error: \n\t{e}'
            )


exists_version = ExistsVersion()


def get_decode_key() -> str:
    """Возвращает ключ для декодирования токена"""
    try:
        with open(game_dir_paths.get_path_scripts_dir + '/key.enc', 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        raise PathException(
            message='file key.enc not found in updater_pack/ directory'
        )


__all__ = [
    'remote_paths',
    'exists_version',
    'game_dir_paths',
    'get_decode_key'
]
