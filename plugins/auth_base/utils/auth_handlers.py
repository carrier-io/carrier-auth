from flask import make_response
from pylon.core.tools import log

from plugins.auth_base.config import Singleton
from typing import Callable


class AuthHandler(dict, metaclass=Singleton):
    def __setitem__(self, key: str, value: Callable):
        lowered = key.lower()
        if lowered in self:
            log.warning(f'AuthHandler overwritten for key: {lowered}')
        super().__setitem__(lowered, value)

    def __getitem__(self, item: str):
        print('GETTING ITEM FROM HANDLER')
        log.debug('GETTING ITEM FROM HANDLER')
        result = super().__getitem__(item.lower())
        if not result:
            return make_response("KO", 401)
        return result
