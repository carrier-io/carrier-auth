import requests
from flask_restful import Api, Resource
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    expires_in: int
    refresh_expires_in: int
    refresh_token: str
    token_type: str
    session_state: str
    scope: str

    def __repr__(self):
        return f'{self.token_type} {self.access_token}'

    def __str__(self):
        return self.__repr__()


class AuthCreds(BaseModel):
    username: str
    password: str
    client_id: str = 'admin-cli'
    grant_type: str = 'password'


class RefreshCreds(BaseModel):
    client_id: str = 'admin-cli'
    grant_type: str = 'refresh_token'
    refresh_token: str


def add_resource_to_api(api: Api, resource: Resource, *urls, **kwargs) -> None:
    # This /api/v1 thing is made here to be able to register auth endpoints for local development
    urls = (*(f"/forward-auth/api/v1{url}" for url in urls), *(f"/forward-auth/api/v1{url}/" for url in urls))
    api.add_resource(resource, *urls, **kwargs)



def get_token(url: str, creds: AuthCreds) -> Token:
    response = requests.post(url, data=creds.dict())
    token = Token.parse_obj(response.json())
    return token


def refresh_token(url: str, creds: RefreshCreds) -> Token:
    response = requests.post(url, data=creds.dict())
    print('REFRESH TOKEN', f'{response.json()=}')
    if not response.ok:
        raise TokenRefreshError(response.json())
    token = Token.parse_obj(response.json())
    return token


class ApiError(Exception):
    def __init__(self, message=''):
        self.message = message
        super(ApiError, self).__init__(message)


class TokenExpiredError(ApiError):
    ...


class TokenRefreshError(ApiError):
    ...

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


# def put_users(url: str, token: str, body: UserRepresentation, realm: str = ''):
#     url = url.format(realm=realm)
#     headers = {'Authorization': token, 'Content-Type': 'application/json'}
#     response = requests.put(url, headers=headers, json=body.dict(exclude_unset=True))
#     return response


# def post_users(url: str, token: str, body: UserRepresentation, realm: str = ''):
#     if not body.username:
#         raise ApiError('Body must contain a username')
#     url = url.format(realm=realm)
#     headers = {'Authorization': token}
#     response = requests.post(url, headers=headers, json=body.dict(exclude_unset=True))
#     return response


# def delete_users(url: str, token: str, realm: str = ''):
#     url = url.format(realm=realm)
#     headers = {'Authorization': token}
#     response = requests.delete(url, headers=headers)
#     return response
