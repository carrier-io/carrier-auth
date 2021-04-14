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
            base_url=self.settings['keycloak_urls']['user'],
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
            base_url=self.settings['keycloak_urls']['user'],
            realm=realm,
            token=self.token,
            entity=user,
            **kwargs
        )
        return make_response(response.dict(), response.status)

    @BaseResource.check_token
    def post(self, realm: str, **kwargs) -> Response:
        user = UserRepresentation.parse_obj(request.json)
        response = post_entity(
            base_url=self.settings['keycloak_urls']['user'],
            realm=realm,
            token=self.token,
            entity=user,
            **kwargs
        )
        return make_response(response.dict(), response.status)

    @BaseResource.check_token
    def delete(self, realm: str, user_id: str, **kwargs) -> Response:
        response = delete_entity(
            base_url=self.settings['keycloak_urls']['user'],
            realm=realm,
            token=self.token,
            entity_or_id=user_id,
            **kwargs
        )
        return make_response(response.dict(), response.status)
