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

from os import environ

import redis


class Config:
    """Set Flask configuration vars from .env file."""

    # General Config
    APP_HOST = "0.0.0.0"
    APP_PORT = "80"
    CONFIG_FILENAME = environ.get("CONFIG_FILENAME", None)
    AUTH_PROXIES = ("oidc", "root")
    SECRET_KEY = b"_5#y2L\"F4Q8z\n\xec]/"
    SESSION_COOKIE_NAME = "auth"

    # Redis client
    REDIS_USER = environ.get("REDIS_USER", "")
    REDIS_PASSWORD = environ.get("REDIS_PASSWORD", "password")
    REDIS_HOST = environ.get("REDIS_HOST", "localhost")
    REDIS_PORT = int(environ.get("REDIS_PORT", 6379))
    REDIS_DB = int(environ.get("REDIS_DB", 3))

    # Flask-Session
    SESSION_TYPE = environ.get("SESSION_TYPE", "redis")
    SESSION_REDIS = redis.from_url(
        environ.get("SESSION_REDIS", f"redis://{REDIS_USER}:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")
    )
