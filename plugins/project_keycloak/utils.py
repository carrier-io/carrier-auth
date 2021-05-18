from flask import session, current_app
from pylon.core.tools.rpc import RpcManager


def current_user_id() -> str:
    return session['auth_attributes']['sub']


def current_user_email() -> str:
    return session['auth_attributes']['email']


class RpcMixin:
    _rpc = None

    @classmethod
    def set_rpc_manager(cls, rpc_manager: RpcManager):
        cls._rpc = rpc_manager

    @property
    def rpc(self):
        if not self._rpc:
            self.set_rpc_manager(current_app.config['CONTEXT'].rpc_manager)
        return self._rpc

    @rpc.setter
    def rpc(self, rpc_manager: RpcManager):
        self.set_rpc_manager(rpc_manager)
