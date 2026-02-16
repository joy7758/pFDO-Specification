from __future__ import annotations
from typing import Literal, Optional, Union
from pydantic import BaseModel, ConfigDict, Field
class Authentication(BaseModel):
    model_config = ConfigDict(extra='forbid')
    username: str
    password: str
class Authentication1(BaseModel):
    model_config = ConfigDict(extra='forbid')
    token: str
class Authentication2(BaseModel):
    model_config = ConfigDict(extra='forbid')
    key: str
class Attributes(BaseModel):
    input: str = Field(..., description='The PID or URI to be searched for.')
class ExtendedQueryRefRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    requestId: Optional[str] = Field(None, description='requestId: the identifier of the request provided by the client; shall be unique within a given DOIP session so clients can distinguish between DOIP service responses. The requestId shall be a string not exceeding 4096 bits.')
    clientId: Optional[str] = Field(None, description='clientId: the identifier of the client.')
    targetId: str = Field(..., description='targetId: the identifier of the DOIP service')
    operationId: Literal['Op.QueryRef'] = Field(..., description='operationId: the identifier of the operation to be performed.')
    authentication: Optional[Union[Authentication, Authentication1, Authentication2]] = Field(None, description='authentication: optional JSON object used by clients to authenticate.')
    attributes: Attributes = Field(..., description='attributes: mandatory JSON object to specify the input')