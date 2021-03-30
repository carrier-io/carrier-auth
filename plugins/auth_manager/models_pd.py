from typing import Optional, List

from pydantic import BaseModel


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
    groups: Optional[List[str]]
    id: Optional[str]
    lastName: Optional[str]
    notBefore: Optional[int]
    origin: Optional[str]
    realmRoles: Optional[List[str]]
    requiredActions: Optional[List[str]]
    self: Optional[str]
    serviceAccountClientId: Optional[str]
    username: Optional[str]


class User(BaseModel):
    realm: str
    rep: UserRepresentation

