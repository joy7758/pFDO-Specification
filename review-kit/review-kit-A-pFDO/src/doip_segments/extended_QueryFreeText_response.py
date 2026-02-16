from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, conint
class ExtendedQueryFreeTextResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')
    requestId: Optional[str] = Field(None, description='requestId: the identifier of the request to which this is a response. The DOIP service must include in its response the requestId provided by the client.')
    status: Literal['0.DOIP/Status.001'] = Field(..., description='status: an identifier that indicates the status of the request. Status codes shall have associated unique identifiers resolvable as specified in the IRP.')
    size: conint(ge=0) = Field(..., description='the number of results across all pages')
    results: List
class Element(BaseModel):
    id: Optional[str] = Field(None, description='id: identifier of the element; must be unique within a DO.')
    length: Optional[str] = Field(None, description='length of the data portion.')
    type: Optional[str] = Field(None, description='shall be a type as defined in this spec or a MIME type')
    attributes: Optional[Dict[str, Any]] = Field(None, description='one or more fields serialized as an object using the default serialization, or as a JSON (sub) object.')
class DoipDoSerialization(BaseModel):
    model_config = ConfigDict(extra='forbid')
    id: str = Field(..., description='id: the identifier of the DO.')
    type: str = Field(..., description='type: the DO type. Must be 0.TYPE/DO or its extension. See Types section.')
    attributes: Optional[Dict[str, Any]] = Field(None, description='attributes: one or more fields (key-value pairs) serialized as a JSON (sub) object.')
    elements: Optional[List[Element]] = Field(None, description='description: one or more elements serialized as an array in the default serialization, with each element consisting of')
    signatures: Optional[str] = Field(None, description='Required for DOs of type 0.TYPE/DOIPServiceInfo and 0.TYPE/DOIPOperation; otherwise optional. The field is an array of strings in the default serialization; each string is in JWS format19 with an unencoded detached payload.')