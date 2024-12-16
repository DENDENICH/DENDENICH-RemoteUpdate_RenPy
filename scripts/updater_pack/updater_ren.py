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
        params: local_game_dir: str - путь к папке game
        params: remote_version_game: str - api путь к файлу с актуальной версией игры
        params: remote_game_archive: str - api путь к файлу с актуальным патчем игры
        """

        self.scrto = scrto
        self.path_local_game_dir = path_local_game_dir      
        self.path_local_game_version = self.path_local_game_dir + '/version.txt'
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

        version_file = os.path.join(self.path_local_game_dir, "version.txt")
        if os.path.exists(version_file):
            with open(version_file, "r") as f:
                return f.read().strip()
        else:
            logger.error(msg=f'Файл <version.txt> отсутствует в системе')
            return None
        

    def download_update(
            self,
            update_archive: str = "update.rar"
            ) -> bool:
        """Скачивание актуального патча"""

        try:
            response = self.http.request(
                method="GET", 
                url=self.url_remote_game_archive, 
                headers=self._get_headers
                )

            if response.status == 200:
                download_url = response.data.decode("utf-8")
                with self.http.request("GET", download_url, preload_content=False) as r, open(update_archive, "wb") as out_file:
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
            update_archive: str = "update.rar"
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
        return self._exist_version == self._fetch_remote_version
    

__all__ = ['Updater']
