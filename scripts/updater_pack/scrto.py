import hashlib
import base64
from cryptography.fernet import Fernet

from .exc import PathException, OtherException



def get_scrto(
        path: str,
        key: str
) -> str | None:

    try:
        index = hashlib.sha256(key.encode()).hexdigest()
        key = hashlib.sha256(index.encode()).digest()[:32]

        cipher = Fernet(base64.urlsafe_b64encode(key))
        with open(path, "rb") as f:
            encrp = f.read()
        decrp = cipher.decrypt(encrp).decode("utf-8")
        return decrp

    except FileNotFoundError:
        raise PathException(
            message='file scrto.enc not found in the updater_pack/ directory'
        )

    except Exception as e:
        raise OtherException(
            message=f'Error operation with scrto: \n\t{e}'
        )
    

__all__ = ['get_scrto']
