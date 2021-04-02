#     Copyright 2020 getcarrier.io
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.


from functools import wraps
from flask import session
from flask_restful import Resource

from pylon.core.tools import log

from plugins.auth_manager.models.token_pd import Token, AuthCreds, RefreshCreds
from plugins.auth_manager.utils.exceptions import TokenExpiredError, TokenRefreshError
from plugins.auth_manager.utils.tools import get_token, refresh_token


class BaseResource(Resource):
    _settings: dict = {}

    @classmethod
    def set_settings(cls, auth_settings: dict):
        BaseResource._settings = auth_settings

    @classmethod
    def get_settings(cls):
        if not BaseResource._settings:
            print('settings from context')
            from flask import current_app
            BaseResource.set_settings(current_app.config["CONTEXT"].auth_settings)
        return BaseResource._settings

    @property
    def settings(self) -> dict:
        return BaseResource.get_settings()

    @settings.setter
    def settings(self, value: dict) -> None:
        BaseResource.set_settings(value)

    @property
    def token(self) -> Token:
        token = session.get('api_token')
        if not token:
            creds = AuthCreds(
                username=self.settings['manager']['username'],
                password=self.settings['manager']['password']
            )
            token = get_token(
                self.settings['manager']['token_url'],
                creds
            )
            session['api_token'] = token
            # session['api_token'] = str(token)
            # session['api_refresh_token'] = token.refresh_token
        return token

    @staticmethod
    def check_token(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                try:
                    data = result.json()
                except TypeError:
                    data = result.json
                if not data['success']:
                    if data.get('error', {}).get('error_code') == 401:
                        raise TokenExpiredError
                return result
            except TokenExpiredError:
                log.warning('Token expired, trying to refresh')
                refresh_creds = RefreshCreds(refresh_token=session['api_token'].refresh_token)
                try:
                    new_token = refresh_token(url=BaseResource._settings['manager']['token_url'], creds=refresh_creds)
                except TokenRefreshError as e:
                    return func(*args, **kwargs, response_debug_processor=lambda r: {'TokenRefreshError': e.message})

                session['api_token'] = new_token
                # session['api_token'] = str(new_token)
                # session['api_refresh_token'] = new_token.refresh_token
                if 'token' in kwargs:
                    kwargs.update(token=new_token)
                return func(*args, **kwargs, response_debug_processor=lambda r: 'Token refreshed')

        return wrapper
