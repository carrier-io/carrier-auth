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
