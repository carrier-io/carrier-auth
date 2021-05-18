from functools import wraps
from typing import Optional

from pylon.core.tools import log


class KwargsRequiredError(Exception):
    _message = 'kwargs: {} are required to be set'

    def __init__(self, detail: Optional[tuple] = ''):
        super(KwargsRequiredError, self).__init__(self._message.format(detail))


def require_kwargs(*required_kwargs):
    def decor(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not all(i in kwargs for i in required_kwargs):
                raise KwargsRequiredError(required_kwargs)
            return func(*args, **kwargs)
        return wrapper
    return decor


require_auth_settings = require_kwargs('auth_settings')


def push_kwargs(**pushed_kwargs):
    def decor(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            intersections = set(kwargs.keys()).intersection(set(pushed_kwargs.keys()))
            # if any(i in kwargs for i in pushed_kwargs):
            if intersections:
                log.warning(
                    f'some pushed kwargs {intersections} intersect with explicit kwargs '
                    f'for func [{func.__module__}.{func.__name__}]. '
                    f'Using explicit by default'
                )
            pushed_kwargs.update(kwargs)
            return func(*args, **pushed_kwargs)
        return wrapper
    return decor
