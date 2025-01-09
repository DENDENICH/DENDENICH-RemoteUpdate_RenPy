import zipfile
import os
from tkinter import (
    Toplevel,
    Button,
    Label,
    messagebox,
    filedialog
)
from utils import (
    get_path,
    check_exists_path,
    create_folder
)


class CreatePatchWindow(Toplevel):
    """Интерфейс создания патчей"""
    def __init__(self, root):
        super().__init__(master=root)
        self.root = root

        # настройка для окна
        self.root.title("Создание патча")
        self.root.geometry("400x300")  # Размер окна
        self.root.resizable(False, False)  # Запрет изменения размера окна

        # Переменные
        self.archive_update_name = 'update.zip'
        self.last_patch_file = "last_patch.txt"
        self.latest_zip_folder = None
        self.exists_path_to_script = get_path(exists_path=True)

        # Интерфейс
        self.info_label = Label(root, text="Программа готова к работе", font=("Arial", 14))
        self.info_label.pack(pady=10)

        self.select_folder_button = Button(root, text="Создать базовый архив", command=self.create_initial_archive)
        self.select_folder_button.pack(pady=5)

        self.create_patch_button = Button(root, text="Создать патч", command=self.create_patch, state="disabled")
        self.create_patch_button.pack(pady=5)

        # Проверка данных о последнем архиве
        self.load_last_patch_info()


    def load_last_patch_info(self):
        """Загружает информацию о последнем архиве из last_patch.txt."""
        if check_exists_path(self.last_patch_file):
            try:
                with open(self.last_patch_file, "r") as file:
                    data = file.read().strip()

                self.latest_zip_folder = data
                if check_exists_path(
                    get_path(
                        self.exists_path_to_script,
                        self.latest_zip_folder,
                        self.archive_update_name
                    )
                ):
                    self.info_label.config(text=f"Найден архив: {self.archive_update_name}")
                    self.create_patch_button.config(state="normal")
                else:
                    self.info_label.config(text="Архив не найден, создайте новый.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка чтения файла last_patch.txt: {e}")
        else:
            self.info_label.config(text="Файл last_patch.txt не найден. Создайте новый архив.")


    def save_last_patch_info(self, folder):
        """Сохраняет информацию о последнем архиве в файл last_patch.txt."""
        try:
            with open(self.last_patch_file, "w") as file:
                file.write(f"{folder}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка записи в файл last_patch.txt: {e}")


    def create_initial_archive(self):
        """Создаёт первоначальный архив и сохраняет его информацию."""
        folder_game = filedialog.askdirectory(title="Выберите базовую папку для архива")
        if not folder_game:
            return

        # Данные для архива
        folder_archive_name = "update_1.0"

        # Создание папки для нового обновления
        create_folder(
            path_dir=self.exists_path_to_script,
            name_dir=folder_archive_name
        )

        # Создание пути для архива
        archive_path = os.path.join(
            self.exists_path_to_script,
            folder_archive_name,
            self.archive_update_name,
        )

        try:
            with zipfile.ZipFile(archive_path, "w") as zipf:
                for root, dirs, files in os.walk(folder_game):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, os.path.relpath(file_path, folder_game))

            # Сохранение информации о последнем архиве
            self.save_last_patch_info(folder_archive_name)

            self.info_label.config(text=f"Базовый патч создан")
            self.create_patch_button.config(state="normal")
            messagebox.showinfo("Успех", f"Базовый патч создан")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать архив: {e}")


    def create_patch(self):
        """Создаёт патч на основе нового дистрибутива."""
        if not self.latest_zip_folder:
            messagebox.showerror("Ошибка", "Информация о последнем архиве отсутствует.")
            return

        # Выбор новой папки дистрибутива
        new_folder = filedialog.askdirectory(title="Укажите путь к новому дистрибутиву игры")
        if not new_folder:
            return

        # Путь к последнему архиву
        latest_zip_path = get_path(
                            self.exists_path_to_script,
                            self.latest_zip_folder,
                            self.archive_update_name
                        )
        if not check_exists_path(latest_zip_path):
            messagebox.showerror("Ошибка", "Последний архив не найден.")
            return

        # Сравнение состава архива и новой папки
        with zipfile.ZipFile(latest_zip_path, "r") as zipf:
            existing_files = set(zipf.namelist())

        patch_files = []
        for root, dirs, files in os.walk(new_folder):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, new_folder)
                if rel_path not in existing_files:
                    patch_files.append(file_path)

        if not patch_files:
            messagebox.showinfo("Информация", "Новых файлов не найдено.")
            return

        # Создание нового архива патча
        try:
            new_version = self.increment_version(self.latest_zip_folder)
            new_folder_patch_name = f"update_{new_version}"
            # Создание папки для нового патча
            create_folder(
                path_dir=self.exists_path_to_script,
                name_dir=new_folder_patch_name
            )
            new_patch_path = get_path(
                            self.exists_path_to_script,
                            new_folder_patch_name,
                            self.archive_update_name
                        )
            # Смена имени последнего архива
            self.latest_zip_folder = new_folder_patch_name

            with zipfile.ZipFile(new_patch_path, "w") as zipf:
                for file_path in patch_files:
                    zipf.write(file_path, os.path.relpath(file_path, new_folder))

            # Обновление файла last_patch.txt
            self.save_last_patch_info(self.latest_zip_folder)

            # Создание файла версии
            self.create_version_file(new_version, )

            messagebox.showinfo("Успех", f"Патч создан")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать патч: {e}")


    def create_version_file(self, version: str):
        """Создает файл версии."""
        version_file_path = get_path(
                            self.exists_path_to_script,
                            self.latest_zip_folder,
                            "version.txt",
                        )
        with open(version_file_path, "w") as file:
            file.write(f"{version}")


    @staticmethod
    def increment_version(archive_name: str):
        """Увеличивает версию архива на 0.1."""
        version = archive_name.split("_")[1].split(".zip")[0]
        major, minor = map(int, version.split("."))
        minor += 1
        if minor >= 10:
            major += 1
            minor = 0
        return f"{major}.{minor}"


__all__ = [
    'CreatePatchWindow'
]
