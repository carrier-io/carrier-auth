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
from plugins.auth_manager.utils.tools import add_resource_to_api, get_token


class Module(module.ModuleModel):
    """ Pylon module """

    def __init__(self, settings, root_path, context):
        self.settings = settings
        self.root_path = root_path
        self.context = context

    def init(self):
        """ Init module """
        log.info('Initializing module auth_manager')
        url_prefix = f'{self.context.url_prefix}/{self.context.auth_settings["endpoints"]["manager"]}/'

        # print(self.context.api)
        BaseResource.set_settings(self.context.auth_settings)
        # print(f'{UserAPI.settings}')
        # print(f'{BaseResource.settings}')
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

        self.context.rpc_manager.register_function(get_token, name='auth_manager_get_token')
        # self.context.rpc_manager.register_function(get_users, name='auth_manager_get_users')
        # self.context.rpc_manager.register_function(put_users, name='auth_manager_put_users')
        # self.context.rpc_manager.register_function(post_users, name='auth_manager_post_users')
        # self.context.rpc_manager.register_function(delete_users, name='auth_manager_delete_users')

        bp = flask.Blueprint(
            'auth_manager', 'plugins.auth_manager',
            root_path=self.root_path,
            url_prefix=url_prefix
        )
        # bp.add_url_rule('/token', 'token', self.token, methods=['GET'])
        bp.add_url_rule('/clear_token', 'clear_token', self.clear_token, methods=['GET'])

        # # bp.add_url_rule('/users/<realm>', 'user-list', self.user_list, methods=['GET'])
        # # bp.add_url_rule('/users/<realm>/<id_>', 'user-detail', self.user_detail, methods=['GET'])
        # bp.add_url_rule('/users/<realm>/<id_>', 'user-update', self.user_update, methods=['PUT'])
        # bp.add_url_rule('/users/<realm>', 'user-create', self.user_create, methods=['POST'])
        # bp.add_url_rule('/users/<realm>/<id_>', 'user-delete', self.user_delete, methods=['DELETE'])



        # Register in app
        self.context.app.register_blueprint(bp)

    def deinit(self):  # pylint: disable=R0201
        """ De-init module """
        log.info('De-initializing module auth_manager')

    def token(self):
        token = session.get('api_token')
        if not token:
            creds = AuthCreds(
                username=self.context.auth_settings['manager']['username'],
                password=self.context.auth_settings['manager']['password']
            )
            token = self.context.rpc_manager.call.auth_manager_get_token(
                self.context.auth_settings['manager']['token_url'],
                creds
            )
            session['api_token'] = token
            # session['api_token'] = str(token)
            # session['api_refresh_token'] = token.refresh_token
        return token

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

    # def user_list(self, realm: str = 'master', retries: int = 0):
    #     from flask import request
    #     try:
    #         data = self.context.rpc_manager.call.auth_manager_get_users(
    #             url=self.context.auth_settings['manager']['user_url'],
    #             token=self.token(),
    #             realm=realm,
    #             **request.args
    #         )
    #     except ApiError:
    #         log.warning('Reacquiring api token')
    #         self.clear_token()
    #         if retries > 2:
    #             return make_response(ApiError, 500)
    #         return self.user_list(realm=realm, retries=retries+1)
    #     # return parse_obj_as(List[UserRepresentation], data).json()
    #     return flask.jsonify(data)

    # def user_detail(self, realm: str, id_: str, retries: int = 0):
    #     url = f"{self.context.auth_settings['manager']['user_url']}/{id_}"
    #     try:
    #         data = self.context.rpc_manager.call.auth_manager_get_users(
    #             url=url,
    #             token=self.token(),
    #             realm=realm,
    #         )
    #     except ApiError:
    #         log.warning('Reacquiring api token')
    #         self.clear_token()
    #         if retries > 2:
    #             return make_response(ApiError, 500)
    #         return self.user_detail(realm=realm, id_=id_, retries=retries+1)
    #     # return parse_obj_as(List[UserRepresentation], data).json()
    #     return flask.jsonify(data)

    # @staticmethod
    # def _get_body(body: [dict, UserRepresentation] = None):
    #     if not body:
    #         body = request.json
    #         if not body:
    #             return flask.jsonify({'error': 'body required'})
    #     if isinstance(body, dict):
    #         body = UserRepresentation.parse_obj(request.json)
    #     elif isinstance(body, str):
    #         body = UserRepresentation.parse_raw(request.json)
    #     else:
    #         if not isinstance(body, UserRepresentation):
    #             body = UserRepresentation(**body)
    #     return body

    # def user_update(self, realm: str, id_: str, body: [dict, UserRepresentation] = None):
    #     body = self._get_body(body)
    #     url = f"{self.context.auth_settings['manager']['user_url']}/{id_}"
    #     response = self.context.rpc_manager.call.auth_manager_put_users(
    #         url=url,
    #         token=self.token(),
    #         realm=realm,
    #         body=body
    #     )
    #
    #     return make_response('', response.status_code)
    #
    # def user_create(self, realm: str, body: [dict, UserRepresentation] = None):
    #     body = self._get_body(body)
    #     url = self.context.auth_settings['manager']['user_url']
    #     response = self.context.rpc_manager.call.auth_manager_post_users(
    #         url=url,
    #         token=self.token(),
    #         realm=realm,
    #         body=body
    #     )
    #
    #     return make_response('', response.status_code)
    #
    # def user_delete(self, realm: str, id_: str):
    #     url = f"{self.context.auth_settings['manager']['user_url']}/{id_}"
    #     response = self.context.rpc_manager.call.auth_manager_delete_users(
    #         url=url,
    #         token=self.token(),
    #         realm=realm,
    #     )

        # return make_response('', response.status_code)
