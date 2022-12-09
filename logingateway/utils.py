import base64
import datetime
import hashlib

__all__ = ("encodeToken",)

PAGE_LIMIT = 10

def encodeToken(clientId: str, clientSecret: str):
    ts = datetime.datetime.now().timestamp()
    hash = hashlib.sha512(
        f"clientId={clientId}|clientSecret={clientSecret}|ts={ts}".encode()).hexdigest()

    return base64.b64encode(f"{clientId}:{hash}:{ts}".encode()).decode()

def createOffsetPage(page: int = 1):
    return page * PAGE_LIMIT, PAGE_LIMIT