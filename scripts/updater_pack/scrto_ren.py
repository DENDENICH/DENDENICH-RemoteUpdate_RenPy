import hashlib
import base64
from cryptography.fernet import Fernet

from .log import logger



def get_scrto(path: str) -> str | None:

    try:
        index = hashlib.sha256('scarlet_snowScRt0'.encode()).hexdigest()
        key = hashlib.sha256(index.encode()).digest()[:32]

        cipher = Fernet(base64.urlsafe_b64encode(key))
        with open(path, "rb") as f:
            encrp = f.read()
        decrp = cipher.decrypt(encrp).decode("utf-8")
        return decrp

    except Exception as e:
        logger.error(msg=f"Error get and decode scrto: \n\t{e}")
        return None
    

__all__ = ['get_scrto']
