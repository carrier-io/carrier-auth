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

import flask  # pylint: disable=E0401
import jinja2  # pylint: disable=E0401
import yaml

from plugins.auth_mappers.mappers.header import HeaderMapper
from plugins.auth_mappers.mappers.json import JsonMapper
from plugins.auth_mappers.mappers.raw import RawMapper
from plugins.auth_root.utils.decorators import push_kwargs

from pylon.core.tools import log  # pylint: disable=E0611,E0401
from pylon.core.tools import module  # pylint: disable=E0611,E0401
from pylon.core.tools.config import config_substitution, vault_secrets


class Module(module.ModuleModel):
    """ Pylon module """

    def __init__(self, settings, root_path, context):
        self.settings = settings
        self.root_path = root_path
        self.context = context
        self.rpc_prefix = None

    def init(self):
        """ Init module """
        log.info('Initializing module auth_oidc')
        _, _, root_module = self.context.module_manager.get_module("auth_root")
        root_settings = root_module.settings
        self.rpc_prefix = root_settings['rpc_manager']['prefix']['mappers']

        mappers = dict()
        mappers['raw'] = RawMapper(info_endpoint=self.settings['endpoints']['info'])
        mappers['header'] = HeaderMapper(
            info_endpoint=self.settings['endpoints']['info'],
            mapper_settings=self.settings['header'],
            access_denied_endpoint=root_settings['endpoints']['access_denied']
        )
        mappers['json'] = JsonMapper(
            info_endpoint=self.settings['endpoints']['info'],
            mapper_settings=self.settings['json'],
            access_denied_endpoint=root_settings['endpoints']['access_denied']
        )
        # rpc_manager
        for k, v in mappers.items():
            self.context.rpc_manager.register_function(
                func=v.auth,
                name=f'{self.rpc_prefix}{k}'
            )

    def deinit(self):  # pylint: disable=R0201
        """ De-init module """
        log.info('De-initializing module auth_mappers')
