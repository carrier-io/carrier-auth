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

import hashlib
from typing import Optional, Iterable

from flask import session


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
