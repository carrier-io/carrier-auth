from os import environ


environ["CORE_CONFIG_SEED"] = 'file:config/pylon-example.yml'
environ['PYLON_CONFIG_PATH'] = 'config/pylon-example.yml'
environ["CORE_DEVELOPMENT_MODE"] = 'true'
# environ["APP_HOST"] = 'http://172.25.0.10'
environ["CONFIG_FILENAME"] = './config/settings.yaml'

from pylon import main

main.main()
