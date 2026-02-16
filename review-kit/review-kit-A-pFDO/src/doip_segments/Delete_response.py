from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field
class DeleteResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')
    requestId: Optional[str] = Field(None, description='requestId: the identifier of the request to which this is a response. The DOIP service must include in its response the requestId provided by the client.')
    status: Literal['0.DOIP/Status.001'] = Field(..., description='status: an identifier that indicates the status of the request. Status codes shall have associated unique identifiers resolvable as specified in the IRP.')
    output: Optional[str] = Field(None, description='arbitrary information returned to the client')