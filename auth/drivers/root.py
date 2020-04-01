import importlib
from flask import current_app, session, request, redirect, make_response, Blueprint

bp = Blueprint("root", __name__)


@bp.route("/auth")
def auth():  # pylint: disable=R0201,C0111
    # Check if need to login
    target = request.args.get("target")
    scope = request.args.get("scope")
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


@bp.route("/login")
def login():  # pylint: disable=R0201,C0111
    return redirect(current_app.config["auth"]["login_handler"], 302)


@bp.route("/logout")
def logout(to=None):  # pylint: disable=R0201,C0111,C0103
    return redirect(current_app.config["auth"]["logout_handler"] + (f"?to={to}" if to is not None else ""))
