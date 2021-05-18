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


from typing import Optional, Union, List

from plugins.auth_manager.models.api_response_pd import ApiResponse, is_subclass_of_base_model, DebugProcessorType
from plugins.auth_manager.models.group_pd import GroupRepresentation
from plugins.auth_manager.models.token_pd import Token
from plugins.auth_manager.models.user_pd import UserRepresentation
from plugins.auth_manager.utils.keycloak_api import KeyCloakAPI
from plugins.auth_manager.utils.tools import get_id, get_id_from_headers, api_data_response


# !!!base_url is included in rpc, but can be overridden!!!


# rpc_name: auth_manager_get_user
def get_users(
        *, base_url: str, realm: str, token: Token,
        user_or_id: Optional[Union[str, UserRepresentation]] = None,
        response_debug_processor: DebugProcessorType = None,
        with_groups: bool = True,
        **kwargs
) -> ApiResponse:
    url = base_url.format(realm=realm)
    user_id = get_id(user_or_id, raise_on_error=False)
    if user_id:
        url = f'{url.rstrip("/")}/{user_id}'
        if with_groups:
            user_data = KeyCloakAPI.get(
                url=url,
                token=token,
                realm=realm,
                response_debug_processor=response_debug_processor,
                response_data_type=UserRepresentation,
                **kwargs
            )
            if user_data.success:
                groups_data = KeyCloakAPI.get_user_groups(user_url=url, token=token)
                if isinstance(user_data.data, dict):
                    user_data.data['groups'] = groups_data.data
                else:
                    user_data.data.groups = groups_data.data
            return user_data
    return KeyCloakAPI.get(
        url=url,
        token=token,
        realm=realm,
        response_debug_processor=response_debug_processor,
        response_data_type=UserRepresentation,
        **kwargs
    )


# rpc_name: auth_manager_get_group
def get_groups(
        *, base_url: str, realm: str, token: Token,
        group_or_id: Optional[Union[str, GroupRepresentation]] = None,
        search: Optional[str] = None,
        response_debug_processor: DebugProcessorType = None,
        with_members: bool = True
) -> ApiResponse:
    search_kwarg = dict()
    url = base_url.format(realm=realm)
    group_id = get_id(group_or_id, raise_on_error=False)
    if group_id:
        url = f'{url.rstrip("/")}/{group_id}'
        if with_members:
            group_data = KeyCloakAPI.get(
                url=url,
                token=token,
                realm=realm,
                response_debug_processor=response_debug_processor,
                response_data_type=GroupRepresentation,
            )
            if group_data.success:
                members_data = KeyCloakAPI.get_group_members(group_url=url, token=token)
                if isinstance(group_data.data, dict):
                    group_data.data['members'] = members_data.data
                else:
                    group_data.data.members = members_data.data
            return group_data
    elif search:
        search_kwarg['search'] = search

    return KeyCloakAPI.get(
        url=url,
        token=token,
        realm=realm,
        response_debug_processor=response_debug_processor,
        response_data_type=GroupRepresentation,
        **search_kwarg
    )


# rpc_name: auth_manager_put_entity
def put_entity(
        *, base_url: str, realm: str, token: Token, entity: Union[UserRepresentation, GroupRepresentation],
        response_debug_processor: DebugProcessorType = None,

) -> ApiResponse:
    entity_id = get_id(entity)
    url = base_url.format(realm=realm)
    url = f'{url.rstrip("/")}/{entity_id}'
    return KeyCloakAPI.put(
        url=url,
        token=token,
        body=entity,
        response_debug_processor=response_debug_processor
    )


# rpc_name: auth_manager_post_user
def post_entity(
        *, base_url: str, realm: str, token: Token, entity: Union[UserRepresentation, GroupRepresentation],
        response_debug_processor: DebugProcessorType = None
) -> ApiResponse:
    url = base_url.format(realm=realm)
    api_response = KeyCloakAPI.post(
        url=url,
        token=token,
        body=entity,
        response_debug_processor=response_debug_processor
    )
    if api_response.success and api_response.headers and 'Location' in api_response.headers:
        created_entity_id = get_id_from_headers(
            location_header_value=api_response.headers.get('Location', '')
        )
        if isinstance(api_response.data, dict):
            api_response.data['id'] = created_entity_id
            api_response = api_data_response(data=api_response, response_data_type=type(entity))
        if not api_response.data:
            entity.id = created_entity_id
            api_response.data = entity
    return api_response



