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


import random

from devtools import debug

from plugins.auth_manager.api.group import GroupAPI
from plugins.auth_manager.api.user import UserAPI, UsergroupsAPI
from plugins.auth_manager.models.group_pd import GroupRepresentation
from plugins.auth_manager.models.token_pd import AuthCreds
from plugins.auth_manager.models.user_pd import UserRepresentation
from plugins.auth_manager.utils.tools import get_token

host = 'http://172.19.0.7'
creds = AuthCreds(
    username='api_test',
    password='api_test',
)

user = UserRepresentation()
user.username = 'test_user'

realm = 'carrier'
token = get_token(url=f'{host}/auth/realms/master/protocol/openid-connect/token', creds=creds)


user_post_url = host + '/auth/admin/realms/{realm}/users'
response = UserAPI._post(
    url=user_post_url,
    token=token,
    realm=realm,
    body=user
)
debug('User created: ')
debug(response)


response = UserAPI._get(
    url=user_post_url,
    token=token,
    realm=realm,
    username=user.username
)
debug('Search results')
debug(response)

created_user = UserRepresentation.parse_obj(response.data[-1])
debug(created_user)


user_put_url = f'{user_post_url}/{created_user.id}'
user.lastName = random.choice(['hitler', 'putin', 'lukashenko'])
user.firstName = random.choice(['vladimir', 'alexander', 'adolf'])
response = UserAPI._put(
    url=user_put_url,
    token=token,
    realm=realm,
    body=user
)
debug('PUT response')
debug(response)










group_post_url = host + '/auth/admin/realms/{realm}/groups'
group = GroupRepresentation()
group.name = 'test_group'
response = GroupAPI._post(
    url=group_post_url,
    token=token,
    realm=realm,
    body=group
)
debug('Creating group')
debug(response)


response = UserAPI._get(
    url=group_post_url,
    token=token,
    realm=realm,
    search=group.name
)
debug('Group search results')
debug(response)


created_group = GroupRepresentation.parse_obj(response.data[-1])
debug(created_group)



url = f"{user_post_url}/{created_user.id}/groups/{created_group.id}"
UsergroupsAPI._add_user_to_group(
    url=url,
    token=token,
    realm=realm,
)
debug('Add created user to created group')



response = UserAPI._delete(
    url=user_put_url,
    token=token,
    realm=realm
)
debug('User DELETE response')
debug(response)


response = UserAPI._delete(
    url=f'{group_post_url}/{created_group.id}',
    token=token,
    realm=realm
)
debug('Group DELETE response')
debug(response)
