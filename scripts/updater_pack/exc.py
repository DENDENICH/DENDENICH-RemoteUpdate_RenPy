from log import logger

class RemoteException(Exception):
    def __init__(self, message: str):
        self.message = message

    @property
    def user_message(self):
        return f'Message: {self.message}'

    def __str__(self):
        logger.error(
            msg=f'{self.__class__.__name__}: {self.message}'
        )
        return self.user_message


class PathException(RemoteException):
    pass


class NetException(RemoteException):
    def __init__(
            self,
            message: str,
            code: int
    ):
        super().__init__(message=message)
        self.code = code

    @property
    def user_message(self):
        return f'Code: {self.code}\nMessage: {self.message}'


class OtherException(RemoteException):
    pass


__all__ = [
    'PathException',
    'NetException',
    'OtherException'
]
