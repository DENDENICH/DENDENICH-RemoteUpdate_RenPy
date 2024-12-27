import os
import json
from pathlib import Path

from zipfile import ZipFile
from urllib3 import PoolManager

from .log import logger
from .scrto import get_scrto
from .utils import (
    get_path_game_dir,
    get_path_update_remote,
    get_path_version_remote,
    get_path_scripts_dir,
    get_path_version,
    get_decode_key
)


class Updater:
        
    def __init__(
        self,
        decode_key: str = get_decode_key(),
        url_remote_version_game: str = get_path_version_remote(),
        url_remote_game_archive: str = get_path_update_remote(), 
        ):
        
        """
        params: scrto: str - путь к файлу токена для аутентификации запросов на сервер
        params: local_game_dir: str - путь к игры game
        params: remote_version_game: str - api путь к файлу с актуальной версией игры
        params: remote_game_archive: str - api путь к файлу с актуальным патчем игры
        """

        # добавить аргумент **kwargs для возможности 
        # вносить аргумента незашифрованого ключа аутентификации scrto

        self.path_local_game_dir = Path(get_path_game_dir())

        # получение расшифрованного токена
        path_scrto = get_path_scripts_dir() + '/scrto.enc'
        self.__scrto = get_scrto(
            path=path_scrto,
            key=decode_key
        )

        self.http = PoolManager()

        self.path_local_game_version = get_path_version()
        self.update_zip = self.path_local_game_dir / 'update.zip'

        self.url_remote_version_game = url_remote_version_game
        self.url_remote_game_archive = url_remote_game_archive

        self.remote_version = self._fetch_remote_version
        self.exist_version = self._exist_version


    @property
    def _get_headers(self) -> dict:
        """Формирование заголовка"""

        return {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f'OAuth {self.__scrto}'
}

    @property
    def _fetch_remote_version(self) -> str:
        """Получение актуальной версии игры"""

        try:
            response = self.http.request(
                method="GET", 
                url=self.url_remote_version_game, 
                headers=self._get_headers
                )

            if response.status == 200:
                content = response.data.decode("utf-8")
                download_url = json.loads(content)['href']
                response = self.http.request(
                    method="GET", 
                    url=download_url
                    )
                version = response.data.decode("utf-8").strip()
                logger.debug(msg=f'Версия успешно полученна с удаленного сервера - {version}')
                return version
            else:
                logger.error(msg=f'При запросе возникла ошибка - {response.status}')
                return ''
            
        except Exception as e:
            logger.error(msg=f'Ошибка при получения актуальной версии:\n\t{e}')
            return ''
        

    @property
    def _exist_version(self) -> str:
        """Получение текущей версии игры"""

        if os.path.exists(self.path_local_game_version):
            with open(self.path_local_game_version, "r") as f:
                return f.read().strip()
        else:
            logger.error(msg=f'Файл <version.txt> отсутствует в системе')
            return ''
        

    def download_update(self, progress_callback = None) -> bool:
        """Скачивание актуального патча"""

        try:
            response = self.http.request(
                method="GET", 
                url=self.url_remote_game_archive, 
                headers=self._get_headers
                )

            if response.status == 200:
                content = response.data.decode("utf-8")
                download_url = json.loads(content)['href']
                with self.http.request("GET", download_url, preload_content=False) as update, open(self.update_zip, "wb") as out_file:
                    chunk_size = 1024 * 1024  # Размер блока (1 MB)
                    #download_progress = 0
                    while True:
                        data = update.read(chunk_size)
                        if not data:
                            break
                        out_file.write(data)
                        #download_progress += len(data)
                        #progress_callback(download_progress)  # вызываем коллбек с текущим прогрессом скачивания

                update.release_conn()
                logger.debug(msg='Обновление успешно скачано')
                return True
            else:
                logger.error(msg=f'При запросе возникла ошибка - {response.status}')
                return False
            
        except Exception as e:
            logger.error(msg=f'Ошибка скачивания обновления:\n\t{e}')
            return False


    def apply_update(self) -> bool:
        """Распаковывает архив обновления и добавляет/заменяет файлы в локальной директории игры."""
            
        try:
            with ZipFile(self.update_zip, 'r') as update_zip:
                # распаковка в текущую дерикторию, замена/дополнение файлов игры
                update_zip.extractall(self.path_local_game_dir)
                logger.debug(msg="Обновление успешно применено")

        except Exception as e:
            logger.error(msg=f"Ошибка применения обновления: \n\t{e}")
            return False

    def update_exist_version(self) -> bool:
        """Обновление текущей версии игры"""

        if os.path.exists(self.path_local_game_version):
            with open(self.path_local_game_version, "w") as f:
                f.write(self.remote_version)
            logger.debug(msg=f"Версия успешно обновлена")
            return True
        else:
            logger.error(msg=f'Файл <version.txt> отсутствует в системе')
            return False


    def is_update_available(self) -> bool:
        return self.exist_version != self.remote_version
    

__all__ = ['Updater']
