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


class ApiError(Exception):
    def __init__(self, message=''):
        self.message = message
        super(ApiError, self).__init__(message)


class TokenExpiredError(ApiError):
    ...


class TokenRefreshError(ApiError):
    ...


class AmbiguousIdError(ApiError):
    _message = 'Either entity must have and id or entity_id as kwarg. IDs are not equal: id1={} =! id2{}'

    def __init__(self, id1, id2):
        super(AmbiguousIdError, self).__init__(message=self._message.format(id1, id2))


class IdExtractError(ApiError):
    _message = 'Cannot get id named: "{key}" from {obj} of type {obj_type}'

    def __init__(self, obj, key):
        super(IdExtractError, self).__init__(message=self._message.format(key=key, obj=obj, obj_type=type(obj)))
