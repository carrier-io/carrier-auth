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


from typing import Union, Optional, Callable

import requests
from pydantic import BaseModel

from plugins.auth_manager.models.api_response_pd import ApiResponse, DebugProcessorType
from plugins.auth_manager.models.group_pd import GroupRepresentation
from plugins.auth_manager.models.token_pd import Token
from plugins.auth_manager.models.user_pd import UserRepresentation
from plugins.auth_manager.utils.tools import api_response, get_id


class KeyCloakAPI:
    @staticmethod
    def get(
            url: str,
            token: Union[str, Token],
            response_data_type: Union[Callable, BaseModel] = None,
            response_debug_processor: DebugProcessorType = None,
            **kwargs
    ) -> ApiResponse:
        headers = {'Authorization': str(token)}
        response = requests.get(url, headers=headers, params=kwargs)
        return api_response(
            response, response_debug_processor=response_debug_processor, response_data_type=response_data_type)

    @staticmethod
    def put(
            url: str,
            token: Union[str, Token],
            body: Union[UserRepresentation, GroupRepresentation],
            response_debug_processor: DebugProcessorType = None
    ) -> ApiResponse:
        headers = {'Authorization': str(token), 'Content-Type': 'application/json'}
        response = requests.put(url, headers=headers, json=body.dict(exclude_unset=True))
        return api_response(response, response_debug_processor=response_debug_processor)

    @staticmethod
    def post(
            url: str,
            token: Union[str, Token],
            body: Union[UserRepresentation, GroupRepresentation],
            response_debug_processor: DebugProcessorType = None
    ) -> ApiResponse:
        headers = {'Authorization': str(token), 'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, json=body.dict(exclude_unset=True))
        return api_response(response, response_debug_processor=response_debug_processor)

    @staticmethod
    def delete(
            url: str,
            token: Union[str, Token],
            response_debug_processor: DebugProcessorType = None
    ) -> ApiResponse:
        headers = {'Authorization': str(token)}
        response = requests.delete(url, headers=headers)
        return api_response(response, response_debug_processor=response_debug_processor)

    @staticmethod
    def get_user_groups(
            user_url: str,
            token: Union[str, Token],
            response_debug_processor: DebugProcessorType = None
    ) -> ApiResponse:
        groups_url = f'{user_url.rstrip("/")}/groups'
        return KeyCloakAPI.get(
            url=groups_url,
            token=token,
            response_data_type=GroupRepresentation,
            response_debug_processor=response_debug_processor
        )

    @staticmethod
    def get_group_members(
            group_url: str,
            token: Union[str, Token],
            response_debug_processor: DebugProcessorType = None
    ) -> ApiResponse:
        members_url = f'{group_url.rstrip("/")}/members'
        return KeyCloakAPI.get(
            url=members_url,
            token=token,
            response_data_type=UserRepresentation,
            response_debug_processor=response_debug_processor
        )

    @staticmethod
    def add_user_to_group(
            user_url: str,
            token: Union[str, Token],
            user: Union[UserRepresentation, str],
            group: Union[GroupRepresentation, str],
            response_debug_processor: DebugProcessorType = None
    ) -> ApiResponse:
        user_id = get_id(user)
        group_id = get_id(group)
        url = f'{user_url.rstrip("/")}/{user_id}/groups/{group_id}'
        headers = {'Authorization': str(token)}
        response = requests.put(url, headers=headers)
        return api_response(response, response_debug_processor=response_debug_processor)

    @staticmethod
    def expel_user_from_group(
            user_url: str,
            token: Union[str, Token],
            user: Union[UserRepresentation, str],
            group: Union[GroupRepresentation, str],
            response_debug_processor: DebugProcessorType = None
    ) -> ApiResponse:
        user_id = get_id(user)
        group_id = get_id(group)
        url = f'{user_url.rstrip("/")}/{user_id}/groups/{group_id}'
        headers = {'Authorization': str(token)}
        response = requests.delete(url, headers=headers)
        return api_response(response, response_debug_processor=response_debug_processor)

    @staticmethod
    def add_subgroup_to_group(
            group_url: str,
            token: Union[str, Token],
            parent: Union[GroupRepresentation, str],
            child: GroupRepresentation,
            response_debug_processor: DebugProcessorType = None
    ) -> ApiResponse:
        parent_id = get_id(parent)
        url = f'{group_url.rstrip("/")}/{parent_id}/children'
        headers = {'Authorization': str(token), 'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, json=child.dict(exclude_unset=True))
        return api_response(response, response_debug_processor=response_debug_processor)
