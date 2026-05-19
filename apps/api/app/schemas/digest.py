from pydantic import BaseModel


class DigestRequest(BaseModel):
    selected_domains: list[str]
    sort_preference: str
    date: str


class DigestItem(BaseModel):
    id: str
    domain_id: str
    title: str
    summary: str
    source: str
    published_at: str
    is_read: bool = False


class DigestGroup(BaseModel):
    domain_id: str
    items: list[DigestItem]


class DigestResponse(BaseModel):
    groups: list[DigestGroup]
