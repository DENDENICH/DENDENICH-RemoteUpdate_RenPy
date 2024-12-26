from updater_pack import Updater

updater = Updater()
if updater.is_update_available():
    updater.download_update()
    updater.apply_update()
    updater.update_exist_version()



