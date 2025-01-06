import sys
from os import makedirs, listdir
from os import path as ph


def create_folder(
        path_dir: str,
        name_dir: str | None = None
) -> None:
    """Функция создания папки по пути и имени, если есть"""
    if name_dir:
        path_dir = ph.join(path_dir, name_dir)
    try:
        makedirs(path_dir)
    except FileExistsError:
        pass


def get_path(
       *paths,
        exists_path: bool = False,
):
    """Функция создания пути"""
    if exists_path:
        if getattr(sys, 'frozen', False):
            # Если скрипт был скомпилирован с помощью PyInstaller
            path = ph.dirname(sys.executable)
        else:
            path = str(
                ph.abspath(__file__).replace(
                    ph.basename(__file__),
                    ''
                )
            )
    else:
        path = ph.join(*paths)

    return path


def check_exists_path(p: str) -> bool:
    """Проверка существования пути"""
    return ph.exists(p)


def get_listdir(path_dir: str):
    return listdir(path_dir)


__all__ = [
    'get_path',
    'create_folder',
    'check_exists_path',
    'get_listdir',
]