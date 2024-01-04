import os
import string
import random


COOKIE_NAME = 'webauthn'
SECRET = ''.join(random.choice(string.ascii_letters) for _ in range(8))
DATA_DIR = os.environ['DATA'] if 'DATA' in os.environ.keys() else './.data'
if 'SECRET' in os.environ.keys():
    SECRET = os.environ['SECRET']
else:
    print(f"generate a random secret: {SECRET}")

__all__ = ['COOKIE_NAME', 'SECRET', 'DATA_DIR']