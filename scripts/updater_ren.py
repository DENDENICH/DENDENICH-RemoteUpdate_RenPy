import logging
from logging import Logger

import hashlib
import base64
from cryptography.fernet import Fernet

import os
import sys

import zipfile
import urllib3


def create_logger(
    file_path: str = "debug_update.log"
    ) -> Logger:
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

logger = create_logger()


def get_scrto(path: str) -> str | None:

    try:
        index = hashlib.sha256('scarlet_snowScRt0'.encode()).hexdigest()

        cipher = Fernet(base64.urlsafe_b64encode(index))
        with open(path, "rb") as f:
            encrp = f.read()
        decrp = cipher.decrypt(encrp).decode("utf-8")
        return decrp

    except Exception as e:
        logger.error(msg=f"Ошибка получения и расшифровки scrto: \n\t{e}")
        return None
        


class Updater:
        
    def __init__(
        self, 
        scrto: str, 
        path_local_game_dir: str, 
        url_remote_version_game: str, 
        url_remote_game_archive: str,
        ):
        
        """
        params: disk_token: str - токен аутентификации для подключения к серверу
        params: local_game_dir: str - путь к папке game
        params: remote_version_game: str - api путь к файлу с актуальной версией игры
        params: remote_game_archive: str - api путь к файлу с актуальным патчем игры
        """

        self.scrto = scrto
        self.path_local_game_dir = path_local_game_dir      
        self.path_local_game_version = self.local_game_dir / 'version.txt'
        self.url_remote_version_game = url_remote_version_game
        self.url_remote_game_archive = url_remote_game_archive

    @property
    def _get_headers(self) -> dict:
        """Формирование заголовка"""

        return {
            "Authorization": f"OAuth {self.scrto}"
        }

    @property
    def _fetch_remote_version(self) -> str | None:
        """Получение актуальной версии игры"""

        try:
            http = urllib3.PoolManager()
            response = http.request(
                method="GET", 
                url=self.url_remote_version_game, 
                headers=self._get_headers
                )

            if response.status == 200:
                download_url = response.data.decode("utf-8")
                response = http.request(
                    method="GET", 
                    url=download_url
                    )
                return response.data.decode("utf-8").strip()
            else:
                logger.error(msg=f'При запросе возникла ошибка - {response.status}')
                return None
            
        except Exception as e:
            logger.error(msg=f'Ошибка при получения актуальной версии:\n\t{e}')
            return None
        

    @property
    def _exist_version(self) -> str | None:
        """Получение текущей версии игры"""

        version_file = os.path.join(self.path_local_game_dir, "version.txt")
        if os.path.exists(version_file):
            with open(version_file, "r") as f:
                return f.read().strip()
        else:
            logger.error(msg=f'Файл <version.txt> отсутствует в системе')
            return None
        

    def download_update(
            self,
            update_archive: str = "update.zip"
            ) -> bool:
        """Скачивание актуального патча"""

        try:
            http = urllib3.PoolManager()
            response = http.request(
                method="GET", 
                url=self.url_remote_game_archive, 
                headers=self._get_headers
                )

            if response.status == 200:
                download_url = response.data.decode("utf-8")
                with http.request("GET", download_url, preload_content=False) as r, open(update_archive, "wb") as out_file:
                    out_file.write(r.data)
                logger.info(msg='Обновление успешно скачано')
                return True
            else:
                logger.error(msg=f'При запросе возникла ошибка - {response.status}')
                return False
            
        except Exception as e:
            logger.error(msg=f'Ошибка скачивания обновления:\n\t{e}')
            return False


    def apply_update(
            self,
            update_archive: str = "update.zip"
        ) -> bool:
        """Распаковывает архив обновления и добавляет/заменяет файлы в локальной директории игры."""
            
        try:
            with zipfile.ZipFile(self.update_archive, "r") as zip_ref:
                for file_info in zip_ref.infolist():                        
                    extracted_path = self.local_game_dir / file_info.filename
                    if file_info.is_dir():
                        extracted_path.mkdir(parents=True, exist_ok=True)
                    else:
                            extracted_path.parent.mkdir(parents=True, exist_ok=True)
                            with extracted_path.open("wb") as output_file:
                                output_file.write(zip_ref.read(file_info))
                logger.info(msg='Обновление успешно установлено')
                return True

        except Exception as e:
            logger.error(msg=f"Ошибка применения обновления: \n\t{e}")
            return False


    def is_update_available(self) -> bool:
        return self.exist_version == self.new_version
    


def get_updater():
    """Функция создания и возврата объекта обновления Updater"""

    PATH_LOCAL_GAME_DIR = os.path.abspath(__file__).replace(
        old=os.path.basename(__file__),
        new=''
        )   
    SCRTO = get_scrto(
        path=PATH_LOCAL_GAME_DIR + '/scrto.enc'
        )
    URL_REMOTE_GAME_VERSION = '/game/version.txt'
    URL_REMOTE_GAME_ARCHIVE = 'game/update.zip'

    return Updater(
        scrto=SCRTO,
        url_remote_version_game=URL_REMOTE_GAME_VERSION,
        url_remote_game_archive=URL_REMOTE_GAME_ARCHIVE,
        path_local_game_dir=PATH_LOCAL_GAME_DIR
    )


updater = get_updater()

__all__ = ['updater']
