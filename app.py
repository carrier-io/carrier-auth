from os import environ
import socket


environ["CORE_DEVELOPMENT_MODE"] = 'true'
environ["CORE_DEBUG_LOGGING"] = 'true'
environ["APP_HOST"] = f'http://{socket.gethostbyname("traefik")}'


from pylon import main

main.main()
