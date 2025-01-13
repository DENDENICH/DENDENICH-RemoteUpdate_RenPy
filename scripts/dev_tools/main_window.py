from tkinter import (
    Frame,
    Tk,
    Button,
    Label,
    messagebox,
    filedialog
)
from utils import (
    check_exists_path
)
from create_patch import CreatePatchWindow
from create_data import CreateDataWindow


class MainWindow(Frame):
    """Главное окно"""
    def __init__(self, root: Tk):
        super().__init__(master=root)
        self.root = root
        self.pack(padx=10, pady=10)

        # Список путей к папкам
        self.folder_paths = []
        self.current_folder: str | None = None

        # Загрузка путей из файла
        self.load_paths()

        # Интерфейс окна

        # Настройка для окна обновления
        self.root.title("Создание и генерация данных")
        self.root.geometry("400x400")  # Размер окна
        self.root.resizable(False, False)  # Запрет изменения размера окна

        # Кнопки
        button_frame = Frame(self)  # Создаём контейнер для кнопок
        button_frame.pack(fill="x", pady=10)

        self.folder_label = Label(root, text="Выберите папку проекта игры", font=("Arial", 14))
        self.folder_label.pack(pady=10)

        self.add_folder_button = Button(root, text="Выберите папку проекта игры", command=self.add_folder)
        self.add_folder_button.pack(pady=5)

        self.switch_folder_button = Button(root, text="Переключить папку", command=self.switch_folder,
                                              state="disabled")
        self.switch_folder_button.pack(pady=5)

        self.create_data_button = Button(root, text="Создать токен обновления", command=self.open_create_data_window, state="disabled")
        self.create_data_button.pack(pady=5)

        self.create_patch_button = Button(root, text="Создать патч", command=self.open_create_patch_window, state="disabled")
        self.create_patch_button.pack(pady=5)

        # Обновление интерфейса после загрузки путей путей
        self.update_interface()


    def open_create_patch_window(self):
        CreatePatchWindow(
            root=self.root
        )


    def open_create_data_window(self):
        CreateDataWindow(
            root=self.root,
            game_project_path=self.current_folder
        )


    def load_paths(self):
        """Загружает пути из файла paths.txt."""
        if check_exists_path("paths.txt"):
            with open("paths.txt", "r") as file:
                self.folder_paths = [line.strip() for line in file.readlines()]
            if self.folder_paths:
                self.current_folder = self.folder_paths[0]


    def save_paths(self):
        """Сохраняет пути в файл paths.txt."""
        with open("paths.txt", "w") as file:
            for path in self.folder_paths:
                file.write(path + "\n")


    def add_folder(self):
        """Добавляет новый путь к папке."""
        folder = filedialog.askdirectory(title="Выберите папку к дистрибутиву")
        if folder:
            if folder not in self.folder_paths:
                self.folder_paths.append(folder)
                self.current_folder = folder
                self.save_paths()
                self.update_interface()
                messagebox.showinfo("Успех", f"Папка проекта игры добавлена: {folder}")
            else:
                messagebox.showwarning("Внимание", "Эта папка проекта уже добавлена.")


    def switch_folder(self):
        """Переключает текущую папку."""
        if len(self.folder_paths) <= 1:
            messagebox.showerror("Ошибка", "Нет доступных папок для переключения. Пожалуйста, добавьте ещё одну папку проекта игры")
            return

        # Выбор новой папки из списка
        folder = filedialog.askdirectory(title="Выберите папку для переключения")
        if folder and folder in self.folder_paths:
            self.current_folder = folder
            self.update_interface()
            messagebox.showinfo("Успех", f"Текущая папка: {folder}")
        else:
            messagebox.showwarning("Внимание", "Выбранная папка отсутствует в списке.")


    def update_interface(self):
        """Обновляет состояние интерфейса."""
        if self.current_folder:
            name_game_dir = self.current_folder.split('/')[-1]
            self.folder_label.config(text=f"Текущая папка: {name_game_dir}")
            self.create_data_button.config(state="normal")
            self.create_patch_button.config(state="normal")
            self.switch_folder_button.config(state="normal")
        else:
            self.folder_label.config(text="Выберите папку проекта игры")
            self.create_data_button.config(state="disabled")
            self.create_patch_button.config(state="disabled")
            self.switch_folder_button.config(state="disabled")


__all__ = [
    'MainWindow'
]