import logging

from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
# from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.templating import Jinja2Templates

# from starlette.responses import FileResponse

# import register
# import login
import invite
import dependencies
# import admin
# import test

import auth

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


# app.include_router(register.router)
app.include_router(auth.login.router)
app.include_router(invite.router)
# app.include_router(admin.router)
# app.include_router(test.router)

# @app.get("/webauthn.js")
# async def webauthn_js():
#     return FileResponse('webauthn.js')