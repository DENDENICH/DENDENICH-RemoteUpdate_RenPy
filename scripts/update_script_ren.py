from updater_pack import Updater
from tkinter import (
    messagebox,
    Tk,
    Label,
    Button,
    Frame,
    ttk,
)


class UpdaterWindows(Frame):
    """Клиент обновления игры"""
    def __init__(self, root: Tk):
        super().__init__(master=root)
        self.root = root
        self.updater = Updater()
        self.pack(padx=10, pady=10)

        self.root.title("Обновление")
        self.root.geometry("400x200")  # Размер окна
        self.root.resizable(False, False)

        # Метка текущей версии
        self.version_label = Label(self, text=f"Текущая версия: {self.updater.exist_version}", font=("Arial", 12))
        self.version_label.pack(pady=5)

        # Кнопка обновления
        self.update_button = Button(self, text="Обновить игру", command=self.start_update, bg="#4CAF50", fg="white",
                                       font=("Arial", 10, "bold"))
        self.update_button.pack(pady=10)

        # Оповещение прогресса
        self.progress_label = Label(self, text="Прогресс", font=("Arial", 10), state='disabled')
        self.progress_label.pack(pady=6)

        #
        # self.progress_bar = ttk.Progressbar(self, length=300, mode="determinate")
        # self.progress_bar.pack(pady=5)


    def start_update(self):
        """Запускает процесс обновления."""
        self.update_button.config(state="disabled")  # Отключаем кнопку во время обновления
        self.update()  # Обновляем интерфейс

        # Проверка обновлений
        new_version = self.updater.is_update_available()
        if new_version != self.updater.exist_version:
            self.progress_label.config(text="Скачивание обновления...")

        else:
            self.progress_label.config(text="Игра уже обновлена.")

    def perform_download(self):
        """Скачивание с отображением прогресса."""
        if self.updater.download_update(): # скачивание обновления
            self.progress_label.config(text="Применение обновления...")
            self.perform_apply()

    def perform_apply(self):
        """Применения обновления"""
        if self.updater.apply_update(): # применение обновления
            self.progress_label.config(text="Обновление успешно установлено.")
            self.update_button.config(state="normal")  # Включаем кнопку обратно
            messagebox.showinfo(
                title='Обновлено',
                message=f'Обновление {self.updater.remote_version} было успешно установлено!'
            )


root = Tk()
updater_window = UpdaterWindows(root)
root.mainloop()
