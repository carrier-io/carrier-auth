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

from json import dumps, loads

from flask import session, redirect, request, Blueprint, g, current_app
from oic import rndstr
from oic.oauth2.exception import GrantError
from oic.oic import Client
from oic.oic.message import ProviderConfigurationResponse, RegistrationResponse, AuthorizationResponse
from oic.utils.authn.client import CLIENT_AUTHN_METHOD
from requests import get, post

from auth.utils.session import clear_session

bp = Blueprint("oidc", __name__)


def create_oidc_client(issuer=None, registration_info=None):
    if "oidc" not in g:
        g.oidc = Client(client_authn_method=CLIENT_AUTHN_METHOD)
        config = get(f"{issuer}/.well-known/openid-configuration", headers={"Content-type": "application/json"}).json()
        provider_config = ProviderConfigurationResponse(**config)
        g.oidc.handle_provider_config(provider_config, issuer)
        g.oidc.store_registration_info(
            RegistrationResponse(**registration_info)
        )
        g.oidc.redirect_uris.append(f"{g.oidc.registration_response['redirect_uris'][0]}/callback")
    return g.oidc


def _build_redirect_url():
    for header in ("X-Forwarded-Proto", "X-Forwarded-Host", "X-Forwarded-Port"):
        if header not in session:
            if "X-Forwarded-Uri" not in session:
                return current_app.config["auth"]["login_default_redirect_url"]
            return session.pop("X-Forwarded-Uri")
    proto = session.pop("X-Forwarded-Proto")
    host = session.pop("X-Forwarded-Host")
    port = session.pop("X-Forwarded-Port")
    if (proto == "http" and port != "80") or (proto == "https" and port != "443"):
        port = f":{port}"
    else:
        port = ""
    uri = session.pop("X-Forwarded-Uri")
    return f"{proto}://{host}{port}{uri}"


def _validate_basic_auth(login, password, scope="openid"):
    url = f'{current_app.config["oidc"]["issuer"]}/protocol/openid-connect/token'
    data = {
        "username": login,
        "password": password,
        "scope": scope,
        "grant_type": "password",
        "client_id": current_app.config["oidc"]["registration"]["client_id"],
        "client_secret": current_app.config["oidc"]["registration"]["client_secret"],
    }
    resp = loads(post(url, data=data, headers={"content-type": "application/x-www-form-urlencoded"}).content)
    if resp.get("error"):
        return False
    return True


def _validate_token_auth(refresh_token, scope="openid"):
    url = f'{current_app.config["oidc"]["issuer"]}/protocol/openid-connect/token'
    data = {
        "refresh_token": refresh_token,
        "scope": scope,
        "grant_type": "refresh_token",
        "client_id": current_app.config["oidc"]["registration"]["client_id"],
        "client_secret": current_app.config["oidc"]["registration"]["client_secret"],
    }
    resp = loads(post(url, data=data, headers={"content-type": "application/x-www-form-urlencoded"}).content)
    if resp.get("error"):
        return False
    return True


def _delete_refresh_token(refresh_token: str) -> None:
    url = f'{current_app.config["oidc"]["issuer"]}/protocol/openid-connect/logout'
    data = {
        "refresh_token": refresh_token,
        "client_id": current_app.config["oidc"]["registration"]["client_id"],
        "client_secret": current_app.config["oidc"]["registration"]["client_secret"],
    }
    post(url,
         data=data,
         params={"delete_offline_token": True},
         headers={"content-type": "application/x-www-form-urlencoded"})


def _auth_request(scope="openid", redirect="/callback", response_type="code"):
    session["state"] = rndstr()
    session["nonce"] = rndstr()
    client = create_oidc_client(current_app.config["oidc"]["issuer"],
                                current_app.config["oidc"]["registration"])
    current_app.logger.info(f"{client.registration_response['redirect_uris'][0]}{redirect}")
    auth_req = client.construct_AuthorizationRequest(request_args={
        "client_id": client.client_id,
        "response_type": response_type,
        "scope": scope,
        "state": session["state"],
        "nonce": session["nonce"],
        "redirect_uri": f"{client.registration_response['redirect_uris'][0]}{redirect}",
    })
    login_url = auth_req.request(client.authorization_endpoint)
    return login_url


def _do_logout(to=None):
    if not to:
        to = request.args.get('to', current_app.config["auth"]["login_handler"])
    return_to = current_app.config["auth"]["logout_default_redirect_url"]
    current_app.logger.info(to)
    if to is not None and to in current_app.config["auth"]["logout_allowed_redirect_urls"]:
        return_to = to
    client = create_oidc_client(current_app.config["oidc"]["issuer"], current_app.config["oidc"]["registration"])
    try:
        end_req = client.construct_EndSessionRequest(
            state=session["state"],
            request_args={"redirect_uri": return_to}
        )
    except GrantError:
        clear_session(session)
        return f"{client.end_session_endpoint}?redirect_uri={return_to}"
    logout_url = end_req.request(client.end_session_endpoint)
    if current_app.config["oidc"]["debug"]:
        current_app.logger.warning("Logout URL: %s", logout_url)
    clear_session(session)
    return logout_url


@bp.route("/login")
def login():
    return redirect(_auth_request(), 302)


@bp.route("/token")
def token():
    return redirect(_do_logout(to="/forward-auth/oidc/token/redirect"))


@bp.route("/token/redirect")
def new_token():
    return redirect(_auth_request(scope="openid offline_access"))


@bp.route("/logout")
def logout():
    logout_url = _do_logout()
    return redirect(logout_url, 302)


@bp.route("/callback")
def callback():
    client = create_oidc_client(current_app.config["oidc"]["issuer"], current_app.config["oidc"]["registration"])
    auth_resp = client.parse_response(AuthorizationResponse, info=dumps(request.args.to_dict()), sformat="json")
    if "state" not in session or auth_resp["state"] != session["state"]:
        return redirect(current_app.config["endpoints"]["access_denied"], 302)
    access_token_resp = client.do_access_token_request(
        state=auth_resp["state"],
        request_args={"code": auth_resp["code"]},
        authn_method="client_secret_basic"
    )
    session_state = session.pop("state")
    session_nonce = session.pop("nonce")
    id_token = dict(access_token_resp["id_token"])
    if access_token_resp["refresh_expires_in"] == 0:
        session["X-Forwarded-Uri"] = f"/token?id={access_token_resp['refresh_token']}"
    redirect_to = _build_redirect_url()
    clear_session(session)
    session["name"] = "auth"
    session["state"] = session_state
    session["nonce"] = session_nonce
    session["auth_attributes"] = id_token
    session["auth"] = True
    session["auth_errors"] = []
    session["auth_nameid"] = ""
    session["auth_sessionindex"] = ""
    #
    if current_app.config["oidc"]["debug"]:
        current_app.logger.warning("Callback redirect URL: %s", redirect_to)
    #
    return redirect(redirect_to, 302)
