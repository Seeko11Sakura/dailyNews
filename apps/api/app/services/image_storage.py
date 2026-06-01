"""文章图片存储：下载原站图片，上传到 Supabase Storage，并记录图片关系。"""

from __future__ import annotations

import hashlib
import logging
import os
from collections.abc import Callable
from pathlib import PurePosixPath
from typing import Any
from urllib.parse import quote, urlparse

import httpx

from app.repositories.base import get_supabase

logger = logging.getLogger(__name__)

_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)

_DEFAULT_BUCKET = "article-images"
_DEFAULT_MAX_PER_ARTICLE = 1
_DEFAULT_MAX_BYTES = 5 * 1024 * 1024
_IMAGE_EXTENSIONS = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}


def _image_bucket() -> str:
    """读取文章图片 bucket 名称。"""
    return os.getenv("ARTICLE_IMAGE_BUCKET", _DEFAULT_BUCKET)


def _supabase_url() -> str:
    """读取 Supabase 项目地址。"""
    return os.getenv("SUPABASE_URL", "").rstrip("/")


def _service_role_key() -> str:
    """读取 Supabase 服务端密钥。"""
    return os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")


def _max_images_per_article() -> int:
    """读取每篇文章最多保存的图片数量。"""
    raw_value = os.getenv("ARTICLE_IMAGE_MAX_PER_ARTICLE")
    if not raw_value:
        return _DEFAULT_MAX_PER_ARTICLE
    try:
        return max(1, int(raw_value))
    except ValueError:
        return _DEFAULT_MAX_PER_ARTICLE


def _max_image_bytes() -> int:
    """读取单张图片最大字节数。"""
    raw_value = os.getenv("ARTICLE_IMAGE_MAX_BYTES")
    if not raw_value:
        return _DEFAULT_MAX_BYTES
    try:
        return max(1024, int(raw_value))
    except ValueError:
        return _DEFAULT_MAX_BYTES


def _unique_urls(image_urls: list[str]) -> list[str]:
    """按顺序去重图片地址。"""
    seen: set[str] = set()
    result: list[str] = []
    for url in image_urls:
        if not url or url in seen:
            continue
        seen.add(url)
        result.append(url)
    return result


def _extension_for_image(url: str, content_type: str) -> str:
    """根据内容类型或 URL 推断图片后缀。"""
    if content_type in _IMAGE_EXTENSIONS:
        return _IMAGE_EXTENSIONS[content_type]

    suffix = PurePosixPath(urlparse(url).path).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
        return ".jpg" if suffix == ".jpeg" else suffix

    return ".jpg"


def _storage_path(article_id: str, image_url: str, index: int, content_type: str) -> str:
    """生成稳定的 Storage 文件路径。"""
    digest = hashlib.sha256(image_url.encode("utf-8")).hexdigest()[:16]
    extension = _extension_for_image(image_url, content_type)
    return f"articles/{article_id}/{index:02d}-{digest}{extension}"


def _download_image(
    image_url: str,
    http_get: Callable[..., Any],
) -> tuple[bytes, str] | None:
    """下载图片并校验大小和类型。"""
    response = http_get(
        image_url,
        headers={"User-Agent": _USER_AGENT},
        timeout=15.0,
        follow_redirects=True,
    )
    response.raise_for_status()

    content_type = response.headers.get("content-type", "").split(";")[0].lower()
    if not content_type.startswith("image/"):
        return None

    content_length = response.headers.get("content-length")
    max_bytes = _max_image_bytes()
    if content_length and int(content_length) > max_bytes:
        return None

    content = response.content
    if not content or len(content) > max_bytes:
        return None

    return content, content_type


def _public_url(bucket: Any, path: str) -> str:
    """获取 Supabase Storage 公共访问地址。"""
    value = bucket.get_public_url(path)
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return str(value.get("publicUrl") or value.get("public_url") or "")
    return str(value or "")


def _public_storage_url(bucket_name: str, path: str) -> str:
    """拼出公开 bucket 的访问地址。"""
    base_url = _supabase_url()
    encoded_path = "/".join(quote(part) for part in path.split("/"))
    return f"{base_url}/storage/v1/object/public/{bucket_name}/{encoded_path}"


def _upload_with_service_key(
    bucket_name: str,
    path: str,
    content: bytes,
    content_type: str,
) -> str | None:
    """用服务端密钥直接上传图片，兼容新版 sb_secret key。"""
    base_url = _supabase_url()
    key = _service_role_key()
    if not base_url or not key:
        return None

    encoded_path = "/".join(quote(part) for part in path.split("/"))
    response = httpx.post(
        f"{base_url}/storage/v1/object/{bucket_name}/{encoded_path}",
        headers={
            "Authorization": f"Bearer {key}",
            "apikey": key,
            "Content-Type": content_type,
            "cache-control": "31536000",
            "x-upsert": "true",
        },
        content=content,
        timeout=30.0,
    )
    response.raise_for_status()
    return _public_storage_url(bucket_name, path)


def _upload_image(
    bucket: Any,
    bucket_name: str,
    path: str,
    content: bytes,
    content_type: str,
    *,
    direct_upload: bool = True,
) -> str:
    """上传图片并返回公开访问地址。"""
    if direct_upload and _service_role_key().startswith("sb_secret_"):
        public_url = _upload_with_service_key(bucket_name, path, content, content_type)
        if public_url:
            return public_url

    bucket.upload(
        path,
        content,
        file_options={
            "content-type": content_type,
            "cache-control": "31536000",
            "x-upsert": "true",
        },
    )
    return _public_url(bucket, path)


def store_article_images(
    article_id: str,
    image_urls: list[str],
    *,
    supabase: Any | None = None,
    http_get: Callable[..., Any] | None = None,
) -> list[dict[str, Any]]:
    """保存文章图片并返回已写入的图片记录。"""
    if not article_id or not image_urls:
        return []

    client = supabase or get_supabase()
    fetch = http_get or httpx.get
    direct_upload = http_get is None
    bucket_name = _image_bucket()
    bucket = client.storage.from_(bucket_name)
    stored_records: list[dict[str, Any]] = []

    for index, image_url in enumerate(_unique_urls(image_urls)[: _max_images_per_article()]):
        try:
            downloaded = _download_image(image_url, fetch)
            if downloaded is None:
                continue
            content, content_type = downloaded
            path = _storage_path(article_id, image_url, index, content_type)

            public_url = _upload_image(
                bucket,
                bucket_name,
                path,
                content,
                content_type,
                direct_upload=direct_upload,
            )

            record = {
                "article_id": article_id,
                "original_url": image_url,
                "storage_path": path,
                "public_url": public_url,
                "sort_order": index,
                "mime_type": content_type,
                "size_bytes": len(content),
            }
            client.table("article_images").insert(record).execute()
            stored_records.append(record)
        except Exception as exc:
            logger.warning("Failed to store article image %s: %s", image_url, exc)

    return stored_records
