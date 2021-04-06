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


from typing import Optional, Any, Callable, Union, List

import requests
from flask_restful import Api, Resource
from pydantic import BaseModel
from requests import Response

from plugins.auth_manager.models.api_response_pd import ApiResponse, is_subclass_of_base_model
from plugins.auth_manager.models.token_pd import AuthCreds, Token, RefreshCreds
from plugins.auth_manager.utils.exceptions import TokenRefreshError, IdExtractError


def add_resource_to_api(api: Api, resource: Resource, *urls, **kwargs) -> None:
    # This /api/v1 thing is made here to be able to register auth endpoints for local development
    urls = (*(f"/forward-auth/api/v1{url}" for url in urls), *(f"/forward-auth/api/v1{url}/" for url in urls))
    api.add_resource(resource, *urls, **kwargs)


def get_token(url: str, creds: AuthCreds) -> Token:
    response = requests.post(url, data=creds.dict())
    token = Token.parse_obj(response.json())
    return token


def refresh_token(url: str, creds: RefreshCreds) -> Token:
    response = requests.post(url, data=creds.dict())
    if not response.ok:
        raise TokenRefreshError(response.json())
    token = Token.parse_obj(response.json())
    return token


def api_response(
        response: Response,
        response_data_type: Union[Callable, BaseModel, List, None] = None,
        response_debug_processor: Optional[Callable] = None
) -> ApiResponse:
    resp = ApiResponse()
    data = resp.get_data_from_response(response)
    resp.debug = resp.get_debug_data(response, response_debug_processor)

    if response.ok:
        resp.data = data
    else:
        resp.error.message = data
        resp.error.error_code = response.status_code

    resp.success = response.ok
    resp.status = response.status_code
    return api_data_response(data=resp, response_data_type=response_data_type)


def api_data_response(
        data: Any,
        status: int = 200,
        response_data_type: Union[Callable, BaseModel, List, None] = None
) -> ApiResponse:
    if isinstance(data, ApiResponse):
        resp = data
    else:
        resp = ApiResponse()
        resp.status = status
        resp.success = 200 <= status < 300
        resp.data = data

    if resp.success and response_data_type:
        try:
            resp.data = resp.format_response_data(resp.data, response_data_type)
        except Exception as e:
            resp.debug['response_data_type_error'] = str(e)
    return resp


def get_id(obj: Any, possible_id_attribute_name='id', raise_on_error=True):
    print(f'{obj=}')
    print(f'{isinstance(obj, BaseModel)=}')
    # print(f'{issubclass(obj, BaseModel)=}')
    print(f'{issubclass(type(obj), BaseModel)=}')
    print(f'{is_subclass_of_base_model(obj)=}')

    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        return obj.get(possible_id_attribute_name)
    if is_subclass_of_base_model(obj):
        try:
            return obj.__getattribute__(possible_id_attribute_name)
        except AttributeError:
            if raise_on_error:
                raise IdExtractError(obj, possible_id_attribute_name)
    if raise_on_error:
        raise IdExtractError(obj, possible_id_attribute_name)
    return None
