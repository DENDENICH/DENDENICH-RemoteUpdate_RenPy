import os
import json
from pathlib import Path

import zipfile
from urllib3 import PoolManager

from .log import logger


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
        params: local_game_dir: str - путь к game/
        params: remote_version_game: str - api путь к файлу с актуальной версией игры
        params: remote_game_archive: str - api путь к файлу с актуальным патчем игры
        """

        self.scrto = scrto

        self.path_local_game_dir = Path(path_local_game_dir)
        self.path_local_game_version = self.path_local_game_dir / '/version.txt'
        self.update_zip = self.path_local_game_dir / 'update.zip'

        self.remote_version = self._fetch_remote_version
        self.exist_version = self._exist_version

        self.url_remote_version_game = url_remote_version_game
        self.url_remote_game_archive = url_remote_game_archive
        self.http = PoolManager()

    @property
    def _get_headers(self) -> dict:
        """Формирование заголовка"""

        return {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f'OAuth {self.scrto}'
}

    @property
    def _fetch_remote_version(self) -> str | None:
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
                logger.error(msg=f'Версия успешно полученна с удаленного сервера - {version}')
                return version
            else:
                logger.error(msg=f'При запросе возникла ошибка - {response.status}')
                return None
            
        except Exception as e:
            logger.error(msg=f'Ошибка при получения актуальной версии:\n\t{e}')
            return None
        

    @property
    def _exist_version(self) -> str | None:
        """Получение текущей версии игры"""

        if os.path.exists(self.path_local_game_version):
            with open(self.path_local_game_version, "r") as f:
                return f.read().strip()
        else:
            logger.error(msg=f'Файл <version.txt> отсутствует в системе')
            return None
        

    def download_update(self) -> bool:
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
                    while True:
                        data = update.read(chunk_size)
                        if not data:
                            break
                        out_file.write(data)
                update.release_conn()
                logger.info(msg='Обновление успешно скачано')
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
            with zipfile.ZipFile(self.update_zip, "r") as update_zip:
                for file_info in update_zip.infolist():
                    extracted_path = self.path_local_game_dir / file_info.filename
                    if file_info.is_dir():
                        os.makedirs(
                            name=extracted_path,
                            exist_ok=True
                        )
                    else:
                        os.makedirs(os.path.dirname(extracted_path), exist_ok=True)
                        with update_zip.open(file_info) as src_file:
                            with extracted_path.open("wb") as output_file:
                                output_file.write(src_file.read())
                logger.info(msg='Обновление успешно установлено')
                return True

        except Exception as e:
            logger.error(msg=f"Ошибка применения обновления: \n\t{e}")
            return False


    def is_update_available(self) -> bool:
        return self.exist_version == self.remote_version
    

    def update_exist_version(self) -> bool:
        """Обновление текущей версии игры"""

        if os.path.exists(self.path_local_game_version):
            with open(self.path_local_game_version, "w") as f:
                f.write(self.remote_version)
                return True
        else:
            logger.error(msg=f'Файл <version.txt> отсутствует в системе')
            return None 
    

__all__ = ['Updater']
