
import json
from typing import List, Optional

import requests
import socket

from flask import make_response
from flask_restful import Api, Resource
from pydantic import BaseModel, parse_obj_as

from plugins.auth_manager.models_pd import UserRepresentation


class AuthCreds(BaseModel):
    username: str
    password: str
    client_id: str = 'admin-cli'
    grant_type: str = 'password'


def add_resource_to_api(api: Api, resource: Resource, *urls, **kwargs) -> None:
    # This /api/v1 thing is made here to be able to register auth endpoints for local development
    urls = (*(f"/forward-auth/api/v1{url}" for url in urls), *(f"/forward-auth/api/v1{url}/" for url in urls))
    api.add_resource(resource, *urls, **kwargs)


def get_token(url: str, creds: AuthCreds) -> str:
    response = requests.post(url, data=creds.dict())
    data = response.json()
    return '{token_type} {access_token}'.format(**data)


class ApiError(Exception):
    def __init__(self, message=''):
        super(ApiError, self).__init__(message)

#
# def get_users(url: str, token: str, realm: str = '', **kwargs) -> dict:
#     url = url.format(realm=realm)
#     # print(f'{url=}')
#     headers = {'Authorization': token}
#     response = requests.get(url, headers=headers, params=kwargs)
#     # print(f'{response.status_code=}')
#     if response.status_code == 401:
#         raise ApiError(f'Users request error: {response.json().get("error", str(response.content))}')
#     data = response.json()
#     # print(f'{data=}')
#     return data


def put_users(url: str, token: str, body: UserRepresentation, realm: str = ''):
    url = url.format(realm=realm)
    headers = {'Authorization': token, 'Content-Type': 'application/json'}
    response = requests.put(url, headers=headers, json=body.dict(exclude_unset=True))
    return response


def post_users(url: str, token: str, body: UserRepresentation, realm: str = ''):
    if not body.username:
        raise ApiError('Body must contain a username')
    url = url.format(realm=realm)
    headers = {'Authorization': token}
    response = requests.post(url, headers=headers, json=body.dict(exclude_unset=True))
    return response


def delete_users(url: str, token: str, realm: str = ''):
    url = url.format(realm=realm)
    headers = {'Authorization': token}
    response = requests.delete(url, headers=headers)
    return response


if __name__ == '__main__':

    creds = AuthCreds(
        username='api_test',
        password='api_test',
    )
    host = 'http://172.19.0.8'
    uri = '/auth/realms/master/protocol/openid-connect/token'
    t = get_token(f'{host}{uri}', creds)
    uri = '/auth/admin/realms/{realm}/users'
    users = get_users(f'{host}{uri}', t, realm='master')
    print(users)
    # pd_users = parse_obj_as(List[UserRepresentation], users)
    # print(pd_users)
    for i in users:
        # for k, v in i.dict(exclude_unset=True).items():
        #     print(f'{k}: {v}')
        print(i.json(exclude_unset=True, indent=2))
        print('*'*88)
