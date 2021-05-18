from typing import Optional, List

from flask import session
from pylon.core.tools import log

from plugins.auth_manager.models.api_response_pd import ApiResponse
from plugins.auth_manager.models.group_pd import GroupRepresentation
from plugins.project.models.project import Project
from plugins.project_keycloak.invitation_handler import InvitationHandler
from plugins.project_keycloak.models.invitation_pd import InvitationModel
from plugins.project_keycloak.utils import current_user_id, RpcMixin


class KeycloakGroupsHandler(RpcMixin):
    REALM = 'carrier'
    SESSION_CACHE_KEY = 'project_keycloak_groups'

    MAIN_GROUP_NAME = 'owner'
    SUBGROUP_NAMES = ['maintainer', 'analyst', ]

    def __init__(self, project: Project):
        self.project = project

    @property
    def token(self):
        return self.rpc.call.auth_manager_get_token()

    @property
    def keycloak_groups_cached(self):
        try:
            return session[self.SESSION_CACHE_KEY]
        except KeyError:
            session[self.SESSION_CACHE_KEY] = self.project.keycloak_groups
        return session[self.SESSION_CACHE_KEY]

    @staticmethod
    def invalidate_cache():
        try:
            del session[KeycloakGroupsHandler.SESSION_CACHE_KEY]
        except KeyError:
            ...

    def _search_main_group(self) -> Optional[str]:
        log.debug('Getting id using search method')
        response = self.rpc.call.auth_manager_get_groups(
            realm=self.REALM,
            token=self.token,
            search=self.project.id,
            with_members=False
        )
        if response.success:
            for found_group in response.data:
                if str(found_group.name) == str(self.project.id):
                    self._refresh_main_group_from_keycloak(found_group)
                    return self.get_group_id(self.MAIN_GROUP_NAME)
        log.warning(f'Group for project {self.project.name} is not found in keycloak')
        return None

    def update(self):
        self.invalidate_cache()
        super(Project, self.project).commit()

    def _refresh_main_group_from_keycloak(self, group_data: GroupRepresentation) -> None:
        self.project.keycloak_groups[self.MAIN_GROUP_NAME] = group_data.id
        for subgroup in group_data.subGroups:
            self.map_group_by_id(subgroup.name, subgroup.id, commit=False)
        self.update()

    def get_group_id(self, group_name: str, recursion_prevent: bool = False) -> str:
        try:
            return self.keycloak_groups_cached[group_name]
        except KeyError:
            if group_name == self.MAIN_GROUP_NAME:
                if not self._search_main_group():
                    self.create_main_group()
                    return self.get_group_id(group_name, recursion_prevent=True)
            else:
                self.update_group_info()
                try:
                    self.keycloak_groups_cached[group_name]
                except KeyError:
                    if recursion_prevent:
                        log.critical(f'Recursion on creating subgroup {group_name}')
                        raise RecursionError(f'Recursion on creating subgroup {group_name}')
                    return self.create_subgroup(group_name)

    def update_group_info(self) -> bool:
        response = self.rpc.call.auth_manager_get_groups(
            realm=self.REALM,
            token=self.token,
            with_members=False,
            group_or_id=self.get_group_representation_offline(),
            # response_debug_processor=lambda r: r.url
        )
        if response.success:
            self._refresh_main_group_from_keycloak(response.data)
        else:
            log.critical(f'Error updating group info {response.error}')
        return response.success

    def create_main_group(self) -> ApiResponse:
        response = self.rpc.call.auth_manager_post_group(
            realm=self.REALM,
            token=self.token,
            group=self.get_group_representation_offline(str(self.project.id)),
        )
        if response.success:
            log.debug(f'Group {response.data.id} for project {self.project.name} successfully created')
            self.map_group_by_id(self.MAIN_GROUP_NAME, response.data.id)
            self.add_current_user_to_groups([self.get_group_id(self.MAIN_GROUP_NAME)])
        return response

    def create_subgroup(self, name: str) -> Optional[str]:
        response = self.rpc.call.auth_manager_add_subgroup(
            realm=self.REALM,
            token=self.token,
            parent=self.get_group_representation_offline(),
            child=self.get_group_representation_offline(name),
        )
        if response.success:
            if response.status == 201:
                self.map_group_by_id(name, response.data.id)
        else:
            log.critical(f'Error creating subgroup {response.error}')
            return None
        return self.get_group_id(name, recursion_prevent=True)

    def get_group_representation_offline(self, keycloak_group_name: str = None, **kwargs) -> GroupRepresentation:
        is_main_group = not keycloak_group_name or keycloak_group_name == self.MAIN_GROUP_NAME
        repr_name = id_key = keycloak_group_name
        if is_main_group:
            repr_name, id_key = self.project.id, self.MAIN_GROUP_NAME
        group = GroupRepresentation(
            name=str(repr_name),
            attributes={'project_name': [self.project.name], self.MAIN_GROUP_NAME: [is_main_group]},
            **kwargs
        )
        try:
            group.id = self.keycloak_groups_cached[id_key]
        except KeyError:
            log.debug(f'Unable to get group ID for {keycloak_group_name} [{repr_name}]')
        return group

    def map_group_by_id(self, name: str, group_keycloak_id: str, commit: bool = True):
        self.project.keycloak_groups[name] = group_keycloak_id
        if commit:
            self.update()

    def add_current_user_to_groups(self, group_ids: List[str]) -> None:
        self.rpc.call.auth_manager_add_users_to_groups(
            realm=self.REALM,
            token=self.token,
            users=[current_user_id()],
            groups=group_ids,
        )

    def create_subgroups(self):
        for g in self.SUBGROUP_NAMES:
            self.create_subgroup(g)

    def new_invitation(self, invitation_data):
        return InvitationModel(
            project_id=self.project.id,
            groups=[self.get_group_representation_offline(invitation_data['group'])],
            email=invitation_data['email']
        )

    def send_invitations(self, invitations: list) -> None:
        invitations_handler = InvitationHandler()
        inv = None
        for i in sorted(invitations, key=lambda x: x['email']):
            if inv:
                if inv.check_email(i['email']):
                    inv.groups.append(self.get_group_representation_offline(i['group']))
                else:
                    invitations_handler.get_join_url(inv)
                    inv.create_send_task()
                    inv = self.new_invitation(i)
            else:
                inv = self.new_invitation(i)
        if inv:
            invitations_handler.get_join_url(inv)
            inv.create_send_task()
