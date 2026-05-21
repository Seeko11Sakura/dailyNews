from pydantic import BaseModel

from app.domain_catalog import DomainId


class Domain(BaseModel):
    id: DomainId
    name: str
    emoji: str
