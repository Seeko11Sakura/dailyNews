from pydantic import BaseModel


class ExploreRequest(BaseModel):
    selected_domains: list[str]
    seen_domain_ids: list[str]
    date: str


class ExploreCard(BaseModel):
    domain_id: str
    domain_name: str
    reason: str
    preview_titles: list[str]


class ExploreResponse(BaseModel):
    cards: list[ExploreCard]
