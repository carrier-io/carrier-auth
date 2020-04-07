import importlib
from time import time
from base64 import b64decode
from flask import current_app, session, request, redirect, make_response, Blueprint
from auth.drivers.oidc import _validate_basic_auth, _validate_token_auth

bp = Blueprint("root", __name__)


def handle_auth(auth_header):
    if "Basic " in auth_header:
        auth = auth_header.strip().split(' ')
        username, password = b64decode(auth[1].strip()).decode().split(':', 1)
        if not _validate_basic_auth(username, password):
            return make_response("KO", 401)
    elif any(b in auth_header for b in ["bearer ", "Bearer "]):
        auth = auth_header.strip().split(' ')
        if not _validate_token_auth(auth[1]):
            return make_response("KO", 401)
    else:
        return make_response("KO", 401)
    return make_response("OK")


@bp.route("/auth")
def auth():  # pylint: disable=R0201,C0111
    # Check if need to login
    target = request.args.get("target")
    scope = request.args.get("scope")
    if "Authorization" in request.headers:
        return handle_auth(request.headers.get("Authorization"))
    if not session.get('auth_attributes') or session['auth_attributes']['exp'] < int(time()):
        return redirect(current_app.config["auth"]["login_handler"], 302)
    if not session.get("auth", False) and not current_app.config["global"]["disable_auth"]:
        # Redirect to login
        for header in ["X-Forwarded-Proto", "X-Forwarded-Host", "X-Forwarded-Port", "X-Forwarded-Uri"]:
            if header in request.headers:
                session[header] = request.headers[header]
        return redirect(current_app.config["auth"].get("auth_redirect",
                                                       f"{request.base_url}{request.script_root}/login"))
    if target is None:
        target = "raw"
    # Map auth response
    response = make_response("OK")
    try:
        mapper = importlib.import_module(f"auth.mappers.{target}")
        response = mapper.auth(scope, response)
    except:  # pylint: disable=W0702
        from traceback import format_exc
        current_app.logger.error(f"Failed to map auth data {format_exc()}")
    return response


@bp.route("/token")
def token():  # pylint: disable=R0201,C0111
    return redirect(current_app.config["auth"]["token_handler"], 302)


@bp.route("/login")
def login():  # pylint: disable=R0201,C0111
    return redirect(current_app.config["auth"]["login_handler"], 302)


@bp.route("/logout")
def logout():  # pylint: disable=R0201,C0111,C0103
    to = request.args.get('to')
    return redirect(current_app.config["auth"]["logout_handler"] + (f"?to={to}" if to is not None else ""))
