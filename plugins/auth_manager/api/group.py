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


from typing import Optional

from flask import request, make_response

from requests import Response

from plugins.auth_manager.api.base import BaseResource
from plugins.auth_manager.models.group_pd import GroupRepresentation
from plugins.auth_manager.rpc import get_groups, put_entity, post_group, delete_entity


class GroupAPI(BaseResource):
    @BaseResource.check_token
    def get(self, realm: str, group_id: Optional[str] = None, **kwargs) -> Response:
        response = get_groups(
            base_url=self.settings['keycloak_urls']['group'],
            realm=realm,
            token=self.token,
            group_or_id=group_id,
            search=request.args.get('search'),
            **kwargs
        )
        return make_response(response.dict(), response.status)

    @BaseResource.check_token
    def put(self, realm: str, group_id: str, **kwargs) -> Response:
        group = GroupRepresentation.parse_obj(request.json)
        group.id = group_id

        # todo: if not debug remove response_debug_processor
        if 'response_debug_processor' not in kwargs:
            kwargs['response_debug_processor'] = lambda r: {
                'status_code': r.status_code,
                'updating_fields': group.dict(exclude_unset=True)
            }
        response = put_entity(
            base_url=self.settings['keycloak_urls']['group'],
            realm=realm,
            token=self.token,
            entity=group,
            **kwargs
        )
        return make_response(response.dict(), response.status)

    @BaseResource.check_token
    def post(self, realm: str, **kwargs) -> Response:
        group = GroupRepresentation.parse_obj(request.json)
        response = post_group(
            base_url=self.settings['keycloak_urls']['group'],
            realm=realm,
            token=self.token,
            group=group,
            **kwargs
        )
        return make_response(response.dict(), response.status)


    @BaseResource.check_token
    def delete(self, realm: str, group_id: str, **kwargs) -> Response:
        response = delete_entity(
            base_url=self.settings['keycloak_urls']['group'],
            realm=realm,
            token=self.token,
            entity_or_id=group_id,
            **kwargs
        )
        return make_response(response.dict(), response.status)
