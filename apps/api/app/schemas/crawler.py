"""爬虫接口的数据结构，供路由层和前端调试使用。"""

from pydantic import BaseModel


class ArticleCrawlRequest(BaseModel):
    """单篇文章抓取请求。"""

    url: str


class ArticleCrawlResponse(BaseModel):
    """单篇文章抓取结果。"""

    url: str
    title: str
    content: str
    published_at: str = ""
    image_urls: list[str]
    content_length: int
