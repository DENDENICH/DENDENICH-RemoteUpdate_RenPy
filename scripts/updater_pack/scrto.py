import hashlib
import base64
from cryptography.fernet import Fernet


def get_scrto(
        path: str,
        key: str
) -> str | None:

    index = hashlib.sha256(key.encode()).hexdigest()
    key = hashlib.sha256(index.encode()).digest()[:32]

    cipher = Fernet(base64.urlsafe_b64encode(key))
    with open(path, "rb") as f:
        encrp = f.read()
    decrp = cipher.decrypt(encrp).decode("utf-8")
    return decrp


__all__ = ['get_scrto']
