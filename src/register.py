from typing import Any
import json
from fastapi import APIRouter, Request, Response, HTTPException, Depends, Body
from fastapi.templating import Jinja2Templates
import webauthn
from webauthn.helpers.structs import PublicKeyCredentialDescriptor

import dependencies
from helpers import set_session, set_authorization, get_verification_dictionary, get_nice_string, get_existing_credentials


router = APIRouter(
    prefix="/register",
    tags=["register","auth","webauthn"],
)


@router.post('/finalize')
async def register_finalize(
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
            'permissions': user_data['permissions'] if user_data and user_data['permissions'] else []
        }
        store.save(f"credential_{credential['id']}",_data)
        set_authorization(response, credential['user'], credential['id'])
        if session and session['rd']:
            _result['redirect'] = session['rd']
        if credential['user'] == 'admin':
            _result['admin'] = 1
        _result['verified'] = 1
    except Exception as error:
        print(error)
    store.remove(user_key)
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
        store.save(f"user_{invitation['user']}", invitation)
        print('users', store.search('user'))
        _credentials =[PublicKeyCredentialDescriptor(id=id) for id in get_existing_credentials(store.search('credential'))]
        print('_credentials', _credentials)
        return webauthn.options_to_json(webauthn.generate_registration_options(
            rp_id=host,
            rp_name=host,
            exclude_credentials=_credentials,
            user_id=invitation['user'], 
            user_name=invitation['user']))

    except Exception as error:
        print(error)
    raise HTTPException(status_code=500, detail="registration challenge failed")


@router.get("/{key}")
async def register(
            request: Request,
            key: str = '',
            rd: str = '',
            templates: Jinja2Templates = Depends(dependencies.get_templates)):
    return templates.TemplateResponse("register.html",{"rd":rd,"request": request, "key": key})

__all__ = ['router']