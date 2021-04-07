#     Copyright 2020 getcarrier.io
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.


from typing import Optional, List, Any

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
    members: Optional[List[Any]]


GroupRepresentation.update_forward_refs()
