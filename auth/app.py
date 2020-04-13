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
from flask_session import Session

from auth.config import Config
from auth.utils import config


def read_config():  # Reading the config file
    settings_file = Config.CONFIG_FILENAME
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
    current_app.config["keys"] = []
    for key in Config.AUTH_PROXIES:
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
    app_session = Session()
    app = Flask(__name__)

    # Application Configuration
    app.config.from_object(Config)

    # Initialize Plugins
    app_session.init_app(app)

    with app.app_context():
        read_config()
        seed_endpoints()
    return app


def main():
    create_app().run(host=Config.APP_HOST, port=Config.APP_PORT, debug=True)


if __name__ == "__main__":
    main()
