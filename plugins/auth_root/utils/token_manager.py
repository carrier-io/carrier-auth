#   Copyright 2020
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
import binascii
import hashlib
from queue import Empty
from typing import Optional, Iterable

from flask import session, Response, make_response
from pylon.core.tools import log
from pylon.core.tools.rpc import RpcManager


def encode_header(auth_header):
    return hashlib.sha256(auth_header.encode()).hexdigest()


def get_auth_token(keys: Optional[Iterable] = ('name', 'value',)) -> dict:
    return {k: v for k, v in session.items() if k in keys}


def check_auth_token(auth_header) -> bool:
    return bool(get_auth_token() == encode_header(auth_header))


def clear_auth_token() -> None:
    session.clear()


def set_auth_token(auth_header: str, value: Optional[str] = '') -> None:
    session['name'] = encode_header(auth_header)
    session['value'] = encode_header(value)


def check_auth(auth_header: str, *, rpc_prefix: str, rpc_timeout: int, rpc_manager: RpcManager) -> Response:
    try:
        auth_key, auth_value = auth_header.strip().split(" ")
    except ValueError:
        return make_response("KO", 401)
    if check_auth_token(auth_header=auth_header):
        return make_response("OK", 200)
    try:
        auth_result = rpc_manager.call_function_with_timeout(
            func='{prefix}{key}'.format(
                prefix=rpc_prefix,
                key=auth_key.lower()
            ),
            timeout=rpc_timeout,
            auth_value=auth_value
        )
    except Empty:
        log.error(f'Cannot find handler for auth_key {auth_key.lower()}')
        return make_response("KO", 401)
    except binascii.Error:
        log.error('Incorrect auth data received')
        return make_response('KO', 403)
    return make_response(*auth_result)

