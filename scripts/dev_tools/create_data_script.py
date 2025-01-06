import base64
import hashlib
import random
import string
from urllib3 import PoolManager
from cryptography.fernet import Fernet
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


class Hash:
    """Class hashing token"""

    @staticmethod
    def get_unique_index(key: str) -> str:
        """Get unique index"""
        return hashlib.sha256(key.encode()).hexdigest()


    @staticmethod
    def generate_key(index) -> bytes:
        """Get key"""
        return hashlib.sha256(index.encode()).digest()[:32]


    @staticmethod
    def encrypt_token(token, key) -> bytes:
        """Decode token, get decoding token"""
        cipher = Fernet(base64.urlsafe_b64encode(key))
        return cipher.encrypt(token.encode("utf-8"))


def generate_key(length=32):
    # Создаем набор символов: буквы и цифры
    characters = string.ascii_letters + string.digits + string.punctuation
    # Генерируем строку заданной длины
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string


class CreateDataWindow(Toplevel):
    """Класс окна обновления"""

    def __init__(self, root: Tk, exists_path: str):

        # проверка каталогов перед запуском утилиты
        self.root = root
        if not self._check_scripts_dir():
            self.root.destroy() # Утилита закрывается, если есть конфликты с путями

        super().__init__(master=root)

        # настройка для окна обновления
        self.root.title("Создание и генерация данных")
        self.root.geometry("400x200")  # Размер окна
        self.root.resizable(False, False)  # Запрет изменения размера окна


        # Поле для токена
        token_entry_label = Label(
            self,
            text='Введите токен API Яндекс.Диска:',
            font=("Arial", 10, "bold"),
            anchor="w"
        )
        token_entry_label.pack(fill="x", pady=5)
        self.token_entry = Entry(self, width=50)
        self.token_entry.pack(pady=5)

        # Кнопки
        button_frame = Frame(self)  # Создаём контейнер для кнопок
        button_frame.pack(fill="x", pady=10)

        self.create_hash_button = Button(
            button_frame,
            text='Создать данные',
            state='disabled',  # Кнопка создания хэша не активна
            command=self._create_token_and_key_file,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold")
        )
        self.create_hash_button.pack(side='right', padx=5)

        self.connect_button = Button(
            button_frame,
            text='Проверить токен',
            command=self._connect_to_server,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold")
        )
        self.connect_button.pack(side='left', padx=5)

        # Переменные путей
        self.update_folder_path = get_path(
            exists_path, # папка проекта
            'game', # папка игры
            'update_data' # папка, хранящая данные для обновления
        )


    @property
    def _get_url(self) -> str:
        return 'https://cloud-api.yandex.net/v1/disk/resources?path=/game'

    @staticmethod
    def _get_header(token) -> dict:
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'OAuth {token}'
        }


    def _check_scripts_dir(self) -> bool:
        """Проверка наличия папки с скриптами обновления в папке игры"""
        # получение текущей папки
        try:

            # проверка наличия папки game/update_data
            if check_exists_path(self.update_folder_path):
                data_list = [
                    'scrto.enc',
                    'key.enc',
                    'version.enc'
                ]
                # проверка наличия всех необходимых файлов в папке update_data
                if len(get_listdir(self.update_folder_path)) == len(data_list): # если все файлы из списка data_list есть:
                    messagebox.showwarning(
                        title='Предупреждение',
                        message=f'Все необходимые данные обновления уже есть в проекте'
                    )
                    return False
                return True

            else:
                create_folder(path_dir=self.update_folder_path) # создаём папку update_data
                return True

        except Exception as e:
            messagebox.showerror(
                title='Ошибка',
                message=f'Возникло непредвиденное исключение:\n{e}')
            return False


    def _connect_to_server(self) -> None:
        """Проверка токена и созданной папки game путем соединения с сервером"""
        # получение значений из полей
        token = self.token_entry.get().strip()

        # проверка наличия значений в полях
        if not token:
            messagebox.showwarning(
                title='Ошибка', 
                message='Необходимо ввести токен'
                )
            return

        # установление контакта с сервером
        try:
            http = PoolManager()
            response = http.request(
                method="GET",
                url=self._get_url,
                headers=self._get_header(token=token)
            )
            if response.status == 200:
                messagebox.showinfo(
                    title='Есть контакт!',
                    message=f'Соединение с сервером было успешно установлено'
                )
                # Разблокируем кнопку создания хэша
                self.create_hash_button.config(state='normal')
                return

            if response.status == 401: #не авторизован
                messagebox.showerror(
                    title='Ошибка соединения',
                    message='Не коректный токен'
                )
                return

            if response.status == 404: # папка game не найдена
                messagebox.showwarning(
                    title='Ресурс не найден',
                    message='Пожалуйста, создайте папку game в Яндекс.Диске'
                )
                return

        except Exception as e:
            messagebox.showerror(
                title='Ошибка',
                message=f'Ошибка при соединении с сервером:\n{e}'
            )
            return


    def _create_token_and_key_file(self) -> None:
        """Создание файлов токена, ключа и версии """

        token = self.token_entry.get().strip()
        key = generate_key()
        if not token or not key:
            messagebox.showwarning(
                title='Ошибка', 
                message='Необходимо ввести токен и уникальный ключ'
                )
            return
        
        # Создание файла для хэшированного токена
        scrto_path = get_path(
            self.update_folder_path,
            'scrto.enc'
        )
        try:
            with open(scrto_path, 'wb') as file:
                index = Hash.get_unique_index(key=key)
                key_hash = Hash.generate_key(index=index)
                hash_token = Hash.encrypt_token(
                    token=token,
                    key=key_hash
                )
                file.write(hash_token)
        except Exception as e:
            messagebox.showerror(
                title='Ошибка', 
                message=f'Не удалось создать и зашифровать токен\nОшибка: {e}'
                )
            return
        
        # создание файла для ключа
        key_path = get_path(
            self.update_folder_path,
            'key.enc'
        )
        try:
            with open(key_path, 'w') as file:
                file.write(key)
        except Exception as e:
            messagebox.showerror(
                title='Ошибка', 
                message=f'Не удалось создать ключ\nОшибка: {e}'
                )
            return

        # создание файла для версии
        version_path = get_path(
            self.update_folder_path,
            'version.enc'
        )
        version = '1.0'
        try:
            with open(version_path, 'w') as file:
                file.write(version)
        except Exception as e:
            messagebox.showerror(
                title='Ошибка',
                message=f'Не удалось создать файл версии\nОшибка: {e}'
            )
            return
        
        messagebox.showinfo(
                title='Успешно!', 
                message='Токен и ключ были успешно созданны'
                )
        self.root.destroy() # окно закрывается
        return

