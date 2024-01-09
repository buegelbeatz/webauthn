"""All required Dependencies are managed in this module."""

from fastapi import  Request, HTTPException
from fastapi.templating import Jinja2Templates
import jwt
import os
import yaml

import environment
from store import Store

#TODO: https://stackoverflow.com/questions/51291722/define-a-jsonable-type-using-mypy-pep-526
def get_session(request: Request):
    try:
        token = request.cookies.get(f"{environment.COOKIE_NAME}_session")
        if token:
            payload = jwt.decode(token.encode(), f"{environment.SECRET}_session", algorithms=["HS256"])
        return payload
    except Exception: # pylint: disable=W0718
        pass
    return None


def get_store() -> Store:
    """Giving back a store singleton as an dependency"""
    return Store(environment.DATA_DIR)

def get_templates() -> Jinja2Templates:
    return Jinja2Templates(directory="templates")

def get_user_payload(request: Request):
    try:
        token = None
        authorization = request.headers.get('authorization')
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
        if not token:
            token = request.cookies.get(environment.COOKIE_NAME)
        if token:
            payload = jwt.decode(token.encode(), environment.SECRET, algorithms=["HS256"])
        return payload
    except Exception: # pylint: disable=W0718
        pass
    return ''


def get_settings():
    path = ""
    settings = None
    try:
        if os.path.exists(f"{environment.DATA_DIR}/settings.yaml"):
            path = f"{environment.DATA_DIR}/settings.yaml"
        if os.path.exists("/settings.yaml"):
            path = f"{environment.DATA_DIR}/settings.yaml"
        if path:
            with open(path, 'r', encoding='utf-8') as file:
                settings = yaml.safe_load(file)
    except Exception: # pylint: disable=W0718
        print(f"""
####################################################################
MISSING settings.yaml file! Please mount this to '/settings.yaml' 
if you are in kubernetes context or copy it over to your 
'{environment.DATA}' folder. Should look like:

users:
  - john.doe@example.com
  - mario.rossi@example.it
  - heinz.mustermann@example.de
permissions:
  - key: test1
    url: https://test1.example.org
  - key: test2
    url: https://test2.example.org
    
####################################################################
""")
        raise HTTPException(status_code=503, detail="If you are admin please check the server side console output!")
    return settings


def get_admin_bool(request: Request) -> bool:
    _payload = get_user_payload(request)
    if _payload and _payload['user'] != 'admin':
        return False
    return True


def get_user(request: Request):
    _payload = get_user_payload(request)
    if not _payload or _payload['user'] == '':
        raise HTTPException(status_code=401, detail="you need to authenticate", headers={"WWW-Authenticate": "Bearer"}) 
    return _payload


def get_admin(request: Request) -> bool:
    if not get_admin_bool(request):
        raise HTTPException(status_code=403, detail="access is only allowed for admin")
    return True

__all__ = ['get_store', 'get_session', 'get_templates', 'get_user_payload', 'get_admin_bool', 'get_user', 'get_admin', 'get_settings']
