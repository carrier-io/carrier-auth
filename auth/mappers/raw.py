#   Copyright 2020
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""
    Mapper: raw
"""

from flask import request, current_app, session


def auth(scope, response):
    """ Map auth data """
    response.headers["X-Auth-Session-Endpoint"] = f"{request.base_url}{current_app.config['endpoints']['info']}/query"
    response.headers["X-Auth-Session-Name"] = session["name"]
    return response


def info(scope=None):
    """ Map info data """
    result = dict()
    result["auth"] = session.get("auth", False)
    result["auth_errors"] = session.get("auth_errors", list())
    result["auth_nameid"] = session.get("auth_nameid", "")
    result["auth_sessionindex"] = session.get("auth_sessionindex", "")
    result["auth_attributes"] = session.get("auth_attributes", dict())
    return result
