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
from flask import request, make_response

from requests import Response

from plugins.auth_manager.api.base import BaseResource
from plugins.auth_manager.models.token_pd import Token
from plugins.auth_manager.models.user_pd import UserRepresentation
from plugins.auth_manager.rpc import get_users, put_entity, post_entity, delete_entity
from plugins.auth_manager.utils.tools import api_response


class UserAPI(BaseResource):
    @BaseResource.check_token
    def get(self, realm: str, user_id: Optional[str] = None, **kwargs) -> Response:
        response = get_users(
            base_url=self.settings['manager']['user_url'],
            realm=realm,
            token=self.token,
            user_or_id=user_id,
            **request.args,
            **kwargs
        )
        # todo: if not debug: return make_response(response.dict(exclude={'debug'}), response.status)
        return make_response(response.dict(), response.status)

    @BaseResource.check_token
    def put(self, realm: str, user_id: str, **kwargs) -> Response:
        user = UserRepresentation.parse_obj(request.json)
        user.id = user_id

        # todo: if not debug remove response_debug_processor
        if 'response_debug_processor' not in kwargs:
            kwargs['response_debug_processor'] = lambda r: {
                'status_code': r.status_code,
                'updating_fields': user.dict(exclude_unset=True)
            }
        response = put_entity(
            base_url=self.settings['manager']['user_url'],
            realm=realm,
            token=self.token,
            entity=user,
            **kwargs
        )
        print(f'def put {response.dict()}')
        return make_response(response.dict(), response.status)

    @BaseResource.check_token
    def post(self, realm: str, **kwargs) -> Response:
        user = UserRepresentation.parse_obj(request.json)
        response = post_entity(
            base_url=self.settings['manager']['user_url'],
            realm=realm,
            token=self.token,
            entity=user,
            **kwargs
        )
        print(f'def post {response.dict()}')
        return make_response(response.dict(), response.status)

    @BaseResource.check_token
    def delete(self, realm: str, user_id: str, **kwargs) -> Response:
        response = delete_entity(
            base_url=self.settings['manager']['user_url'],
            realm=realm,
            token=self.token,
            entity_or_id=user_id,
            **kwargs
        )
        print(f'def delete {response.dict()}')
        return make_response(response.dict(), response.status)


# class UsergroupsAPI(BaseResource):
    # @BaseResource.check_token
    # def get(self, realm: str, user_id: str) -> Response:
    #     url = self.settings['manager']['user_url']
    #     if user_id:
    #         url = f'{url}/{user_id}/groups'
    #     return UserAPI._get(
    #         url=url,
    #         token=self.token,
    #         realm=realm,
    #         **request.args
    #     )

    # @staticmethod
    # def _add_user_to_group(url: str, token: Union[str, Token], realm: str = '',
    #          response_debug_processor: Optional[Callable] = None) -> Response:
    #     url = url.format(realm=realm)
    #     headers = {'Authorization': str(token)}
    #     response = requests.put(url, headers=headers)
    #     return api_response(response, response_debug_processor=response_debug_processor)

    # @BaseResource.check_token
    # def put(self, realm: str, user_id: str, group_id: str) -> Response:
    #     url = f"{self.settings['manager']['user_url']}/{user_id}/groups/{group_id}"
    #     return self._add_user_to_group(
    #         url=url,
    #         token=self.token,
    #         realm=realm,
    #     )
    #
    # @staticmethod
    # def _remove_user_from_group(url: str, token: Union[str, Token], realm: str = '',
    #                        response_debug_processor: Optional[Callable] = None) -> Response:
    #     url = url.format(realm=realm)
    #     headers = {'Authorization': str(token)}
    #     response = requests.delete(url, headers=headers)
    #     return api_response(response, response_debug_processor=response_debug_processor)
    #
    # @BaseResource.check_token
    # def delete(self, realm: str, user_id: str, group_id: str) -> Response:
    #     url = f"{self.settings['manager']['user_url']}/{user_id}/groups/{group_id}"
    #     return self._remove_user_from_group(
    #         url=url,
    #         token=self.token,
    #         realm=realm,
    #     )