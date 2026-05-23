"""
URL normalization and hashing for article deduplication.

Deterministic: same logical URL always produces the same hash,
regardless of tracking params, scheme differences, or trailing slashes.
"""

from __future__ import annotations

import hashlib
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

# Query parameters stripped during normalization (tracking / attribution).
_TRACKING_PARAMS: frozenset[str] = frozenset(
    {
        # UTM family
        "utm_source",
        "utm_medium",
        "utm_campaign",
        "utm_term",
        "utm_content",
        "utm_id",
        "utm_source_platform",
        "utm_creative_format",
        "utm_marketing_tactic",
        # Click identifiers
        "fbclid",
        "gclid",
        "dclid",
        "msclkid",
        "twclid",
        "wbraid",
        "gbraid",
        # Generic attribution
        "ref",
        "source",
        "campaign",
    }
)


def normalize_url(url: str) -> str:
    """Normalize a URL for deduplication.

    Steps:
    1. Force scheme to https
    2. Lowercase host, strip www. prefix
    3. Strip trailing slash from path (unless root "/")
    4. Remove tracking query parameters
    5. Sort remaining query parameters alphabetically
    6. Drop fragment (#...)
    """
    parsed = urlparse(url)

    # Scheme -> https
    scheme = "https"

    # Host normalization
    hostname = (parsed.hostname or "").lower()
    if hostname.startswith("www."):
        hostname = hostname[4:]

    # Path: strip trailing slash (but keep "/" for bare host)
    path = parsed.path.rstrip("/") or "/"

    # Query params: remove tracking, sort remainder
    params = parse_qs(parsed.query, keep_blank_values=True)
    cleaned = {
        k: v
        for k, v in params.items()
        if k.lower() not in _TRACKING_PARAMS
    }
    # Sort by key; urlencode handles list values deterministically
    query = urlencode(sorted(cleaned.items()), doseq=True)

    # Rebuild without fragment or port (port is implicit for 443)
    return urlunparse((scheme, hostname, path, "", query, ""))


def url_hash(url: str) -> str:
    """Return the MD5 hex digest of the normalized URL."""
    return hashlib.md5(normalize_url(url).encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Inline smoke tests
# ---------------------------------------------------------------------------

def _run_tests() -> None:
    # URL normalization
    assert (
        normalize_url("https://example.com/article?utm_source=rss&id=123")
        == "https://example.com/article?id=123"
    ), f"got: {normalize_url('https://example.com/article?utm_source=rss&id=123')}"

    assert (
        normalize_url("http://www.example.com/path/")
        == "https://example.com/path"
    ), f"got: {normalize_url('http://www.example.com/path/')}"

    # Scheme upgrade
    assert normalize_url("http://example.com").startswith("https://")

    # www stripping
    assert "www." not in normalize_url("https://www.example.com/page")

    # Fragment removal
    assert "#" not in normalize_url("https://example.com/page#section1")

    # Multiple tracking params
    result = normalize_url(
        "https://example.com/page?utm_source=a&utm_medium=b&key=val"
    )
    assert result == "https://example.com/page?key=val", f"got: {result}"

    # Deterministic hash length
    assert len(url_hash("https://example.com")) == 32

    # Determinism: same input -> same output
    assert url_hash("https://Example.COM/path/") == url_hash("https://example.com/path")

    print("url_normalizer: all tests passed")


if __name__ == "__main__":
    _run_tests()
