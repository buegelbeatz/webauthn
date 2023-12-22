import os
from tools import generate_random_password

COOKIE_NAME = 'webauthn'
SECRET = generate_random_password()
DATA_DIR = os.environ['DATA'] if 'DATA' in os.environ.keys() else './.data'
if 'SECRET' in os.environ.keys():
    SECRET = os.environ['SECRET']
else:
    print(f"generate a random secret: {SECRET}")

__all__ = ['COOKIE_NAME', 'SECRET', 'DATA_DIR']