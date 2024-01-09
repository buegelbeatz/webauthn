'''This module is only required if the redirect mechanism somehow does not work.'''

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

import dependencies

router = APIRouter(
    prefix="/done",
    tags=["done", "webauthn"],
)

@router.get("/{path:path}")
async def done(
    request: Request,
    user=Depends(dependencies.get_user),
    templates: Jinja2Templates = Depends(dependencies.get_templates)):
    print(f"user '{user['user']}' done!")
    return templates.TemplateResponse("done.html",{"request": request})

__all__ = ['router']
