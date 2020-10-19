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

import jsonpath_rw

from flask import current_app, redirect
from auth.mappers import raw


def auth(scope, response):
    """ Map auth data """
    if scope not in current_app.config["mappers"]["header"]:
        raise redirect(current_app.config["endpoints"]["access_denied"])
    response = raw.auth(scope, response)  # Set "raw" headers too
    auth_info = info(scope)
    if f"/{scope}" not in auth_info["auth_attributes"]["groups"]:
        raise NameError(f"User is not a memeber of {scope} group")
    try:
        for header, path in current_app.config["mappers"]["header"][scope].items():
            response.headers[header] = jsonpath_rw.parse(path).find(auth_info)[0].value
    except:
        current_app.logger.error("Failed to set scope headers")
    return response


def info(scope):
    """ Map info data """
    return raw.info(scope)
