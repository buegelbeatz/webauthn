import random
import string
from fastapi import  Response, Request
import jwt
import re
import json
from base64 import urlsafe_b64encode, urlsafe_b64decode

import environment

# TODO: Rename
def get_nice_string(value):
    return re.sub("=+$","", urlsafe_b64encode(value).rstrip(b'=').decode('utf-8'))

def get_client_data_json(value):
    return json.loads(urlsafe_b64decode(value).decode('utf-8'))

def get_b64_decoded(value):
    return urlsafe_b64decode(value + "==")

def get_encoded_from_b64_decoded(value):
    return urlsafe_b64decode("".join([value,"=="]).encode())

def get_verification_dictionary(credential):
    client_data_json = get_client_data_json(credential['response']['clientDataJSON'])
    print('client_data_json', client_data_json)
    return {
        'credential' : credential,
        'expected_challenge': get_b64_decoded(client_data_json['challenge']),
        'expected_rp_id': re.sub(r"^https?:\/\/([^\/]+).*$", r'\1', client_data_json['origin']),
        'expected_origin': client_data_json['origin']
    }

def get_existing_credentials(credentials):
    return [get_encoded_from_b64_decoded(credential['id']) for credential in credentials]

def generate_random_password():
    return ''.join(random.choice(string.ascii_letters) for _ in range(8))

def generate_random_pin():
    random_pin = random.randint(0, 9999)
    formatted_pin = f'{random_pin:04}'
    return formatted_pin

def _set_cookie(request: Request, response: Response, key, value):
    _domain = re.sub(r"^.*(\.[^\.]+\.[^\.]+)$",r"\1",request.headers.get('host'))
    response.set_cookie(key=key, value=value, domain=_domain, secure=True, httponly=True, samesite='none')

def set_session(request: Request, response: Response, payload):
    token = jwt.encode(payload, f"{environment.SECRET}_session", algorithm="HS256")
    _set_cookie(request, response, f"{environment.COOKIE_NAME}_session", token)

# TODO: Maybe more nice to bring all the authorization stuff together 
def set_authorization(request: Request,response: Response, user_name, credential_id):
    token = jwt.encode({"id": credential_id, "user": user_name}, environment.SECRET, algorithm="HS256")
    _set_cookie(request, response, f"{environment.COOKIE_NAME}", token)
    response.headers['X-User'] = user_name
    response.headers['Bearer'] = token

__all__ = ['set_session',
           'set_authorization',
           'generate_random_pin',
           'generate_random_password',
           'get_nice_string',
           'get_client_data_json',
           'get_b64_decoded',
           'get_encoded_from_b64_decoded',
           'get_verification_dictionary',
           'get_existing_credentials']
