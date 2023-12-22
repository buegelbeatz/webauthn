from fastapi import  Response
import jwt

import environment


def set_session(response: Response, payload):
    token = jwt.encode(payload, f"{environment.SECRET}_session", algorithm="HS256").decode()
    response.set_cookie(key=f"{environment.COOKIE_NAME}_session", value=token)

def set_authorization(response: Response, user_name, credential_id):
    token = jwt.encode({"id": credential_id, "user": user_name}, environment.SECRET, algorithm="HS256").decode()
    response.set_cookie(key=environment.COOKIE_NAME, value=token)
    response.headers['X-User'] = user_name
    response.headers['Bearer'] = token

__all__ = ['set_session', 'set_authorization']
