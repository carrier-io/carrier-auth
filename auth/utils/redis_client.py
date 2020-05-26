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
from typing import Optional

import redis

from auth.config import Config


class RedisClient:
    DEFAULT_VALUE = "1"
    DEFAULT_TTL = 60 * 10

    def __init__(self):
        self._rc = redis.Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            db=Config.REDIS_DB,
            password=Config.REDIS_PASSWORD,
            username=Config.REDIS_USER
        )

    def check_auth_token(self, auth_header: str) -> bool:
        key_hex = hashlib.sha256(auth_header.encode()).hexdigest()
        return self._rc.exists(key_hex)

    def get_auth_token(self, auth_header: str) -> Optional[str]:
        key_hex = hashlib.sha256(auth_header.encode()).hexdigest()
        return self._rc.get(name=key_hex)

    def clear_auth_token(self, auth_header: str) -> Optional[str]:
        key_hex = hashlib.sha256(auth_header.encode()).hexdigest()
        return self._rc.delete(key_hex)

    def set_auth_token(self, auth_header: str, value: Optional[str] = None, ttl: Optional[int] = None) -> None:
        """
        ``ttl`` sets an expire flag on key for ``ttl`` seconds.
        """
        key_hex = hashlib.sha256(auth_header.encode()).hexdigest()
        if value is None:
            value = self.DEFAULT_VALUE
        if ttl is None:
            ttl = self.DEFAULT_TTL
        return self._rc.set(name=key_hex, value=value, ex=ttl)
