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

from pydantic import BaseModel

from plugins.auth_manager.models.group_pd import GroupRepresentation


class UserConsentRepresentation(BaseModel):
    clientId: Optional[str]
    createdDate: Optional[int]
    grantedClientScopes: Optional[List[str]]
    lastUpdatedDate: Optional[int]


class MultivaluedHashMap(BaseModel):
    empty: Optional[bool]
    loadFactor: Optional[float]
    threshold: Optional[int]


class CredentialRepresentation(BaseModel):
    algorithm: Optional[str]
    config: Optional[MultivaluedHashMap]
    counter: Optional[int]
    createdDate: Optional[int]
    device: Optional[str]
    digits: Optional[int]
    hashIterations: Optional[int]
    hashedSaltedValue: Optional[str]
    period: Optional[int]
    salt: Optional[str]
    temporary: Optional[bool]
    type: Optional[str]
    value: Optional[str]


class FederatedIdentityRepresentation(BaseModel):
    identityProvider: Optional[str]
    userId: Optional[str]
    userName: Optional[str]


class UserRepresentation(BaseModel):
    access: Optional[dict]
    attributes: Optional[dict]
    clientConsents: Optional[List[UserConsentRepresentation]]
    clientRoles: Optional[dict]
    createdTimestamp: Optional[int]
    credentials: Optional[List[CredentialRepresentation]]
    disableableCredentialTypes: Optional[List[str]]
    email: Optional[str]
    emailVerified: Optional[bool]
    enabled: Optional[bool]
    federatedIdentities: Optional[List[FederatedIdentityRepresentation]]
    federationLink: Optional[str]
    firstName: Optional[str]
    groups: Optional[List[Any]]
    id: Optional[str]
    lastName: Optional[str]
    notBefore: Optional[int]
    origin: Optional[str]
    realmRoles: Optional[List[str]]
    requiredActions: Optional[List[str]]
    self: Optional[str]
    serviceAccountClientId: Optional[str]
    username: Optional[str]
