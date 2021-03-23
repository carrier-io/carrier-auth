import json
from base64 import b64decode

from flask import make_response

from plugins.auth_base.utils.token_manager import set_auth_token
from plugins.auth_oidc.app import _validate_basic_auth, _validate_token_auth


def basic(auth_value):
    KEY_NAME = 'basic'
    username, password = b64decode(auth_value.strip()).decode().split(":", 1)
    is_ok, auth_data = _validate_basic_auth(username, password)
    if is_ok:
        set_auth_token(auth_header=f'{KEY_NAME} {auth_value}', value=json.dumps(auth_data))
        return make_response("OK", 200)
    return make_response("KO", 401)


def bearer(auth_value):
    KEY_NAME = 'bearer'
    is_ok, auth_data = _validate_token_auth(auth_value)
    if is_ok:
        set_auth_token(auth_header=f'{KEY_NAME} {auth_value}', value=json.dumps(auth_data))
        return make_response("OK", 200)
    return make_response("KO", 401)
