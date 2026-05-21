from pydantic import BaseModel, Field
from pydantic import field_validator

from app.domain_catalog import DomainId


class ExploreRequest(BaseModel):
    selected_domains: list[DomainId] = Field(min_length=1, max_length=5)
    seen_domain_ids: list[DomainId] = Field(default_factory=list)
    date: str

    @field_validator("selected_domains", "seen_domain_ids")
    @classmethod
    def domain_lists_must_be_unique(
        cls, domain_ids: list[DomainId]
    ) -> list[DomainId]:
        if len(set(domain_ids)) != len(domain_ids):
            raise ValueError("domain lists must not contain duplicates")
        return domain_ids


class ExploreCard(BaseModel):
    domain_id: DomainId
    domain_name: str
    reason: str
    preview_titles: list[str] = Field(min_length=1, max_length=3)


class ExploreResponse(BaseModel):
    cards: list[ExploreCard]
