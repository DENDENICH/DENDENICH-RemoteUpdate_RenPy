from updater_pack import(
    Updater,
    NetException,
)

from tkinter import (
    messagebox,
    Tk,
    Label,
    Button,
    Frame,
)


class UpdaterWindows(Frame):
    """Клиент обновления игры"""
    def __init__(self, root: Tk):
        super().__init__(master=root)
        self.root = root
        self.pack(padx=10, pady=10)

        # Объект обновления
        try:
            self.updater = Updater()
        except FileNotFoundError as e:
            messagebox.showerror(
                title="Ошибка",
                message=f"Возникла ошибка путей:\n\t{e}"
            )
            self.root.destroy()
        except NetException as ne:
            messagebox.showerror(
                title="Ошибка",
                message=f"Ошибка при подключении к серверу:\n\t{ne}"
            )
            self.root.destroy()
        except Exception as e:
            messagebox.showerror(
                title="Ошибка",
                message=f"Возникла непредвиденная ошибка:\n\t{e}"
            )
            self.root.destroy()

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
        if self.updater.is_update_available():
            self.progress_label.config(text="Скачивание обновления...")
            self.perform_download()  # Запускаем процесс скачивания
        else:
            self.progress_label.config(text="Игра уже обновлена.")


    def perform_download(self):
        """Скачивание с отображением прогресса."""
        try:
            self.updater.download_update() # скачивание обновления
        except NetException as ne:
            messagebox.showerror(
                title="Ошибка",
                message=f"Ошибка при скачивании:\n\t{ne}"
            )
            self.update_button.config(state="normal")  # Включаем кнопку обратно
            return
        except Exception as e:
            messagebox.showerror(
                title="Ошибка",
                message=f"Возникла непредвиденная ошибка при скачивании:\n\t{e}"
            )
            self.update_button.config(state="normal")  # Включаем кнопку обратно
            return

        self.progress_label.config(text="Применение обновления...")
        self.perform_apply() # запуск процесса применения обновления


    def perform_apply(self):
        """Применения обновления"""
        try:
            self.updater.apply_update() # применение обновления
        except FileNotFoundError as e:
            messagebox.showerror(
                title="Ошибка",
                message=f"Возникла ошибка путей:\n\t{e}"
            )
            self.update_button.config(state="normal")  # Включаем кнопку обратно
            return
        except Exception as e:
            messagebox.showerror(
                title="Ошибка",
                message=f"Возникла непредвиденная ошибка при скачивании:\n\t{e}"
            )
            self.update_button.config(state="normal")  # Включаем кнопку обратно
            return

        self.progress_label.config(text="Обновление успешно установлено.")
        self.update_button.config(state="normal")  # Включаем кнопку обратно
        messagebox.showinfo(
            title='Обновлено',
            message=f'Обновление {self.updater.remote_version} было успешно установлено!'
        )
        self.root.destroy()


if __name__ == '__main__':
    root = Tk()
    updater_window = UpdaterWindows(root)
    root.mainloop()
