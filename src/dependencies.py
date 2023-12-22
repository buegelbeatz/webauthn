"""All required Dependencies are managed in this module."""

from fastapi import  Request
from fastapi.templating import Jinja2Templates
import jwt

import environment
from store import Store

#TODO: https://stackoverflow.com/questions/51291722/define-a-jsonable-type-using-mypy-pep-526
def get_session(request: Request):
    try:
        token = request.cookies.get(f"{environment.COOKIE_NAME}_session")
        if token:
            payload = jwt.decode(token.encode(), f"{environment.SECRET}_session", algorithms=["HS256"])
        return payload
    except Exception:
        pass
    return None


def get_store() -> Store:
    """Giving back a store singleton as an dependency"""
    return Store(environment.DATA_DIR)

def get_templates() -> Jinja2Templates:
    return Jinja2Templates(directory="templates")

__all__ = ['get_store', 'get_session', 'get_templates']
