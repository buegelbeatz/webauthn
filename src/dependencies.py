"""All required Dependencies are managed in this module."""

from fastapi import  Request, HTTPException
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

def get_user_str(request: Request) -> str:
    try:
        token = None
        authorization = request.headers.get('authorization')
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
        if not token:
            token = request.cookies.get(environment.COOKIE_NAME)
        if token:
            payload = jwt.decode(token.encode(), environment.SECRET, algorithms=["HS256"])
        return payload['user']
    except Exception:
        pass
    return ''


def get_admin_bool(request: Request) -> bool:
    _user = get_user_str(request)
    if _user != 'admin':
        return False
    return True


def get_user(request: Request) -> str:
    _user = get_user_str(request)
    if not _user:
        raise HTTPException(status_code=401, detail="you need to authenticate", headers={"WWW-Authenticate": "Bearer"}) 
    return _user


def get_admin(request: Request) -> bool:
    if not get_admin_bool(request):
        raise HTTPException(status_code=403, detail="access is only allowed for admin")
    return True

__all__ = ['get_store', 'get_session', 'get_templates', 'get_user_str', 'get_admin_bool', 'get_user', 'get_admin']
