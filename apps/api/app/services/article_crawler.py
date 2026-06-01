"""文章爬虫预览：从单篇原文页提取标题、正文和图片地址。"""

from __future__ import annotations

import json
import logging
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup, Tag

from app.services.article_content import extract_article_content

logger = logging.getLogger(__name__)

_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)

_IMAGE_ROOT_SELECTORS = [
    "article",
    "[itemprop='articleBody']",
    ".c-article-content",
    ".article-content",
    ".entry-content",
    ".post-content",
    ".content",
    ".article",
]

_IMAGE_ATTRS = ["data-src", "data-original", "data-lazy-src", "data-url", "src"]


def _clean_title(value: str | None) -> str:
    """清理标题中的多余空白。"""
    if not value:
        return ""
    return " ".join(value.split()).strip()


def _meta_content(soup: BeautifulSoup, key: str) -> str:
    """读取指定 meta 字段的内容。"""
    tag = soup.find("meta", attrs={"property": key}) or soup.find(
        "meta", attrs={"name": key}
    )
    if not isinstance(tag, Tag):
        return ""
    content = tag.get("content")
    return _clean_title(content if isinstance(content, str) else "")


def _json_ld_objects(soup: BeautifulSoup) -> list[dict[str, object]]:
    """读取页面中的 JSON-LD 结构化数据。"""
    objects: list[dict[str, object]] = []
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw_text = script.string or script.get_text("", strip=True)
        if not raw_text:
            continue
        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError:
            continue

        if isinstance(data, dict):
            graph = data.get("@graph")
            if isinstance(graph, list):
                objects.extend(item for item in graph if isinstance(item, dict))
            objects.append(data)
        elif isinstance(data, list):
            objects.extend(item for item in data if isinstance(item, dict))
    return objects


def _extract_title(soup: BeautifulSoup) -> str:
    """从常见位置提取文章标题。"""
    for key in ["og:title", "twitter:title"]:
        title = _meta_content(soup, key)
        if title:
            return title

    h1 = soup.find("h1")
    if isinstance(h1, Tag):
        title = _clean_title(h1.get_text(" ", strip=True))
        if title:
            return title

    if soup.title:
        return _clean_title(soup.title.get_text(" ", strip=True))

    return ""


def _extract_published_at(soup: BeautifulSoup) -> str:
    """从 meta、JSON-LD 或 time 标签提取发布时间。"""
    for key in [
        "article:published_time",
        "og:published_time",
        "pubdate",
        "publishdate",
        "date",
        "datePublished",
    ]:
        value = _meta_content(soup, key)
        if value:
            return value

    for item in _json_ld_objects(soup):
        for key in ("datePublished", "dateCreated", "dateModified"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

    time_tag = soup.find("time")
    if isinstance(time_tag, Tag):
        value = time_tag.get("datetime") or time_tag.get("pubdate")
        if isinstance(value, str) and value.strip():
            return value.strip()
        text = _clean_title(time_tag.get_text(" ", strip=True))
        if text:
            return text

    return ""


def _normalize_image_url(raw_url: str | None, base_url: str) -> str:
    """把图片地址整理成完整 URL。"""
    if not raw_url:
        return ""
    value = raw_url.strip()
    if not value or value.startswith(("data:", "blob:", "javascript:")):
        return ""
    absolute_url = urljoin(base_url, value)
    parsed = urlparse(absolute_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ""
    return absolute_url


def _looks_like_content_image(url: str) -> bool:
    """过滤明显不是正文主图的图片地址。"""
    if not url:
        return False
    lowered = url.lower()
    blocked = ("logo", "avatar", "icon", "qrcode", "qr-code", "sprite", "loading")
    return not any(word in lowered for word in blocked)


def _src_from_srcset(value: str | None) -> str:
    """从 srcset 中取第一张图片地址。"""
    if not value:
        return ""
    first = value.split(",")[0].strip()
    return first.split(" ")[0].strip()


def _image_url_from_tag(tag: Tag, base_url: str) -> str:
    """从图片节点读取可用的图片地址。"""
    for attr in _IMAGE_ATTRS:
        raw = tag.get(attr)
        if isinstance(raw, str):
            url = _normalize_image_url(raw, base_url)
            if url:
                return url

    srcset = tag.get("srcset") or tag.get("data-srcset")
    if isinstance(srcset, str):
        return _normalize_image_url(_src_from_srcset(srcset), base_url)

    return ""


def _extract_json_ld_images(soup: BeautifulSoup, base_url: str) -> list[str]:
    """从 JSON-LD 中提取图片地址。"""
    image_urls: list[str] = []
    for item in _json_ld_objects(soup):
        image = item.get("image")
        values = image if isinstance(image, list) else [image]

        for value in values:
            raw_url = ""
            if isinstance(value, str):
                raw_url = value
            elif isinstance(value, dict):
                nested_url = value.get("url")
                raw_url = nested_url if isinstance(nested_url, str) else ""
            url = _normalize_image_url(raw_url, base_url)
            if _looks_like_content_image(url):
                _append_unique(image_urls, url)
    return image_urls


def _append_unique(items: list[str], value: str) -> None:
    """按原顺序追加不重复的值。"""
    if value and value not in items:
        items.append(value)


def _extract_image_urls(soup: BeautifulSoup, base_url: str) -> list[str]:
    """从正文区域提取图片地址。"""
    image_urls: list[str] = []

    for key in ["og:image", "twitter:image"]:
        url = _normalize_image_url(_meta_content(soup, key), base_url)
        if _looks_like_content_image(url):
            _append_unique(image_urls, url)

    for url in _extract_json_ld_images(soup, base_url):
        _append_unique(image_urls, url)

    roots = [tag for selector in _IMAGE_ROOT_SELECTORS for tag in soup.select(selector)]
    if not roots:
        roots = [soup]

    for root in roots:
        for image in root.select("img"):
            url = _image_url_from_tag(image, base_url)
            if _looks_like_content_image(url):
                _append_unique(image_urls, url)

    return image_urls[:20]


def extract_article_preview(html: str, base_url: str) -> dict[str, object]:
    """从 HTML 中提取文章预览信息。"""
    soup = BeautifulSoup(html, "html.parser")
    content = extract_article_content(html)

    return {
        "title": _extract_title(soup),
        "content": content,
        "published_at": _extract_published_at(soup),
        "image_urls": _extract_image_urls(soup, base_url),
    }


def crawl_article(url: str) -> dict[str, object]:
    """打开单篇文章并返回抓取预览，不写入数据库。"""
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("文章地址必须是 http 或 https 链接")

    response = httpx.get(
        url,
        headers={"User-Agent": _USER_AGENT},
        timeout=15.0,
        follow_redirects=True,
    )
    response.raise_for_status()

    final_url = str(response.url)
    preview = extract_article_preview(response.text, final_url)
    preview["url"] = final_url
    preview["content_length"] = len(str(preview["content"]))
    return preview
