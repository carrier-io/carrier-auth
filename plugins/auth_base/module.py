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
import jinja2  # pylint: disable=E0401


from pylon.core.tools import log  # pylint: disable=E0611,E0401
from pylon.core.tools import module  # pylint: disable=E0611,E0401
from plugins.auth_base.app import bp
from plugins.auth_base.config import Config, SettingsFileNotFoundError


class Module(module.ModuleModel):
    """ Pylon module """

    def __init__(self, settings, root_path, context):
        self.settings = settings
        self.root_path = root_path
        self.context = context

    def init(self):
        """ Init module """
        log.info('Initializing module auth_base')
        try:
            self.context.app.config.from_object(Config())
        except SettingsFileNotFoundError as e:
            self.context.app.logger.error(repr(e))
            self.deinit()
        self.context.app.register_blueprint(bp, url_prefix=self.context.app.config['SETTINGS']['endpoints']['root'])

    def deinit(self):  # pylint: disable=R0201
        """ De-init module """
        log.info('De-initializing module auth_base')


