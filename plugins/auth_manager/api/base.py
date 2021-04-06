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
from typing import Callable

from flask import session, request
from flask_restful import Resource, abort

from pylon.core.tools import log
from pylon.core.tools.rpc import RpcManager

from plugins.auth_manager.models.api_response_pd import ApiResponse
from plugins.auth_manager.models.token_pd import Token, AuthCreds, RefreshCreds
from plugins.auth_manager.utils.exceptions import TokenExpiredError, TokenRefreshError
from plugins.auth_manager.utils.tools import get_token, refresh_token


class BaseResource(Resource):
    _settings: dict = {}
    _rpc_manager: RpcManager = None

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

    @classmethod
    def set_rpc_manager(cls, rpc_manager: RpcManager):
        BaseResource._rpc_manager = rpc_manager

    @classmethod
    def get_rpc_manager(cls):
        if not BaseResource._rpc_manager:
            print('rpc_manager from context')
            from flask import current_app
            BaseResource.set_settings(current_app.config["CONTEXT"].rpc_manager)
        return BaseResource._rpc_manager

    @property
    def rpc_manager(self) -> RpcManager:
        return BaseResource.get_rpc_manager()

    @rpc_manager.setter
    def rpc_manager(self, value: RpcManager) -> None:
        BaseResource.set_rpc_manager(value)

    def get_token(self):
        creds = AuthCreds(
            username=self.settings['manager']['username'],
            password=self.settings['manager']['password']
        )
        token = get_token(
            self.settings['manager']['token_url'],
            creds
        )
        return token

    @property
    def token(self) -> Token:
        if not self.check_authorized():
            abort(401)
        token = session.get('api_token')
        if not token:
            token = self.get_token()
            session['api_token'] = token
        return token

    @staticmethod
    def check_authorized() -> bool:
        if "Authorization" in request.headers:
            check_result = BaseResource._rpc_manager.call_function(
                func='{prefix}check_auth'.format(prefix=BaseResource._settings['rpc_manager']['prefix']),
                auth_header=request.headers.get("Authorization", "")
            )
            return check_result.status_code == 200
        return False

    @staticmethod
    def check_token(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                try:
                    print(f'check_token try {type(result)=} {result=}')
                    data = result.json()
                except TypeError:
                    print(f'check_token TypeError {type(result)=} {result=}')
                    data = result.json
                if not data['success']:
                    if data.get('error', {}).get('error_code') == 401:
                        raise TokenExpiredError
                return result
            except TokenExpiredError:
                log.warning('Token expired, trying to refresh')
                debug_message = 'Token refreshed'
                refresh_creds = RefreshCreds(refresh_token=session['api_token'].refresh_token)
                try:
                    session['api_token'] = refresh_token(url=BaseResource._settings['manager']['token_url'], creds=refresh_creds)
                    if 'token' in kwargs:
                        kwargs.update(token=session['api_token'])
                except TokenRefreshError as e:
                    # return func(*args, **kwargs, response_debug_processor=lambda r: {'TokenRefreshError': e.message})
                    session['api_token'] = BaseResource().get_token()
                    debug_message = 'Token refresh failed, got new token'
                return func(*args, **kwargs, response_debug_processor=lambda r: debug_message)
        return wrapper
