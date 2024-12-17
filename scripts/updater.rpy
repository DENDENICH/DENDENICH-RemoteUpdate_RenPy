init python:
    from updater_pack import Updater, get_scrto

    def get_updater() -> Updater:
        """Функция создания и возврата объекта обновления Updater"""

        PATH_LOCAL_GAME_DIR = os.path.abspath(__file__).replace(os.path.basename(__file__), '')   
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
            if updater.download_update():
                text "Обновление успешно скачано" style "menu_text_highlight"
            else:
                text "Ошибка при скачивании обновления" style "menu_text_highlight"

            text "Установка обновления..." style "menu_text_highlight"
            if updater.apply_update() and updater.update_exist_version():
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
