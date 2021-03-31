from os import environ
import socket


environ["CORE_CONFIG_SEED"] = 'file:config/pylon.yml'
environ['PYLON_CONFIG_PATH'] = './config/pylon.yml'
environ["CORE_DEVELOPMENT_MODE"] = 'true'
# environ["APP_HOST"] = f'http://172.19.0.9'
environ["APP_HOST"] = f'http://{socket.gethostbyname("traefik")}'
# environ["APP_HOST"] = f'http://192.168.88.113'
# docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' carrierauth_auth_1
# environ["CONFIG_FILENAME"] = './config/auth_settings.yaml'

from pylon import main

main.main()
