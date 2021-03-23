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
import os
from functools import cached_property
from os import environ
from typing import Optional

import redis
import yaml
from pylon.core.tools.config import config_substitution, vault_secrets


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SettingsFileNotFoundError(Exception):
    MESSAGE = 'Settings file path is invalid. Check "CONFIG_FILENAME" env. Current is: {}'

    def __init__(self, detail: Optional[str] = ''):
        super(SettingsFileNotFoundError, self).__init__(self.MESSAGE.format(detail))


class Config(metaclass=Singleton):
    """Set Flask configuration vars from .env file."""

    # General Config
    # APP_HOST = "0.0.0.0"
    # APP_PORT = "80"
    CONFIG_FILENAME = environ.get("CONFIG_FILENAME", None)
    # AUTH_PROXIES = []  # registered in module init
    # SECRET_KEY = b"_5#y2L\"F4Q8z\n\xec]/"
    # SESSION_COOKIE_NAME = "auth"

    # # Redis client
    # REDIS_USER = environ.get("REDIS_USER", "")
    # REDIS_PASSWORD = environ.get("REDIS_PASSWORD", "password")
    # REDIS_HOST = environ.get("REDIS_HOST", "localhost")
    # REDIS_PORT = int(environ.get("REDIS_PORT", 6379))
    # REDIS_DB = int(environ.get("REDIS_DB", 3))
    #
    # # Flask-Session
    # SESSION_TYPE = environ.get("SESSION_TYPE", "redis")
    # SESSION_REDIS = redis.from_url(
    #     environ.get("SESSION_REDIS", f"redis://{REDIS_USER}:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")
    # )

    # SETTINGS = dict()
    #
    # def __init__(self):
    #     try:
    #         settings_data = open(self.CONFIG_FILENAME, "rb").read()
    #     except (TypeError, FileNotFoundError):
    #         # current_app.logger.error("Settings file path not set. Please set CONFIG_FILENAME")
    #         raise SettingsFileNotFoundError(str(self.CONFIG_FILENAME))
    #
    #     settings = yaml.load(os.path.expandvars(settings_data), Loader=yaml.SafeLoader)
    #     self.SETTINGS = config_substitution(settings, vault_secrets(settings))

    @cached_property
    def SETTINGS(self):
        try:
            settings_data = open(self.CONFIG_FILENAME, "rb").read()
        except (TypeError, FileNotFoundError):
            # current_app.logger.error("Settings file path not set. Please set CONFIG_FILENAME")
            raise SettingsFileNotFoundError(str(self.CONFIG_FILENAME))

        settings = yaml.load(os.path.expandvars(settings_data), Loader=yaml.SafeLoader)
        return config_substitution(settings, vault_secrets(settings))

# x = Config
# print(x.AUTH_PROXIES)
# try:
#     y = Config().settings
# except SettingsFileNotFoundError as e:
#     print(e)
#     print(str(e))
#     print(repr(e))
# print(x.AUTH_PROXIES)
# print(y.AUTH_PROXIES)
# Config.AUTH_PROXIES.append('123')
# print()
# print(x.AUTH_PROXIES)
# print(y.AUTH_PROXIES)
# print()
# z = Config
# z.AUTH_PROXIES.append('qwe')
# print()
# print(x.AUTH_PROXIES)
# print(y.AUTH_PROXIES)
# print(z.AUTH_PROXIES)
# print()
# print(x.settings)
# print(y.settings)
# print(z.settings)
# print(z().settings)
