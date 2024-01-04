from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
# from starlette.responses import FileResponse
import re
import urllib.parse

import dependencies
import helpers
import environment

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)


def _mailto(request: Request, permission):
       user = permission['user']
       parameters = {"Subject": f"Invitation for '{','.join(permission['permissions'])}'", 
                     "body": f"https://{request.headers.get('host')}/auth/invite/{permission['id']}"}
       return f"mailto:{user}?{urllib.parse.urlencode(parameters).replace('+', '%20')}"

def _src(request: Request, permission):
       return f"https://{request.headers.get('host')}/auth/invite/qr/{permission['id']}"

@router.get("/")
async def admin(
            request: Request,
            is_admin=Depends(dependencies.get_admin_bool),
            store=Depends(dependencies.get_store),
            templates: Jinja2Templates = Depends(dependencies.get_templates)):
    if is_admin:
        data = store.search()
        permissions = [{**permission, "mailto":_mailto(request, permission), "src":_src(request, permission)} for permission in data]
        print(permissions)
        return templates.TemplateResponse("admin.html",
        {"request": request, "permissions": permissions})
    else:
        return RedirectResponse(url="/auth/login?rd=%2Fauth%2Fadmin", status_code=303)

@router.post('/add')
async def admin_add(
            store=Depends(dependencies.get_store),
            _=Depends(dependencies.get_admin),
            user=Form(),
            permissions=Form()):
    if user == 'admin' or re.match(r"^.*webauthn.*$",permissions):
        raise HTTPException(status_code=406, detail="could not give 'webauthn' parmissions or use user 'admin' here")
    email_regexp = re.compile(r'^\s*([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+\s*$')
    permissions_regexp = re.compile(r'^\s*([a-z][a-z\d\-]+)([\s,;]+[a-z][a-z\d\-]+)*\s*$')
    if not re.match(email_regexp,user) or not re.match(permissions_regexp,permissions):
        raise HTTPException(status_code=406, detail="user needs to be an email and permission need to be a lower case list divided by ' ', ',' or ';'")
    key = helpers.generate_random_password()
    store.save(f"invite_{key}", {'user': user.strip(), 'permissions': re.split(r"[\s,;]+", permissions.strip())})
    return RedirectResponse(url="/auth/admin", status_code=303)

@router.post('/delete')
async def admin_delete(
                store=Depends(dependencies.get_store),
                _=Depends(dependencies.get_admin), 
                id=Form(),
                type=Form(),
                user=Form()):
    payload = store.load(f"{type}_{id}")
    if payload and payload['user'] and payload['user'] == user and user != 'admin':
        store.remove(f"{type}_{id}")
    return RedirectResponse(url="/auth/admin", status_code=303)


__all__ = ['router']