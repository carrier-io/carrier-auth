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

from typing import Optional

import redis

from auth.constants import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD, REDIS_USER


class RedisClient:

    DEFAULT_TTL = 60 * 30

    def __init__(self):
        self._rc = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD,
            username=REDIS_USER
        )

    def check_basic_auth_token(self, login: str, password: str, scope: str) -> bool:
        key = f"{login}::{password}::{scope}"
        return self._rc.exists(key)

    def get_basic_auth_token(self, login: str, password: str, scope: str) -> Optional[str]:
        key = f"{login}::{password}::{scope}"
        return self._rc.get(name=key)

    def set_basic_auth_token(
            self, login: str, password: str, scope: str, value: str, ttl: Optional[int] = None
    ) -> None:
        """
        ``ttl`` sets an expire flag on key for ``ttl`` seconds.
        """
        key = f"{login}::{password}::{scope}"
        if ttl is None:
            ttl = self.DEFAULT_TTL
        return self._rc.set(name=key, value=value, ex=ttl)

    def check_auth_token(self, refresh_token: str, scope: str) -> bool:
        key = f"{refresh_token}::{scope}"
        return self._rc.exists(key)

    def get_auth_token(self, refresh_token: str, scope: str) -> Optional[str]:
        key = f"{refresh_token}::{scope}"
        return self._rc.get(name=key)

    def set_auth_token(
            self, refresh_token: str, scope: str, value: str, ttl: Optional[int] = None
    ) -> None:
        """
        ``ttl`` sets an expire flag on key for ``ttl`` seconds.
        """
        key = f"{refresh_token}::{scope}"
        if ttl is None:
            ttl = self.DEFAULT_TTL
        return self._rc.set(name=key, value=value, ex=ttl)
