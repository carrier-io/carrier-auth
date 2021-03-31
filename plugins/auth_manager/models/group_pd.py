from typing import Optional, List

from pydantic.main import BaseModel


class GroupRepresentation(BaseModel):
    access: Optional[dict]
    attributes: Optional[dict]
    clientRoles: Optional[dict]
    id: Optional[str]
    name: Optional[str]
    path: Optional[str]
    realmRoles: Optional[List[str]]
    subGroups: Optional[List['GroupRepresentation']]


GroupRepresentation.update_forward_refs()

# Request
# URL: http: // localhost: 8080 / auth / admin / realms / {realm} / users / {userId} / groups / {groupId}
# Request
# Method: PUT
#  https://documenter.getpostman.com/view/7294517/SzmfZHnd