from typing import Literal

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator

from app.domain_catalog import DomainId

SortPreference = Literal["freshness", "authority"]


class DigestRequest(BaseModel):
    selected_domains: list[DomainId] = Field(min_length=1, max_length=5)
    sort_preference: SortPreference
    date: str

    @field_validator("selected_domains")
    @classmethod
    def selected_domains_must_be_unique(
        cls, selected_domains: list[DomainId]
    ) -> list[DomainId]:
        if len(set(selected_domains)) != len(selected_domains):
            raise ValueError("selected_domains must not contain duplicates")
        return selected_domains


class DigestItem(BaseModel):
    id: str
    domain_id: DomainId
    title: str
    summary: str = Field(max_length=100)
    source: str
    published_at: str
    is_read: bool = False


class DigestGroup(BaseModel):
    domain_id: DomainId
    items: list[DigestItem]


class DigestResponse(BaseModel):
    groups: list[DigestGroup]
