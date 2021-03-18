from os import environ


environ["CORE_CONFIG_SEED"] = 'file:config/pylon-example.yml'
environ["CORE_DEVELOPMENT_MODE"] = 'true'
environ["APP_HOST"] = 'http://127.0.0.1'

from pylon import main

main.main()
