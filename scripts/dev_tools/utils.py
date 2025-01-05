import base64
import hashlib
import random
import string
import sys
from os import makedirs, listdir
from os import path as ph
from cryptography.fernet import Fernet


class Hash:
    """Class hashing token"""

    @staticmethod
    def get_unique_index(key: str) -> str:
        """Get unique index"""
        return hashlib.sha256(key.encode()).hexdigest()


    @staticmethod
    def generate_key(index) -> bytes:
        """Get key"""
        return hashlib.sha256(index.encode()).digest()[:32]


    @staticmethod
    def encrypt_token(token, key) -> bytes:
        """Decode token, get decoding token"""
        cipher = Fernet(base64.urlsafe_b64encode(key))
        return cipher.encrypt(token.encode("utf-8"))


def generate_key(length=32):
    # Создаем набор символов: буквы и цифры
    characters = string.ascii_letters + string.digits + string.punctuation
    # Генерируем строку заданной длины
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string


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
    'Hash',
    'get_path',
    'create_folder',
    'generate_key',
    'check_exists_path',
    'get_listdir'
]