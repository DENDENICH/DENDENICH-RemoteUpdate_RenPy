import json
import os
from pathlib import Path

from zipfile import ZipFile
from urllib3 import PoolManager

from exc import (
    PathException,
    NetException,
    OtherException
)
from scrto import get_scrto
from utils import (
    remote_paths,
    game_dir_paths,
    exists_version,
    get_encode_key
)


class Updater:
        
    def __init__(self):

        self.path_to_project_game_dir = Path(game_dir_paths.path_to_project_game_dir)

        # Получение токена аутентификации
        key = get_encode_key()
        self.__scrto = get_scrto(
            path=os.path.join(
                game_dir_paths.path_to_update_data_dir_name,
                'scrto.enc'
            ),
            key=key
        )

        # Формирование пути к файлу обновления
        self.path_to_update_zip = os.path.join(
            self.path_to_project_game_dir,
            'update.zip'
        )
        self.http = PoolManager()

        self.remote_version = self._fetch_remote_version
        self.exist_version = exists_version.get_exist_version


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
                url=remote_paths.get_path_version_remote,
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
                return version
            else:
                raise NetException(
                    code=response.status,
                    message='Error fetching remote version'
                )
        except Exception as e:
            raise OtherException(
                message=f'Error \n\t{e}'
            )
        

    def download_update(self, progress_callback = None) -> None:
        """Скачивание актуального патча"""

        try:
            response = self.http.request(
                method="GET", 
                url=remote_paths.get_path_update_remote,
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
            else:
                raise NetException(
                    code=response.status,
                    message='Error downloading'
                )
            
        except Exception as e:
            raise OtherException(
                message=f'Error \n\t{e}'
            )


    def apply_update(self) -> None:
        """Распаковывает архив обновления и добавляет/заменяет файлы в локальной директории игры."""
            
        try:
            with ZipFile(self.update_zip, 'r') as update_zip:
                # распаковка в текущую дерикторию, замена/дополнение файлов игры
                update_zip.extractall(self.path_project_game_dir)

        except FileNotFoundError:
            raise PathException(
                message=f'file patch not found in\n{self.path_project_game_dir}'
            )

        except Exception as e:
            OtherException(
                message=f'Error applying update \n\t{e}'
            )
        # Удаление архива
        os.remove(self.update_zip)
        # Изменение локальной версии
        exists_version.update_exist_version(new_version=self.remote_version)


    def is_update_available(self) -> bool:
        return self.exist_version != self.remote_version
    

__all__ = ['Updater']
