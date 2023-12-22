import random
import string
import re
import json
from base64 import urlsafe_b64encode, urlsafe_b64decode
from fastapi import Request #, Response
# import jwt


def generate_random_password():
    return ''.join(random.choice(string.ascii_letters) for _ in range(8))

# def get_nice_string(value):
#     return re.sub("=+$","", urlsafe_b64encode(value).rstrip(b'=').decode('utf-8'))

# def get_client_data_json(value):
#     return json.loads(urlsafe_b64decode(value).decode('utf-8'))

# def get_b64_decoded(value):
#     return urlsafe_b64decode(value + "==")

# def get_encoded_from_b64_decoded(value):
#     return urlsafe_b64decode("".join([value,"=="]).encode())

# def get_verification_dictionary(credential):
#     client_data_json = get_client_data_json(credential['response']['clientDataJSON'])
#     return {
#         'credential' : credential,
#         'expected_challenge': get_b64_decoded(client_data_json['challenge']),
#         'expected_rp_id': re.sub(r"^https?:\/\/([^\/]+).*$", r'\1', client_data_json['origin']),
#         'expected_origin': client_data_json['origin']
#     }

# def get_existing_credentials(entries):
#     return [get_encoded_from_b64_decoded(entry['id']) for entry in entries if entry['type'] == 'credential']

# # TODO: Is this really still required?
# async def get_data(request: Request):
#     if "application/json" in request.headers.get("Content-Type", ""):
#         try:
#             _raw_data = await request.body()
#             _data = json.loads(_raw_data.decode())
#             print("Received JSON payload:", _data)
#             return _data
#         except Exception:
#             pass
#     return False

# __all__ = ['generate_random_password', 'get_nice_string', 'get_client_data_json', 'get_b64_decoded', 'get_data', 'get_verification_dictionary', 'get_existing_credentials']

__all__ = ['generate_random_password']