'''In this module the authorization for a specific subdomain is tested'''

import re
from fastapi import APIRouter, Request, Response, HTTPException, Depends

import dependencies

router = APIRouter(
    prefix="/authorize",
    tags=["authorize", "webauthn"],
)


@router.get("/{path:path}")
async def authorize(
            response: Response,
            request: Request,
            user_payload=Depends(dependencies.get_user)):
    '''Check if the Bearer token or the cookie have the right setup: permission is part of domain and user exists'''
    try:
        _domain = re.sub(r"^https://([^/])+.*$",r"\1",request.headers.get('referer'))
        _user = user_payload['user']
        _permissions = user_payload['permissions']
        print(_domain,_user,_permissions)
        for permission in _permissions:
            if _domain.startswith(permission):
                response.headers['X-User'] = _user
                return 'ok'
    except Exception: # pylint: disable=W0718
        pass
    raise HTTPException(status_code=401, detail="Access is not allowed")

__all__ = ['router']
