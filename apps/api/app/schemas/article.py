from pydantic import BaseModel


class ArticleDetail(BaseModel):
    id: str
    title: str
    summary: str
    content: str
    source_url: str
    cover_image_url: str | None = None
    fetch_status: str
