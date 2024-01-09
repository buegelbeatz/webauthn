from typing import Any
import json
import urllib.parse
from fastapi import APIRouter, Request, Response, HTTPException, Depends, Body
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import webauthn
from webauthn.helpers.structs import PublicKeyCredentialDescriptor

import dependencies
from helpers import set_authorization, get_verification_dictionary, get_nice_string, get_existing_credentials


router = APIRouter(
    prefix="/register",
    tags=["register","auth","webauthn"],
)


@router.post('/finalize')
async def register_finalize(
        request: Request,
        response: Response, 
        payload: Any = Body(None),
        store=Depends(dependencies.get_store), 
        session=Depends(dependencies.get_session)):
    _result = {'verified': 0}
    user_key = None
    try:
        print('payload', payload)
        credential = payload['credential']
        verification_result = webauthn.verify_registration_response(**get_verification_dictionary(credential))
        user_key = f"user_{credential['user']}"
        user_data = store.load(user_key)
        _data = {
            'public_key': get_nice_string(verification_result.credential_public_key), 
            'user': credential['user'],
            'user_agent': user_data['user_agent'],
            'permissions': user_data['permissions'] if user_data and user_data['permissions'] else []
        }
        store.save(f"credential_{credential['id']}",_data)
        set_authorization(request,response, credential['user'], credential['id'])
        if session and session['rd']:
            _result['redirect'] = session['rd']
        if credential['user'] == 'admin':
            _result['admin'] = 1
        _result['verified'] = 1
    except Exception as error: # pylint: disable=W0718
        print(error)
    store.remove(user_key)
    print(_result)
    return json.dumps(_result)


@router.post("/challenge")
async def register_challenge(
        request: Request,
        payload: Any = Body(None),
        store=Depends(dependencies.get_store)):
    print('payload',payload)
    if not payload or not payload['id']:
        raise HTTPException(status_code=404, detail="invitation does not exists")
    try:
        invitation = store.load(f"invite_{payload['id']}")
        host = request.headers.get("host")
        store.remove(f"invite_{payload['id']}")
        invitation['user_agent'] = request.headers.get("user-agent")
        store.save(f"user_{invitation['user']}", invitation)
        _credentials =[PublicKeyCredentialDescriptor(id=id) for id in get_existing_credentials(store.search('credential'))]
        return webauthn.options_to_json(webauthn.generate_registration_options(
            rp_id=host,
            rp_name=host,
            exclude_credentials=_credentials,
            user_id=invitation['user'], 
            user_name=invitation['user']))

    except Exception as error: # pylint: disable=W0718
        print(error)
    raise HTTPException(status_code=500, detail="registration challenge failed")


@router.get("/{key}")
async def register(
            request: Request,
            key: str = '',
            rd: str = '',
            store=Depends(dependencies.get_store),
            templates: Jinja2Templates = Depends(dependencies.get_templates)):
    invitation = store.load(f"invite_{key}")
    if invitation is None: 
        raise HTTPException(status_code=401, detail="no invitation available")
    credentials = store.search('credential')
    user_agent = request.headers.get('user-agent')
    redirect = "" if rd == "" else f"?{urllib.parse.urlencode({'rd': rd})}"
    for credential in credentials:
        if credential['user'] == invitation['user'] and 'user_agent' in credential and credential['user_agent'] == user_agent:
            store.remove(f"invite_{key}")
            return RedirectResponse(url=f"/auth/login/{redirect}", status_code=303)
    return templates.TemplateResponse("register.html",{"rd":rd,"request": request, "key": key})


__all__ = ['router']
