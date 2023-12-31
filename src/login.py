from typing import Any
import json
from fastapi import APIRouter, Request, Response, HTTPException, Depends, Body
# from starlette.responses import FileResponse
from fastapi.templating import Jinja2Templates
import webauthn
from webauthn.helpers.structs import PublicKeyCredentialDescriptor

import environment
import dependencies
from helpers import set_authorization, get_verification_dictionary, get_encoded_from_b64_decoded, get_existing_credentials


router = APIRouter(
    prefix="/login",
    tags=["login","auth","webauthn"],
)


@router.post('/finalize')
async def login_finalize(
        request: Request,
        response: Response, 
        payload: Any = Body(None),
        store=Depends(dependencies.get_store), 
        session=Depends(dependencies.get_session)):
    _result = {'verified': 0}
    try:
        print('payload', payload)
        credential = payload['credential']
        saved_credential = store.load(f"credential_{credential['id']}")
        print('saved_credential', saved_credential)
        webauthn.verify_authentication_response(
            **get_verification_dictionary(credential),
            credential_public_key=get_encoded_from_b64_decoded(saved_credential['public_key']),
            credential_current_sign_count=0,
            require_user_verification=True
        )
        set_authorization(request, response, saved_credential['user'], credential['id'])
        if session and session['rd']:
            _result['redirect'] = session['rd']
        if saved_credential['user'] == 'admin':
            _result['admin'] = 1
        _result['verified'] = 1
    except Exception as error: # pylint: disable=W0718
        print(error)
        response.delete_cookie(key=environment.COOKIE_NAME)
    return json.dumps(_result)


@router.post("/challenge")
async def login_challenge(
        request: Request, 
        store=Depends(dependencies.get_store)):
    try:
        _credentials = [PublicKeyCredentialDescriptor(id=id) for id in get_existing_credentials(store.search('credential'))]
        print(_credentials)
        _challenge = webauthn.options_to_json(webauthn.generate_authentication_options(
            rp_id=request.headers.get('host'),
            user_verification='required',
            allow_credentials=_credentials))
        print('_challenge', _challenge)
        return _challenge
    except Exception as error: # pylint: disable=W0718
        print(error)
    raise HTTPException(status_code=500, detail="login challenge failed")


@router.get("/")
async def login(
            request: Request,
            rd: str = '',
            templates: Jinja2Templates = Depends(dependencies.get_templates)):
    return templates.TemplateResponse("login.html",{"rd":rd,"request": request})


__all__ = ['router']