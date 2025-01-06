from tkinter import (
    Frame,
    Toplevel,
    Tk,
    Entry,
    Button,
    Label,
    messagebox
)
from utils import (
    get_path,
    create_folder,
    get_listdir,
    check_exists_path
)
from git import Repo, InvalidGitRepositoryError


def initialize_repo_if_needed(repo_path):
    """
    Инициализирует Git-репозиторий в указанной директории, если он еще не существует.
    """
    try:
        # Проверяем, является ли директория уже Git-репозиторием
        repo = Repo(repo_path)
    except InvalidGitRepositoryError:
        # Если нет, инициализируем новый репозиторий
        repo = Repo.init(repo_path)

    return repo


class CreatePatchWindow(Toplevel):
    """Интерфейс создания патчей"""
    def __init__(self, game_path: str, repo, root):
        super().__init__(master=root)
        self.root = root

        self.game_path = game_path
        self.repo = repo

        # Создание интерфейса


__all__ = [
    'initialize_repo_if_needed',
    'CreatePatchWindow'
]
