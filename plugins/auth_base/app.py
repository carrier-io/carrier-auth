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

import importlib
from json import dumps
from time import time

from flask import current_app, session, request, redirect, make_response, Blueprint

from plugins.auth_base.utils.auth_handlers import AuthHandler
from plugins.auth_base.utils.token_manager import check_auth_token, get_auth_token, clear_auth_token

bp = Blueprint("root", __name__)


def handle_auth(auth_header: str):
    try:
        auth_key, auth_value = auth_header.strip().split(" ")
    except ValueError:
        return make_response("KO", 401)
    if check_auth_token(auth_header=auth_header):
        return make_response("OK", 200)
    return AuthHandler()[auth_key]


@bp.route("/auth")
def auth():
    if "X-Forwarded-Uri" in request.headers:
        if request.headers["X-Forwarded-Uri"].startswith("/static") and \
                any(request.headers["X-Forwarded-Uri"].endswith(res) for res in [".ico", ".js", ".css"]):
            return make_response("OK")
    # Check if need to login
    target = request.args.get("target")
    scope = request.args.get("scope")
    for header in ("X-Forwarded-Proto", "X-Forwarded-Host", "X-Forwarded-Port", "X-Forwarded-Uri"):
        if header in request.headers:
            session[header] = request.headers[header]
    if "Authorization" in request.headers:
        return handle_auth(auth_header=request.headers.get("Authorization", ""))
    if "X-Forwarded-Uri" in request.headers and "/api/v1" in "X-Forwarded-Uri":
        if "Referer" in request.headers and "/api/v1" not in "Referer":
            session["X-Forwarded-Uri"] = request.headers["Referer"]
        else:
            session["X-Forwarded-Uri"] = request.base_url
    if not session.get("auth_attributes") or session["auth_attributes"]["exp"] < int(time()):
        return redirect(current_app.config['SETTINGS']["auth"]["login_handler"], 302)
    if not session.get("auth", False) and not current_app.config['SETTINGS']["global"]["disable_auth"]:
        # Redirect to login
        return redirect(current_app.config['SETTINGS']["auth"].get(
            "auth_redirect",
            f"{request.base_url}{request.script_root}/login")
        )
    if target is None:
        target = "raw"
    # Map auth response
    response = make_response("OK")
    try:
        mapper = importlib.import_module(f"auth.mappers.{target}")
        response = mapper.auth(scope, response)
    except (ImportError, AttributeError, TypeError):
        from traceback import format_exc
        current_app.logger.error(f"Failed to map auth data {format_exc()}")
    except NameError:
        return redirect(current_app.config['SETTINGS']["auth"]["login_default_redirect_url"])
    return response


def me_from_token(auth_header: str):
    if not check_auth_token(auth_header):
        clear_auth_token()
        handle_auth(auth_header=auth_header)
    return get_auth_token()


@bp.route('/me', methods=["GET"])
def me():
    res = {}
    if isinstance(session.get("auth_attributes"), dict):
        res = {
            "username": session.get("auth_attributes")['preferred_username'],
            "groups": session.get("auth_attributes")['groups']
        }
    if not res and "Authorization" in request.headers:
        res = me_from_token(auth_header=request.headers.get("Authorization", ""))
    return make_response(dumps(res), 200)


@bp.route("/token")
def token():
    return redirect(current_app.config['SETTINGS']["auth"]["token_handler"], 302)


@bp.route("/login")
def login():
    return redirect(current_app.config['SETTINGS']["auth"]["login_handler"], 302)


@bp.route("/logout")
def logout():
    to = request.args.get("to")
    return redirect(current_app.config['SETTINGS']["auth"]["logout_handler"] + (f"?to={to}" if to is not None else ""))
