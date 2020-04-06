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

import json
import os
from json import dumps

import requests
from flask import session, redirect, request, Blueprint, g, current_app
from oic import rndstr
from oic.oauth2.exception import GrantError
from oic.oic import Client
from oic.oic.message import ProviderConfigurationResponse, RegistrationResponse, AuthorizationResponse
from oic.utils.authn.client import CLIENT_AUTHN_METHOD

from auth.utils.session import clear_session

bp = Blueprint("oidc", __name__)


def create_oidc_client(issuer=None, registration_info=None):
    if "oidc" not in g:
        oidc = Client(client_authn_method=CLIENT_AUTHN_METHOD)
        config = requests.get(
            f"{issuer}/.well-known/openid-configuration", headers={"Content-type": "application/json"}
        ).json()
        provider_config = ProviderConfigurationResponse(**config)
        oidc.handle_provider_config(provider_config, issuer)
        oidc.store_registration_info(
            RegistrationResponse(**registration_info)
        )
        oidc.redirect_uris.append(f"{oidc.registration_response['redirect_uris'][0]}/callback")
        oidc.redirect_uris.append(f"{oidc.registration_response['redirect_uris'][0]}/token/callback")
        g.oidc = oidc
    return g.oidc


def _build_redirect_url():
    for header in ["X-Forwarded-Proto", "X-Forwarded-Host", "X-Forwarded-Port", "X-Forwarded-Uri"]:
        if header not in session:
            return current_app.config["auth"]["login_default_redirect_url"]
    proto = session.pop("X-Forwarded-Proto")
    host = session.pop("X-Forwarded-Host")
    port = session.pop("X-Forwarded-Port")
    if (proto == "http" and port != "80") or (proto == "https" and port != "443"):
        port = f":{port}"
    else:
        port = ""
    uri = session.pop("X-Forwarded-Uri")
    return f"{proto}://{host}{port}{uri}"


def _auth_request(scope="openid", redirect="/callback", recreate_scope=True):
    if recreate_scope:
        session["state"] = rndstr()
        session["nonce"] = rndstr()

    client = create_oidc_client(current_app.config["oidc"]["issuer"],
                                current_app.config["oidc"]["registration"])
    current_app.logger.info(f"{client.registration_response['redirect_uris'][0]}{redirect}")
    auth_req = client.construct_AuthorizationRequest(request_args={
        "client_id": client.client_id,
        "response_type": "code",
        "scope": [scope],
        "state": session["state"],
        "nonce": session["nonce"],
        "redirect_uri": f"{client.registration_response['redirect_uris'][0]}{redirect}",
    })
    login_url = auth_req.request(client.authorization_endpoint)
    if current_app.config["oidc"]["debug"]:
        current_app.logger.warning("OIDC login URL: %s", login_url)
    return login_url


@bp.route("/login")
def login():
    return redirect(_auth_request(), 302)


@bp.route("/token")
def token():
    client = create_oidc_client(current_app.config["oidc"]["issuer"],
                                current_app.config["oidc"]["registration"])
    data = {
        "grant_type": "password",
        "client_id": client.client_id,
        "client_secret": client.client_secret,
        "username": "service_user",
        "password": "service_user"
    }
    response = requests.post(client.token_endpoint, data=data)
    if response.status_code != requests.codes.ok:
        return json.dumps({
            "message": "Keycloak error",
            "status_code": response.status_code,
            "text": response.text
        })
    data = response.json()
    return data.get("access_token")


@bp.route("/logout")
def logout():  # pylint: disable=R0201,C0111,C0103
    to = request.args.get("to", current_app.config["auth"]["login_handler"])
    return_to = current_app.config["auth"]["logout_default_redirect_url"]
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
        return redirect(f"{client.end_session_endpoint}?redirect_uri={return_to}", 302)
    logout_url = end_req.request(client.end_session_endpoint)
    if current_app.config["oidc"]["debug"]:
        current_app.logger.warning("Logout URL: %s", logout_url)
    clear_session(session)
    return redirect(logout_url, 302)


@bp.route("/token/callback")
def token_callback():
    pass


@bp.route("/callback")
def callback():  # pylint: disable=R0201,C0111,W0613
    client = create_oidc_client(current_app.config["oidc"]["issuer"], current_app.config["oidc"]["registration"])
    auth_resp = client.parse_response(AuthorizationResponse, info=dumps(request.args.to_dict()), sformat="json")
    if "state" not in session or auth_resp["state"] != session["state"]:
        return redirect(current_app.config["endpoints"]["access_denied"], 302)
    access_token_resp = client.do_access_token_request(
        state=auth_resp["state"],
        request_args={"code": auth_resp["code"]},
        authn_method="client_secret_basic"
    )
    if current_app.config["oidc"]["debug"]:
        current_app.logger.warning("Callback access_token_resp: %s", access_token_resp)
    redirect_to = _build_redirect_url()
    session_state = session.pop("state")
    session_nonce = session.pop("nonce")
    id_token = dict(access_token_resp["id_token"])
    clear_session(session)
    session["name"] = "auth"
    session["state"] = session_state
    session["nonce"] = session_nonce
    session["auth"] = True
    session["auth_errors"] = []
    session["auth_nameid"] = ""
    session["auth_sessionindex"] = ""
    session["auth_attributes"] = id_token
    #
    if current_app.config["oidc"]["debug"]:
        current_app.logger.warning("Callback redirect URL: %s", redirect_to)
    #
    return redirect(redirect_to, 302)
