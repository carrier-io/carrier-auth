#!/usr/bin/python3
# coding=utf-8

#   Copyright 2021 getcarrier.io
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

""" Module """
import os
from queue import Empty

import flask  # pylint: disable=E0401
import jinja2  # pylint: disable=E0401
import yaml
from flask import request, make_response, session, redirect, Response
from time import time

from pylon.core.tools import log  # pylint: disable=E0611,E0401
from pylon.core.tools import module  # pylint: disable=E0611,E0401
from pylon.core.tools.config import config_substitution, vault_secrets

from plugins.auth_root.utils.decorators import push_kwargs
from plugins.auth_root.utils.token_manager import check_auth_token, clear_auth_token, get_auth_token, check_auth


class Module(module.ModuleModel):
    """ Pylon module """

    def __init__(self, settings, root_path, context):
        self.settings = settings
        self.root_path = root_path
        self.context = context
        self.rpc_prefix = None

    def init(self):
        """ Init module """
        log.info('Initializing module auth_root')

        self.rpc_prefix = self.settings['rpc_manager']['prefix']['root']
        bp = flask.Blueprint(  # pylint: disable=C0103
            'auth_root', 'plugins.auth_root',
            root_path=self.root_path,
            url_prefix=f'{self.context.url_prefix}/{self.settings["endpoints"]["root"]}/'
        )
        bp.add_url_rule('/auth', 'auth', self.auth)
        bp.add_url_rule('/me', 'me', self.me, methods=['GET'])
        bp.add_url_rule('/token', 'token', self.token)
        bp.add_url_rule('/login', 'login', self.login)
        bp.add_url_rule('/logout', 'logout', self.logout)

        # Register in app
        self.context.app.register_blueprint(bp)

        # rpc_manager
        self.context.rpc_manager.register_function(
            push_kwargs(
                rpc_manager=self.context.rpc_manager,
                rpc_prefix=self.rpc_prefix,
                rpc_timeout=int(self.settings['rpc_manager']['timeout'])
            )(check_auth),
            name=f'{self.rpc_prefix}check_auth'
        )

    def deinit(self):  # pylint: disable=R0201
        """ De-init module """
        log.info('De-initializing module auth_root')

    @staticmethod
    def load_config():
        settings_data = open(os.getenv('CONFIG_FILENAME'), 'rb').read()
        settings = yaml.load(os.path.expandvars(settings_data), Loader=yaml.SafeLoader)
        return config_substitution(settings, vault_secrets(settings))

    def auth(self):
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
            return self.handle_auth(auth_header=request.headers.get("Authorization", ""))
        if "X-Forwarded-Uri" in request.headers and "/api/v1" in "X-Forwarded-Uri":
            if "Referer" in request.headers and "/api/v1" not in "Referer":
                session["X-Forwarded-Uri"] = request.headers["Referer"]
            else:
                session["X-Forwarded-Uri"] = request.base_url
        if not session.get("auth_attributes") or session["auth_attributes"]["exp"] < int(time()):
            return redirect(self.settings["login_handler_url"], 302)
        if not session.get("auth", False) and not self.settings["disable_auth"]:
            # Redirect to login
            return redirect(self.settings.get(
                "auth_redirect",
                f"{request.base_url}{request.script_root}/login")
            )
        if target is None:
            target = "raw"

        # Map auth response
        response = make_response("OK")
        try:
            self.context.rpc_manager.call_function_with_timeout(
                func='{prefix}{key}'.format(
                    prefix=self.settings['rpc_manager']['prefix']['mappers'],
                    key=target.lower()
                ),
                timeout=int(self.settings['rpc_manager']['timeout']),
                response=response,
                scope=scope
            )
        except Empty:
            log.error(f'Cannot find mapper for auth_key {target}')
            return make_response("KO", 403)
        except (AttributeError, TypeError):
            from traceback import format_exc
            log.error(f"Failed to map auth data {format_exc()}")
        except NameError:
            return redirect(self.settings["login_default_redirect_url"])
        return response

    def me(self):
        if isinstance(session.get("auth_attributes"), dict):
            return flask.jsonify(
                {
                    "username": session.get("auth_attributes")['preferred_username'],
                    "groups": session.get("auth_attributes")['groups']
                }
            )
        if "Authorization" in request.headers:
            auth_header = request.headers.get("Authorization", "")
            if not check_auth_token(auth_header):
                clear_auth_token()
                self.handle_auth(auth_header)
        return flask.jsonify(get_auth_token())

    def token(self):
        return redirect(self.settings["token_handler_url"], 302)

    def login(self):
        return redirect(self.settings["login_handler_url"], 302)

    def logout(self):
        to = request.args.get("to")
        return redirect(
            self.settings["logout_handler_url"] + (f"?to={to}" if to else ""))

    def handle_auth(self, auth_header) -> Response:
        return check_auth(
            auth_header,
            rpc_manager=self.context.rpc_manager,
            rpc_prefix=self.rpc_prefix,
            rpc_timeout=int(self.settings['rpc_manager']['timeout'])
        )
