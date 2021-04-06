from typing import List, Union

from flask import Response, request, make_response
from pydantic import BaseModel

from plugins.auth_manager.api.base import BaseResource
from plugins.auth_manager.models.group_pd import GroupRepresentation
from plugins.auth_manager.models.user_pd import UserRepresentation
from plugins.auth_manager.rpc import add_users_to_groups, expel_users_from_groups


class Membership(BaseModel):
    users: List[Union[UserRepresentation, str]]
    groups: List[Union[GroupRepresentation, str]]


class MembershipAPI(BaseResource):
    @BaseResource.check_token
    def put(self, realm: str, **kwargs) -> Response:
        data = Membership.parse_obj(request.json)
        response = add_users_to_groups(
            user_url=self.settings['manager']['user_url'],
            realm=realm,
            token=self.token,
            users=data.users,
            groups=data.groups,
            **kwargs
        )
        return make_response(response.dict(), response.status)

    # delete cannot have json payload
    @BaseResource.check_token
    def post(self, realm: str, **kwargs) -> Response:
        data = Membership.parse_obj(request.json)
        response = expel_users_from_groups(
            user_url=self.settings['manager']['user_url'],
            realm=realm,
            token=self.token,
            users=data.users,
            groups=data.groups,
            **kwargs
        )
        return make_response(response.dict(), response.status)
