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

import os

import yaml
from flask import Flask, current_app

from auth.constants import CONFIG_FILENAME, AUTH_PROXIES, APP_HOST, APP_PORT
from auth.utils import config


def read_config():  # Reading the config file
    settings_file = CONFIG_FILENAME
    if not settings_file:
        current_app.logger.error("Settings file path not set. Please set CONFIG_FILENAME")
    with open(settings_file, "rb") as file:
        settings_data = file.read()
        settings = yaml.load(os.path.expandvars(settings_data), Loader=yaml.SafeLoader)
        settings = config.config_substitution(settings, config.vault_secrets(settings))

    current_app.config["global"] = settings["global"]
    current_app.config["endpoints"] = settings["endpoints"]
    current_app.config["auth"] = settings["auth"]
    current_app.config["mappers"] = settings["mappers"]
    current_app.config["keys"] = list()
    for key in AUTH_PROXIES:
        if key not in settings:
            continue
        current_app.config[key] = settings[key]


def seed_endpoints():
    from auth.drivers.root import bp
    current_app.register_blueprint(bp, url_prefix=current_app.config["endpoints"]["root"])
    if "oidc" in current_app.config:
        from auth.drivers.oidc import bp
        current_app.register_blueprint(bp, url_prefix=current_app.config["endpoints"]["oidc"])


def create_app():
    app = Flask(__name__)
    app.config["SESSION_COOKIE_NAME"] = "auth"
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
    with app.app_context():
        read_config()
        seed_endpoints()
    return app


def main():
    create_app().run(host=APP_HOST, port=APP_PORT, debug=True)


if __name__ == "__main__":
    main()
