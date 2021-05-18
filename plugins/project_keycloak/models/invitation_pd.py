from os import getenv
from typing import List, Optional

from arbiter import Arbiter
from pydantic import BaseModel

from plugins.auth_manager.models.group_pd import GroupRepresentation


class InvitationModel(BaseModel):
    TASK_NAME = 'send_invitation'

    project_id: int
    email: str
    groups: List[GroupRepresentation]
    url: Optional[str] = None

    def check_email(self, email: str) -> bool:
        return self.email.lower() == email.lower()

    @property
    def arbiter(self):
        return Arbiter(
            host=getenv('RABBIT_HOST'), port=5672,
            user=getenv('RABBITMQ_USER'), password=getenv('RABBITMQ_PASSWORD')
        )

    def create_send_task(self) -> List[str]:
        if not self.url:
            raise AttributeError('URL must be specified')
        return self.arbiter.apply(
            self.TASK_NAME,
            task_args=[self.dict(exclude_unset=True, exclude_defaults=True)]
        )
