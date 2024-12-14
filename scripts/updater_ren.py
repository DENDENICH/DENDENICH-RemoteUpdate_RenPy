import logging
from logging import FileHandler

import hashlib
import base64
from cryptography.fernet import Fernet

import os
import sys

import zipfile
from pathlib import Path
import urllib3


def create_logger(
    file_path: str = "debug_update.log"
    ) -> FileHandler:
    """Функция создания логера для вывода отладки процесса обновления"""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s #%(levelname)-8s %(filename)s: %(lineno)d - %(funcName)s | %(message)s |",
        handlers=[
            logging.FileHandler(file_path),
            logging.StreamHandler(sys.stdout)
        ]
    )

    return logging.getLogger('main_logger')



class Scrto:
        
    def __init__(
        self,
        path: str
    ):

        self.__path = path
        self.__scrto = self.__generate_scrto()
        self._logger = create_logger()


    def __generate_scrto(self):

        index = hashlib.sha256('scarlet_snowScRt0'.encode()).hexdigest()
        return hashlib.sha256(index.encode()).digest()[:32]


    def get_scrto(self) -> str | None:

        try:
            cipher = Fernet(base64.urlsafe_b64encode(self.__scrto))
            with open(self.__path, "rb") as f:
                encrp = f.read()
            decrp = cipher.decrypt(encrp).decode("utf-8")
            return decrp

        except Exception as e:
            self._logger.error(msg=f"Ошибка получения и расшифровки scrto: \n\t{e}")
            return None
        


class Updater:
        
    def __init__(
        self, 
        server_token: str, 
        path_local_game_dir: str, 
        url_remote_version_game: str, 
        url_remote_game_archive: str,
        update_archive: str
            ):
        
        """
        params: disk_token: str - токен аутентификации для подключения к серверу
        params: local_game_dir: str - путь к папке game
        params: remote_version_game: str - api путь к файлу с актуальной версией игры
        params: remote_game_archive: str - api путь к файлу с актуальным патчем игры
        params: update_archive: str - название архива для скачивания в него обновления
        """

        self.server_token = server_token
        self.path_local_game_dir = path_local_game_dir      
        self.path_local_game_version = self.local_game_dir / 'version.txt'
        self.url_remote_version_game = url_remote_version_game
        self.url_remote_game_archive = url_remote_game_archive
        self.update_archive = update_archive


    def _get_headers(self) -> dict:
        """Формирование заголовка"""

        return {
            "Authorization": f"OAuth {self.disk_token}"
        }


    def fetch_remote_version(self) -> str:
        """Получение актуальной версии игры"""

        http = urllib3.PoolManager()
        response = http.request(
            method="GET", 
            url=self.url_remote_version_game, 
            headers=self._get_headers()
            )

        if response.status == 200:
            download_url = response.data.decode("utf-8")
            response = http.request(
                method="GET", 
                url=download_url
                )
            return response.data.decode("utf-8").strip()
        else:
            raise Exception("Не удалось получить версию с сервера")
        

    def download_update(self):
        """Скачивание актуального патча"""

        http = urllib3.PoolManager()
        response = http.request(
            method="GET", 
            url=self.url_remote_game_archive, 
            headers=self.get_headers()
            )

        if response.status == 200:
            download_url = response.data.decode("utf-8")
            with http.request("GET", download_url, preload_content=False) as r, open(self.update_archive, "wb") as out_file:
                out_file.write(r.data)
            return self.update_archive
        else:
            raise Exception("Не удалось скачать обновление")


    def apply_update(self, update_path):
        with zipfile.ZipFile(update_path, 'r') as zip_ref:
            zip_ref.extractall(self.local_game_dir)


    @property
    def exist_version(self):
        version_file = os.path.join(self.local_game_dir, "version.txt")
        if os.path.exists(version_file):
            with open(version_file, "r") as f:
                return f.read().strip()
        return None


    @property
    def new_version(self):
        return self.fetch_remote_version()


    def is_update_available(self):
        return self.exist_version != self.new_version