import logging

from fastapi import FastAPI, Request, APIRouter
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.templating import Jinja2Templates

import invite
import admin
import login
import register
# import test

# import auth
import dependencies

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.getLevelName(logging.DEBUG))

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.exception_handler(StarletteHTTPException)
async def custom_exception_handler(
        request: Request,
        exc: StarletteHTTPException):
    status_code = exc.status_code
    detail = exc.detail
    # logger.debug(dir(templates))
    return templates.TemplateResponse("error.html", 
        {"request": request,
         "detail": detail,
         "status_code": status_code})

app.mount("/static", StaticFiles(directory="static"), name="static")

router = APIRouter(
    prefix="/auth",
    tags=["register","login","admin","invite", "webauthn"],
)

router.include_router(invite.router)
router.include_router(admin.router)
router.include_router(register.router)
router.include_router(login.router)

app.include_router(router)
