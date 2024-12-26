from urllib3 import PoolManager
import os
import base64
import hashlib
from cryptography.fernet import Fernet
from tkinter import (
    Frame,
    Tk,
    Entry,
    Button,
    Label,
    messagebox
)

class Hash:
    """Класс для хэширования токена"""

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
        encrpt = cipher.encrypt(token.encode("utf-8"))
        return encrpt


class Window(Frame):
    """Класс окна обновления"""

    def __init__(self, root: Tk):

        # проверка каталогов перед запуском утилиты
        if not self._check_scripts_dir():
            root.destroy() # Утилита закрывается, если есть конфликты

        super().__init__(master=root)
        self.root = root

        # Поле для токена
        token_entry_label = Label(
            self,
            text='Введите токен API Яндекс.Диска'
        )
        self.token_entry = Entry(self)
        self.token_entry.pack()

        # Поле для уникального ключа шифрования
        key_entry_label = Label(
            self,
            text='Введите уникальный ключ для шифрования'
        )
        self.key_entry = Entry(self)
        self.key_entry.pack()

        # Кнопка для запуска процесса генерации хэша; создание файла для токена и ключа
        self.create_hash_button = Button(
            self,
            text='Сгенерировать хэш',
            state='disabled', # кнопка создания хэша не активна, пока не установится успешный контак с сервером
            command=self._create_token_and_key_file
        )
        self.create_hash_button.pack(side='right')

        # Кнопка соединения с сервером
        self.connect_button = Button(
            self,
            text='Проверить токен',
            command=self._connect_to_server
        )
        self.connect_button.pack(side='left')


    @staticmethod
    @property
    def _get_url() -> str:
        return 'https://cloud-api.yandex.net/v1/disk/resources?path=/game'

    @staticmethod
    def _get_header(token) -> dict:
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'OAuth {token}'
        }
    
    @staticmethod
    @property
    def _get_path() -> str:
        exists_dir = str(
            os.path.abspath(__file__).replace(
                os.path.basename(__file__),
                '',
                )
            )
        return os.path.join(exists_dir, '/scripts/updater_pack')


    def _check_scripts_dir(self) -> bool:
        """Проверка наличия папки с скриптами обновления в папке игры"""
        # получение текущей папки
        try:
            

            # проверка наличия папки scripts/updater_pack
            if os.path.exists(self._get_path):
                required_files = [
                    'utils.py',
                    'updater.py',
                    'scrto.py',
                    'log.py',
                ]
                scrto_list = [
                    'scrto.enc',
                    'key.enc',
                ]

                for file in os.listdir(self._get_path):
                    # если в updater_pack нет хотябы одного скрипта из списка
                    if file not in required_files:
                        messagebox.showwarning(
                            title='Предупреждение',
                            message=f'В пакете updater_pack отсутствует файл: {file}'
                                    'Пожалуйста, добавьте его в каталог и запустите утилиту снова')
                        return False
                    # если хэшированный токен уже есть в пакете updater_pack
                    if file in scrto_list:
                        messagebox.showwarning(
                            title='Предупреждение',
                            message=f'Хэшированный токен API Яндекс.Диска или ключ уже в есть системе'
                        )
                        return False

                return True

            else:
                messagebox.showerror(
                    title='Ошибка',
                    message='Не найден пакет updater_pack в папке игры game.\n'
                            'Возможно, вы запустили утилиту в не проекта игры, или пакет updater_pack отсутствует в директории game')
                return False

        except Exception as e:
            messagebox.showerror(
                title='Ошибка',
                message=f'Ошибка при получении текущей папки:\n{e}')
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
                url=self._get_url(),
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
        """Создание файлов шифрованного токена от """

        token = self.token_entry.get().strip()
        key = self.key_entry.get().strip()
        if not token or not key:
            messagebox.showwarning(
                title='Ошибка', 
                message='Необходимо ввести токен и уникальный ключ'
                )
            return
        
        # Создание файла для хэшированного токена
        scrto_path = self._get_path + '/scrto.enc'
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
        key_path = self._get_path + '/key.enc'
        try:
            with open(key_path, 'wb') as file:
                file.write(key)
        except Exception as e:
            messagebox.showerror(
                title='Ошибка', 
                message=f'Не удалось создать ключ\nОшибка: {e}'
                )
            return
        
        messagebox.showinfo(
                title='Успешно!', 
                message='Токен и ключ были успешно созданны'
                )
        return


if __name__ == '__main__':
    root = Tk()
    win = Window(root)
    root.mainloop()