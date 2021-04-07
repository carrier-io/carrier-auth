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

import urllib

import jsonpath_rw
from flask import request, session, redirect
from pylon.core.tools import log

from plugins.auth_root.mappers import raw
from plugins.auth_root.utils.decorators import require_auth_settings


@require_auth_settings
def auth(scope, response, auth_settings: dict = None):
    """ Map auth data """
    response.headers["X-Auth-Session-Endpoint"] = \
        f"{request.base_url}{auth_settings['endpoints']['info']}" \
        f"/query?target=json&scope={urllib.parse.quote_plus(scope)}"
    response.headers["X-Auth-Session-Name"] = session["name"]
    return response


@require_auth_settings
def info(scope, auth_settings: dict = None):
    """ Map info data """
    if scope not in auth_settings["mappers"]["json"]:
        raise redirect(auth_settings["endpoints"]["access_denied"])
    auth_info = raw.info()
    result = {"raw": auth_info}
    try:
        for key, path in auth_settings["mappers"]["json"][scope].items():
            result[key] = jsonpath_rw.parse(path).find(auth_info)[0].value
    except:  # pylint: disable=W0702
        from traceback import format_exc
        log.error(f"Failed to set scope data {format_exc()}")
    return result
