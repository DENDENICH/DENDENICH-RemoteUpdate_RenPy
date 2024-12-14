init python:
    import logging
    import os
    import sys
    import zipfile
    from pathlib import Path
    
    import urllib3
    
    
    

    


    
    class Updater:
        """
        Класс для реализации функции обновления контента в пользовательской папке игры
        """

        def __init__(
            self, 
            disk_token: str, 
            local_game_dir: str = "./game", 
            remote_version_game: str = "/game/version.txt", 
            remote_game_archive: str = "/game/update.zip",
            update_archive: str = "update.zip"
            ):

            self.disk = yadisk.YaDisk(token=disk_token)
            self.local_game_dir = Path(local_game_dir)       
            self.local_game_version = self.local_game_dir / 'version.txt'
            self.remote_version_game = remote_version_game
            self.remote_game_archive = remote_game_archive
            self.update_archive = update_archive


        @property
        def _new_version(self) -> str:
            """Возвращает версию игры из файла на Яндекс.Диске."""

            try:
                with self.disk.open(self.remote_version_game) as remote_file:
                    version = remote_file.read().decode('utf-8').strip()
                return version

            except Exception as e:
                logger.error(msg=f"Ошибка чтения версии с Яндекс.Диска: \n\t{e}")
                return None


        @property
        def _exist_version(self) -> str | None:
            """Возвращает текущую версию игры из локального файла."""

            try:
                if self.local_game_version.exists():
                    with open(self.local_game_version, "r") as f:
                        return f.read().strip()
                else:
                    logger.error(msg="Локальный файл version.txt версии не найден.")
                    return None

            except Exception as e:
                logger.error(msg=f"Ошибка чтения локальной версии: \n\t{e}")
                return None

        
        @property
        def is_update_available(self) -> bool:
            """Сравнивает версии игры и возвращает True, если доступно обновление."""

            new_version = self._new_version
            exist_version = self._exist_version
            if new_version and exist_version:
                return new_version > exist_version
            return False


        @property
        def download_update(self) -> bool:
            """Скачивает архив обновления с Яндекс.Диска."""

            try:
                self.disk.download(self.remote_game_archive, self.update_archive)
                logger.info(msg=f"Обновление успешно скачано в {self.update_archive}.")
                return True

            except Exception as e:
                logger.error(msg=f"Ошибка скачивания обновления: \n\t{e}")
                return False


        @property
        def apply_update(self) -> bool:
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

        @property
        def update_version(self) -> bool:
            """Обновляет локальную версию игры до актуальной"""

            try:
                with open(self.local_game_version, "r") as f:
                    f.write(self.remote_version_file)
                logger.info(msg='Обновление версии успешно установлено')
                return True

            except Exception as e:
                logger.error(msg=f"Ошибка перезаписи версии: \n\t{e}")
                return False
                
    
    scrto = Scrto()
    updater = Updater()



# интерфейс обновления
screen updater_screen():
    tag menu

    frame:
        style "menu_frame"
        xalign 0.5
        yalign 0.5

        vbox:
            style "menu"

            label "Обновление игры"

            text "Текущая версия: [updater.current_version]" style "menu_text"
            text "Доступная версия: [updater.new_version]" style "menu_text"

            # Процедуры скачивания и установки обновления
            text "Скачивание обновления..." style "menu_text_highlight"
            if updater.download_update:
                text "Обновление успешно скачано" style "menu_text_highlight"
            else:
                text "Ошибка при скачивании обновления" style "menu_text_highlight"

            text "Установка обновления..." style "menu_text_highlight"
            if updater.apply_update and updater.update_version:
                text "Обновление успешно установленно" style "menu_text_highlight"
            else:
                text "Ошибка при установки обновления" style "menu_text_highlight"

            textbutton "Закрыть" action Return()


# Автоматическая проверка обновлений при загрузке экрана
label start:
    python:
        update_available = updater.is_update_available()

    if update_available: # если доступно обновление
        show screen updater_screen

    return
