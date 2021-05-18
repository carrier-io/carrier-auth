import uuid
from os import getenv
from typing import Union

from flask import url_for
from redis import Redis

from plugins.project_keycloak.models.invitation_pd import InvitationModel


class InvitationHandler:
    REDIS_DB = 7
    PREFIX = 'join_url'
    DELIMITER = ':'
    EXPIRE = 60 * 60

    _redis_client = None

    def __init__(self):
        self.redis_host = getenv('REDIS_HOST')
        self.redis_port = getenv('REDIS_PORT', 6379)
        self.redis_user = getenv('REDIS_USER', '')
        self.redis_password = getenv('REDIS_PASSWORD')

    @property
    def redis_client(self) -> Redis:
        if self._redis_client:
            return self._redis_client
        self._redis_client = Redis(
            host=self.redis_host, port=self.redis_port,
            db=self.REDIS_DB,
            username=self.redis_user,
            password=self.redis_password,
        )
        return self._redis_client

    def __del__(self):
        try:
            self._redis_client.close()
        except AttributeError:
            pass

    def get_key(self, uid):
        return f'{self.PREFIX}{self.DELIMITER}{uid}'

    def get_join_url(self, invitation_data: InvitationModel) -> str:
        uid = uuid.uuid4()
        key = self.get_key(uid)
        invitation_data.url = url_for('project_keycloak.project_join', url_id=uid)
        with self.redis_client as redis_client:
            redis_client.set(key, invitation_data.json(), self.EXPIRE)
        return invitation_data.url

    def load(self, uid: str) -> InvitationModel:
        key = f'{self.PREFIX}{self.DELIMITER}{uid}'
        with self.redis_client as redis_client:
            inv_data = redis_client.get(key)
            inv_data = InvitationModel.parse_raw(inv_data, content_type='json')
            return inv_data

    def invalidate(self, uid: str) -> None:
        with self.redis_client as redis_client:
            redis_client.delete(self.get_key(uid))

    @staticmethod
    def tmp_invite(invitation_data: Union[InvitationModel, dict]):
        if isinstance(invitation_data, dict):
            invitation_data = InvitationModel.parse_obj(invitation_data)
        from pathlib import Path
        folder_path = Path(Path().cwd(), 'tmp', 'emails', str(invitation_data.project_id))
        folder_path.mkdir(parents=True, exist_ok=True)
        file_path = Path(folder_path, f'{invitation_data.email}.txt')
        file_path.write_text(
            f'This is an invitational email for project: {invitation_data.project_id}'
            f'\tfor groups:\t {[i.name for i in invitation_data.groups]}\n'
            f'\t{getenv("APP_HOST")}{getenv("APP_PORT", ":8080")}{invitation_data.url}'
        )
