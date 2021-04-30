from typing import Union
from flask import request, make_response
from requests import Response

from plugins.auth_manager.rpc import add_subgroup
from pydantic import BaseModel

from plugins.auth_manager.models.group_pd import GroupRepresentation
from plugins.auth_manager.api.base import BaseResource


class SubGroup(BaseModel):
    parent: Union[GroupRepresentation, str]
    child: Union[GroupRepresentation, str]


class SubgroupAPI(BaseResource):
    @BaseResource.check_token
    def post(self, realm: str, **kwargs) -> Response:
        relationship = SubGroup.parse_obj(request.json)
        print('RELATION', relationship)
        response = add_subgroup(
            group_url=self.settings['keycloak_urls']['group'],
            realm=realm,
            token=self.token,
            parent=relationship.parent,
            child=relationship.child,
            **kwargs
        )

        return make_response(response.dict(), response.status)
