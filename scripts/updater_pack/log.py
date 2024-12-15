import sys
import logging
from logging import Logger


def create_logger(
    file_path: str = "debug_update.log"
    ) -> Logger:
    """Функция создания логера для вывода отладки процесса обновления"""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s #%(levelname)-8s %(filename)s: %(lineno)d - %(funcName)s | %(message)s |",
        handlers=[
            logging.FileHandler(file_path),
            logging.StreamHandler(sys.stdout)
        ]
    )

    return logging.getLogger('main_logger')

logger = create_logger()

__all__ = ['logger']
