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
from json import JSONDecodeError
from typing import Optional, Any, Callable
from flask import make_response, session
from flask_restful import Resource

from pydantic import BaseModel
from pylon.core.tools import log
from requests import Response

from plugins.auth_manager.utils import AuthCreds, get_token, RefreshCreds, refresh_token, TokenExpiredError, Token, \
    TokenRefreshError


class ApiResponseError(BaseModel):
    message: Any = None
    error_code: Optional[int] = None
    error_description: Optional[str] = None


class ApiResponse(BaseModel):
    status: int = 200
    success: bool = True
    error: Optional[ApiResponseError] = ApiResponseError()
    data: Any = {}
    debug: Any = {}


def api_response(response: Response, debug_processor: Optional[Callable] = None):
    print(f'{response=}')
    debug_data = None
    if debug_processor:
        try:
            debug_data = debug_processor(response)
        except Exception as e:
            debug_data = {'processor_failed': str(e)}
    try:
        data = response.json()
    except JSONDecodeError:
        data = response.text
    if response.ok:
        return api_data_response(data=data, debug=debug_data)
    else:
        error_data = ApiResponseError(
            error_code=response.status_code,
            message=data
        )
        return api_data_response(error=error_data, debug=debug_data)


def api_data_response(data: Any = {}, error: Optional[ApiResponseError] = ApiResponseError(), debug: Any = {}):
    resp = ApiResponse()
    if data:
        resp.data = data
    if error.dict(exclude_unset=True):
        resp.success = False
        resp.error = error
    if debug:
        resp.debug = debug

    return make_response(resp.dict(exclude_none=True), resp.status)


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
        print(f'check token {func=}')

        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f'check token wrapper {func=} {args=} {kwargs=}')
            try:
                result = func(*args, **kwargs)
                print(f'{result=} {type(result)=}')
                try:
                    data = result.json()
                except TypeError:
                    data = result.json
                print(f'{data=} {type(data)=}')
                print(f"{data['success']=} {type(data['success'])=}")
                if not data['success']:
                    if data['error'].get('error_code') == 401:
                        raise TokenExpiredError
                return result
            except TokenExpiredError:
                log.warning('Token expired, trying to refresh')
                # refresh_creds = RefreshCreds(refresh_token=session['api_refresh_token'])
                print(f'{session["api_token"]=}')
                refresh_creds = RefreshCreds(refresh_token=session['api_token'].refresh_token)
                # print(f'{args=} {kwargs=}')
                try:
                    new_token = refresh_token(url=BaseResource._settings['manager']['token_url'], creds=refresh_creds)
                except TokenRefreshError as e:
                    error = ApiResponseError(
                        error_description='Token Refresh Error',
                        message=e.message,
                    )
                    return api_data_response(error=error)

                session['api_token'] = new_token
                # session['api_token'] = str(new_token)
                # session['api_refresh_token'] = new_token.refresh_token
                if 'token' in kwargs:
                    kwargs.update(token=new_token)
                return func(*args, **kwargs)

        return wrapper
