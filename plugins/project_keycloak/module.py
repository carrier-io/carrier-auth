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
from os import getenv

import flask  # pylint: disable=E0401
from arbiter import Minion
from flask import request, render_template, session, redirect, url_for, make_response
from pydantic import ValidationError
from pylon.core.tools import log  # pylint: disable=E0611,E0401
from pylon.core.tools import module  # pylint: disable=E0611,E0401

from plugins.project_keycloak.group_handler import KeycloakGroupsHandler
from plugins.project_keycloak.invitation_handler import InvitationHandler
from plugins.project_keycloak.utils import current_user_id, current_user_email


class Module(module.ModuleModel):
    """ Galloper module """

    def __init__(self, settings, root_path, context):
        self.settings = settings
        self.root_path = root_path
        self.context = context
        self.rpc_prefix = 'project_keycloak_'

    def init(self):
        """ Init module """
        log.info("Initializing module project_keycloak")

        bp = flask.Blueprint(  # pylint: disable=C0103
            'project_keycloak', 'plugins.project_keycloak',
            root_path=self.root_path,
            url_prefix=f'{self.context.url_prefix}/'
        )
        bp.add_url_rule("/join/<url_id>", "project_join", self.project_join)
        self.context.app.register_blueprint(bp)

        KeycloakGroupsHandler.set_rpc_manager(self.context.rpc_manager)
        self.context.rpc_manager.register_function(
            KeycloakGroupsHandler,
            name=f'{self.rpc_prefix}group_handler'
        )
        self.context.rpc_manager.register_function(
            lambda: [KeycloakGroupsHandler.MAIN_GROUP_NAME, *KeycloakGroupsHandler.SUBGROUP_NAMES],
            name=f'{self.rpc_prefix}group_list'
        )

        minion = Minion(
            host=getenv('RABBIT_HOST'), port=5672,
            user=getenv('RABBITMQ_USER'), password=getenv('RABBITMQ_PASSWORD')
        )
        minion.task(name='send_invitation')(InvitationHandler.tmp_invite)
        minion.rpc(workers=1)

    def deinit(self):  # pylint: disable=R0201
        """ De-init module """
        log.info("De-initializing module")

    def project_join(self, url_id):
        try:
            user_id = current_user_id()
            user_email = current_user_email()
        except KeyError:
            session['X-Forwarded-Uri'] = request.url
            return redirect(url_for('auth_root.login'))

        invitation_handler = InvitationHandler()
        try:
            invitation = invitation_handler.load(url_id)
        except ValidationError:
            return make_response('Error 404<br/>Link invalid or expired', 404)

        if not invitation.check_email(user_email):
            return make_response('Error: 403<br/>Invitation link is email-bound. Wrong user email', 403)

        api_response = self.context.rpc_manager.call.auth_manager_add_users_to_groups(
            realm=KeycloakGroupsHandler.REALM,
            token=self.context.rpc_manager.call.auth_manager_get_token(),
            users=[user_id],
            groups=invitation.groups,
        )
        if not api_response.success:
            log.critical(f'Something went wrong on adding user to groups {api_response.error}')
            return make_response('Error: 500<br/>Something went wrong while adding user to groups', 500)

        self.context.rpc_manager.timeout(5).set_active_project(invitation.project_id)

        return render_template('join_success.html', redirect_url=url_for('theme.index'), )
