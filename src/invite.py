import urllib.parse
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
            settings=Depends(dependencies.get_settings),
            store=Depends(dependencies.get_store)):
    if store.load(f"invite_{key}") is None:
        raise HTTPException(status_code=404, detail="invitation does not exists")
    try:
        payload = store.load(f"invite_{key}")
        redirect = ""
        if len(payload['permissions']):
            for permission in settings['permissions']:
                if payload['permissions'][0] == permission['key']:
                    redirect = f"?{urllib.parse.urlencode({'rd':permission['url']})}"
                    break
        _qr = qr.Qr("https", request.headers.get('host'),f"/auth/register/{key}{redirect}")
        return Response(content=_qr.create(), media_type="image/png")
    except Exception as error: # pylint: disable=W0718
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
        return RedirectResponse(url="/auth/admin", status_code=303)
    try:
        key = helpers.generate_random_password()
        pin = helpers.generate_random_pin()
        # TODO: pin is not used at the moment, this should be some additional security wall for initialize
        # print()
        # print("ATTENTION: THIS PIN IS REQUIRED FOR ACTIVATING ADMIN PERMISSIONS!")
        # print("########")
        # print(f"# {pin} #")
        # print("########")
        # print()
        store.save(f"invite_{key}", {'user': 'admin', 'permissions': ['webauthn'], 'pin': pin})
        return RedirectResponse(url=f"/auth/invite/{key}", status_code=303)
    except Exception as error: # pylint: disable=W0718
        print(error)
    raise HTTPException(status_code=500, detail="something went wrong")

__all__ = ['router']
