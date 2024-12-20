import os


def get_path_version_remote() -> str:
    return '/game/version.txt'

def get_path_update_remote()-> str:
    return '/game/update.zip'


def get_path_game_dir() -> str:
    """Возвращает путь к папке игры game"""

    return str(
        os.path.abspath(__file__).replace(
            old=os.path.basename(__file__), 
            new=''
            )
        ) 

__all__ = [
    'get_path_version_remote',
    'get_path_update_remote',
    'get_path_game_dir'
]