from pydantic import BaseModel


class ArticleDetail(BaseModel):
    id: str
    title: str
    summary: str
    content: str
    source_url: str
    fetch_status: str
