from fastapi import APIRouter, Request, Response, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

import helpers
import qr
import dependencies


router = APIRouter(
    prefix="/invite",
    tags=["invite", "webauthn"],
)

@router.get("/qr/{key}", responses = {200: {"content": {"image/png": {}}}}, response_class=Response)
async def invite_qr(
            request: Request, 
            key: str, 
            store=Depends(dependencies.get_store)):
    if store.load(f"invite_{key}") is None:
        raise HTTPException(status_code=404, detail="invitation does not exists")
    try:
        _qr = qr.Qr("https", request.headers.get('host'),'/auth/register')
        return Response(content=_qr.create(key), media_type="image/png")
    except Exception as error:
        print(error)
    raise HTTPException(status_code=500, detail="something went wrong")

@router.get("/{key}")
async def invite(
            request: Request,
            key: str,
            store=Depends(dependencies.get_store),
            templates: Jinja2Templates = Depends(dependencies.get_templates)):
    if store.load(f"invite_{key}") is None:
        raise HTTPException(status_code=404, detail="invitation does not exists")
    return templates.TemplateResponse("invite.html",
        {"request": request,
         "key": key})


@router.get('/')
async def invite_home(
            store=Depends(dependencies.get_store)):
    if store.count():
        raise HTTPException(status_code=403, detail="not allowed")
    try:
        key = helpers.generate_random_password()
        store.save(f"invite_{key}", {'user': 'admin', 'permissions': ['webauthn']})
        return RedirectResponse(url=f"/auth/invite/{key}", status_code=303)
    except Exception as error:
        print(error)
    raise HTTPException(status_code=500, detail="something went wrong")
        
__all__ = ['router']