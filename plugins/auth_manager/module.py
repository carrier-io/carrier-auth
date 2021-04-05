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

import flask  # pylint: disable=E0401
from flask import session, make_response, request

from pylon.core.tools import log  # pylint: disable=E0611,E0401
from pylon.core.tools import module  # pylint: disable=E0611,E0401

from plugins.auth_manager.api.base import BaseResource
from plugins.auth_manager.api.group import GroupAPI
from plugins.auth_manager.api.membership import MembershipAPI
from plugins.auth_manager.api.user import UserAPI, UsergroupsAPI
from plugins.auth_manager.models.token_pd import AuthCreds
from plugins.auth_manager.rpc import get_users, get_groups, put_entity, post_entity, post_group, delete_entity, \
    add_users_to_groups, expel_users_from_groups
from plugins.auth_manager.utils.tools import add_resource_to_api, get_token
from plugins.auth_root.utils.decorators import push_kwargs


class Module(module.ModuleModel):
    """ Pylon module """

    def __init__(self, settings, root_path, context):
        self.settings = settings
        self.root_path = root_path
        self.context = context
        self.rpc_prefix = 'auth_manager_'

    def init(self):
        """ Init module """
        log.info('Initializing module auth_manager')
        url_prefix = f'{self.context.url_prefix}/{self.context.auth_settings["endpoints"]["manager"]}/'

        BaseResource.set_settings(self.context.auth_settings)
        add_resource_to_api(self.context.api, UsergroupsAPI,
                            f'/user/<string:realm>/<string:user_id>/groups',
                            f'/user/<string:realm>/<string:user_id>/groups/<string:group_id>',
                            methods=['GET', 'PUT', 'DELETE']
                            )
        add_resource_to_api(self.context.api, UserAPI,
                            f'/user/<string:realm>',
                            f'/user/<string:realm>/<string:user_id>'
                            )
        add_resource_to_api(self.context.api, GroupAPI,
                            f'/group/<string:realm>',
                            f'/group/<string:realm>/<string:group_id>'
                            )
        add_resource_to_api(self.context.api, MembershipAPI,
                            f'/group/<string:realm>/membership',
                            methods=['PUT', 'POST']
                            )
        # add_resource_to_api(self.context.api, SubgroupAPI,
        #                     f'/group/<string:realm>/<string:group_id>',
        #                     methods=['POST']
        #                     )

        # self.context.api.add_resource(user_api, f'{url_prefix}user/<string:realm>')
        # self.context.api.add_resource(user_api, '/user/<string:realm>/<string:user_id>')
        # print(self.context.api.endpoints)
        # print(self.context.api)
        # https://flask-restful.readthedocs.io/en/latest/quickstart.html#a-minimal-api


        # rpc_manager
        # token
        self.context.rpc_manager.register_function(
            push_kwargs(
                url=self.context.auth_settings['manager']['token_url'],
                creds=AuthCreds(
                    username=self.context.auth_settings['manager']['username'],
                    password=self.context.auth_settings['manager']['password']
                )
            )(get_token),
            name=f'{self.rpc_prefix}get_token'
        )
        # get functions
        self.context.rpc_manager.register_function(get_users, name=f'{self.rpc_prefix}get_users')
        self.context.rpc_manager.register_function(get_groups, name=f'{self.rpc_prefix}get_groups')
        # put functions
        self.context.rpc_manager.register_function(put_entity, name=f'{self.rpc_prefix}put_entity')
        self.context.rpc_manager.register_function(
            push_kwargs(base_url=self.context.auth_settings['manager']['user_url'])(put_entity),
            name=f'{self.rpc_prefix}put_user'
        )
        self.context.rpc_manager.register_function(
            push_kwargs(base_url=self.context.auth_settings['manager']['group_url'])(put_entity),
            name=f'{self.rpc_prefix}put_group'
        )
        # post functions
        self.context.rpc_manager.register_function(post_entity, name=f'{self.rpc_prefix}post_entity')
        self.context.rpc_manager.register_function(
            push_kwargs(base_url=self.context.auth_settings['manager']['user_url'])(post_entity),
            name=f'{self.rpc_prefix}post_user'
        )
        self.context.rpc_manager.register_function(
            push_kwargs(base_url=self.context.auth_settings['manager']['group_url'])(post_group),
            name=f'{self.rpc_prefix}post_group'
        )
        # delete functions
        self.context.rpc_manager.register_function(delete_entity, name=f'{self.rpc_prefix}delete_entity')
        self.context.rpc_manager.register_function(
            push_kwargs(base_url=self.context.auth_settings['manager']['user_url'])(delete_entity),
            name=f'{self.rpc_prefix}delete_user'
        )
        self.context.rpc_manager.register_function(
            push_kwargs(base_url=self.context.auth_settings['manager']['group_url'])(delete_entity),
            name=f'{self.rpc_prefix}delete_group'
        )
        # group membership functions
        self.context.rpc_manager.register_function(
            push_kwargs(user_url=self.context.auth_settings['manager']['user_url'])(add_users_to_groups),
            name=f'{self.rpc_prefix}add_users_to_groups'
        )
        self.context.rpc_manager.register_function(
            push_kwargs(user_url=self.context.auth_settings['manager']['user_url'])(expel_users_from_groups),
            name=f'{self.rpc_prefix}expel_users_from_groups'
        )


        # blueprint endpoints
        bp = flask.Blueprint(
            'auth_manager', 'plugins.auth_manager',
            root_path=self.root_path,
            url_prefix=url_prefix
        )
        bp.add_url_rule('/clear_token', 'clear_token', self.clear_token, methods=['GET'])
        # Register in app
        self.context.app.register_blueprint(bp)

    def deinit(self):  # pylint: disable=R0201
        """ De-init module """
        log.info('De-initializing module auth_manager')

    # def token(self):
    #     token = session.get('api_token')
    #     if not token:
    #         creds = AuthCreds(
    #             username=self.context.auth_settings['manager']['username'],
    #             password=self.context.auth_settings['manager']['password']
    #         )
    #         token = self.context.rpc_manager.call.auth_manager_get_token(
    #             self.context.auth_settings['manager']['token_url'],
    #             creds
    #         )
    #         session['api_token'] = token
    #         # session['api_token'] = str(token)
    #         # session['api_refresh_token'] = token.refresh_token
    #     return token

    def clear_token(self):
        from flask import redirect
        for k in ('api_token', 'api_refresh_token'):
            try:
                del session[k]
            except KeyError:
                ...
        return redirect(
            f'http://{self.context.app.config["SERVER_NAME"]}{self.context.auth_settings["endpoints"]["root"]}/'
        )