# rpc_name: auth_manager_post_group
def post_group(
        group: GroupRepresentation,
        *args, **kwargs
) -> ApiResponse:
    if not group.name:
        return ApiResponse.failed(error_message={'errorMessage': 'Group name is missing'}, status_code=400)
    return post_entity(*args, **kwargs, entity=group)


# rpc_name: auth_manager_delete_entity
def delete_entity(
        *, base_url: str, realm: str, token: Token, entity_or_id: Union[UserRepresentation, GroupRepresentation, str],
        response_debug_processor: DebugProcessorType = None
) -> ApiResponse:
    entity_id = get_id(entity_or_id)

    url = base_url.format(realm=realm)
    url = f'{url.rstrip("/")}/{entity_id}'

    return KeyCloakAPI.delete(
        url=url,
        token=token,
        response_debug_processor=response_debug_processor
    )


# rpc_name: auth_manager_add_users_to_groups
def add_users_to_groups(
        *, user_url: str, realm: str, token: Token,
        users: List[Union[UserRepresentation, str]], groups: List[Union[GroupRepresentation, str]],
        response_debug_processor: DebugProcessorType = None,
) -> ApiResponse:
    url = user_url.format(realm=realm)
    resp = ApiResponse()
    resp.data = []
    resp.error.message = []
    resp.debug = []
    for user in users:
        for group in groups:
            result = KeyCloakAPI.add_user_to_group(
                user_url=url,
                token=token,
                user=user, group=group,
                response_debug_processor=response_debug_processor
            )
            if result.success:
                resp.data.append(f'User <{user}> successfully joined group <{group}>')
            else:
                resp.success = False
                resp.status = 207
                # for token decorator
                if result.error.error_code == 401:
                    resp.error.error_code = 401
                resp.error.message.append({
                    'description': f'User <{user}> failed to join group <{group}>',
                    **result.error.dict()
                })
            if result.debug:
                resp.debug.append(result.debug)
    return resp


# rpc_name: auth_manager_expel_users_from_groups
def expel_users_from_groups(
        *, user_url: str, realm: str, token: Token,
        users: List[Union[UserRepresentation, str]], groups: List[Union[GroupRepresentation, str]],
        response_debug_processor: DebugProcessorType = None,
) -> ApiResponse:
    url = user_url.format(realm=realm)
    resp = ApiResponse()
    resp.data = []
    resp.error.message = []
    resp.debug = []
    for user in users:
        for group in groups:
            result = KeyCloakAPI.expel_user_from_group(
                user_url=url,
                token=token,
                user=user, group=group,
                response_debug_processor=response_debug_processor
            )
            if result.success:
                resp.data.append(f'User <{user}> expelled from group <{group}>')
            else:
                resp.success = False
                resp.status = 207
                # for token decorator
                if result.error.error_code == 401:
                    resp.error.error_code = 401
                resp.error.message.append({
                    'description': f'User <{user}> failed to be expelled from group <{group}>',
                    **result.error.dict()
                })
            if result.debug:
                resp.debug.append(result.debug)
    return resp


# rpc_name: auth_manager_add_subgroup
def add_subgroup(
        *, group_url: str, realm: str, token: Token,
        parent: Union[GroupRepresentation, str], child: Union[GroupRepresentation, str],
        response_debug_processor: DebugProcessorType = None
):
    parent_id = get_id(parent)
    url = f'{group_url.rstrip("/")}/{parent_id}/children'
    if isinstance(child, str):
        child = GroupRepresentation(name=child)
    return post_entity(
        base_url=url, realm=realm, token=token,
        entity=child, response_debug_processor=response_debug_processor
    )
