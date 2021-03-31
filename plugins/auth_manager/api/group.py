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


from typing import Optional, Union, Callable

import requests
from flask import request
from pydantic import ValidationError

from requests import Response

from plugins.auth_manager.api.base import BaseResource, api_response, ApiResponseError, api_data_response
from plugins.auth_manager.api.user import UserAPI
from plugins.auth_manager.models.group_pd import GroupRepresentation
from plugins.auth_manager.utils import Token, ApiError


class GroupAPI(BaseResource):
    # @staticmethod
    # def _get(url: str, token: Union[str, Token], realm: str = '',
    #                response_debug_processor: Optional[Callable] = None, **kwargs) -> Response:
    #     url = url.format(realm=realm)
    #     headers = {'Authorization': str(token)}
    #     response = requests.get(url, headers=headers, params=kwargs)
    #     return api_response(response, debug_processor=response_debug_processor)

    @BaseResource.check_token
    def get(self, realm: str, group_id: Optional[str] = None) -> Response:
        url = self.settings['manager']['group_url']
        if group_id:
            url = f'{url}/{group_id}'
        search_kwarg = dict()
        if request.args.get('search'):
            search_kwarg['search'] = request.args['search']
        return UserAPI._get(
            url=url,
            token=self.token,
            realm=realm,
            **search_kwarg
        )

    # @staticmethod
    # def _put(url: str, token: Union[str, Token], body: GroupRepresentation, realm: str = '',
    #                response_debug_processor: Optional[Callable] = None) -> Response:
    #     url = url.format(realm=realm)
    #     headers = {'Authorization': str(token), 'Content-Type': 'application/json'}
    #     response = requests.put(url, headers=headers, json=body.dict(exclude_unset=True))
    #     if not response_debug_processor:
    #         response_debug_processor = lambda r: {
    #             'status_code': r.status_code,
    #             'updating_fields': body.dict(exclude_unset=True)
    #         }
    #     return api_response(response, debug_processor=response_debug_processor)

    @BaseResource.check_token
    def put(self, realm: str, group_id: str) -> Response:
        url = f"{self.settings['manager']['group_url']}/{group_id}"
        try:
            group = GroupRepresentation.parse_obj(request.json)
        except ValidationError as e:
            error = ApiResponseError()
            error.message = str(e)
            return api_data_response(error=error)
        return UserAPI._put(
            url=url,
            token=self.token,
            realm=realm,
            body=group
        )

    @staticmethod
    def _post(url: str, token: Union[str, Token], body: GroupRepresentation, realm: str = '',
                    response_debug_processor: Optional[Callable] = None) -> Response:
        if not body.name:
            raise ApiError('Body must contain a name')
        url = url.format(realm=realm)
        headers = {'Authorization': str(token), 'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, json=body.dict(exclude_unset=True))
        if not response_debug_processor:
            response_debug_processor = lambda r: {
                'status_code': r.status_code,
                'group_body': body.dict(exclude_unset=True)
            }
        return api_response(response, debug_processor=response_debug_processor)

    @BaseResource.check_token
    def post(self, realm: str) -> Response:
        url = self.settings['manager']['group_url']
        try:
            group = GroupRepresentation.parse_obj(request.json)
        except ValidationError as e:
            error = ApiResponseError()
            error.message = str(e)
            return api_data_response(error=error)
        try:
            return self._post(
                url=url,
                token=self.token,
                realm=realm,
                body=group
            )
        except ApiError as e:
            error = ApiResponseError()
            error.message = str(e)
            return api_data_response(error=error)

    # @staticmethod
    # def _delete(url: str, token: Union[str, Token], realm: str = '',
    #                   response_debug_processor: Optional[Callable] = None) -> Response:
    #     url = url.format(realm=realm)
    #     headers = {'Authorization': str(token)}
    #     response = requests.delete(url, headers=headers)
    #     if not response_debug_processor:
    #         response_debug_processor = lambda r: {'status_code': r.status_code}
    #     return api_response(response, debug_processor=response_debug_processor)

    @BaseResource.check_token
    def delete(self, realm: str, group_id: str) -> Response:
        url = f"{self.settings['manager']['group_url']}/{group_id}"
        return UserAPI._delete(
            url=url,
            token=self.token,
            realm=realm,
        )


class SubgroupAPI(BaseResource):
    @staticmethod
    def _post_subgroup(url: str, token: Union[str, Token], body: GroupRepresentation, realm: str = '',
                       response_debug_processor: Optional[Callable] = None) -> Response:
        url = url.format(realm=realm)
        headers = {'Authorization': str(token), 'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, json=body.dict(exclude_unset=True))
        if not response_debug_processor:
            response_debug_processor = lambda r: {
                'status_code': r.status_code,
                'updating_fields': body.dict(exclude_unset=True)
            }
        return api_response(response, debug_processor=response_debug_processor)

    @BaseResource.check_token
    def post(self, realm: str, group_id: str) -> Response:
        url = f"{self.settings['manager']['group_url']}/{group_id}/children"
        try:
            group = GroupRepresentation.parse_obj(request.json)
        except ValidationError as e:
            error = ApiResponseError()
            error.message = str(e)
            return api_data_response(error=error)
        return self._post_subgroup(
            url=url,
            token=self.token,
            realm=realm,
            body=group
        )


class GroupMemberAPI(BaseResource):
    @BaseResource.check_token
    def get(self, realm: str, group_id: Optional[str] = None) -> Response:
        url = f"{self.settings['manager']['group_url']}/{group_id}/members"
        return UserAPI._get(
            url=url,
            token=self.token,
            realm=realm,
            **request.args
        )