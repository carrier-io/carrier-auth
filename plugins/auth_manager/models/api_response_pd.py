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


from json import JSONDecodeError
from typing import Any, Optional, Callable, Union, List

from pydantic import BaseModel, ValidationError, parse_obj_as
from requests import Response

DebugProcessorType = Optional[Callable[[Response], Any]]


class ApiResponseError(BaseModel):
    message: Any = None
    error_code: Optional[int] = None


class ApiResponse(BaseModel):
    status: int = 200
    success: bool = True
    error: Optional[ApiResponseError] = ApiResponseError()
    data: Any = {}
    debug: Any = {}
    headers: dict = {}

    @classmethod
    def failed(cls, status_code: int = 400, error_message: Any = None):
        klass = cls()
        klass.error.message = error_message
        klass.error.error_code = status_code
        klass.status = klass.error.error_code
        klass.success = False
        return klass

    @staticmethod
    def get_debug_data(response: Response, response_debug_processor: DebugProcessorType = None) -> dict:
        if response_debug_processor:
            try:
                debug_data = response_debug_processor(response)
                if not isinstance(debug_data, dict):
                    return {'data': debug_data}
                else:
                    return debug_data
            except Exception as e:
                return {'processor_failed': str(e)}
        return {}

    @staticmethod
    def get_data_from_response(response: Response):
        try:
            return response.json()
        except JSONDecodeError:
            if response.text:
                return response.text
            return

    @staticmethod
    def format_response_data(data: Any, response_data_type: Union[Callable, BaseModel, List]):
        if is_subclass_of_base_model(response_data_type):
            if isinstance(data, str):
                parsed_data = response_data_type.parse_raw(data)
            elif isinstance(data, list):
                parsed_data = parse_obj_as(List[response_data_type], data)
            elif isinstance(data, dict):
                parsed_data = response_data_type.parse_obj(data)
            else:
                raise ValidationError

        else:
            parsed_data = response_data_type(data)
        return parsed_data


def is_subclass_of_base_model(obj: Any):
    results = [False]
    try:
        results.append(isinstance(obj, BaseModel))
    except TypeError:
        ...
    try:
        results.append(issubclass(type(obj), BaseModel))
    except TypeError:
        ...
    try:
        results.append(issubclass(obj, BaseModel))
    except TypeError:
        ...
    return any(results)
