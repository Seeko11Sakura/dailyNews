"""
Title normalization and near-duplicate folding.

Groups articles with similar titles (from different sources covering the same
event) so the digest shows each story once, not N copies.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from difflib import SequenceMatcher
from typing import Any

# Bracket / decoration pairs commonly wrapping prefixes or suffixes in CJK titles.
_BRACKET_PAIRS: list[tuple[str, str]] = [
    ("【", "】"),  # 【】
    ("[", "]"),
    ("（", "）"),  # （）
    ("(", ")"),
    ("［", "］"),  # ［］
]

# Build a regex that matches any bracket pair content at start or end of title.
_BRACKET_RE = re.compile(
    "|".join(
        rf"(?:{re.escape(l)}.*?{re.escape(r)})"
        for l, r in _BRACKET_PAIRS
    )
)

# Collapse runs of whitespace (including full-width space 　).
_WHITESPACE_RE = re.compile(r"[\s　]+")


def normalize_title(title: str) -> str:
    """Normalize a title for similarity comparison.

    Steps:
    1. Unicode NFKC normalization (full-width -> half-width, etc.)
    2. Strip bracket-wrapped prefixes/suffixes (【...】, [...], etc.)
    3. Remove all punctuation (Unicode category starts with P)
    4. Collapse whitespace to single space
    5. Lowercase
    6. Strip leading/trailing whitespace
    """
    # NFKC: fold full-width chars, compatibility chars
    text = unicodedata.normalize("NFKC", title)

    # Remove bracket-wrapped segments at start or end
    prev = None
    while prev != text:
        prev = text
        text = _BRACKET_RE.sub("", text).strip()

    # Remove punctuation (Unicode category P)
    text = "".join(ch for ch in text if not unicodedata.category(ch).startswith("P"))

    # Collapse whitespace
    text = _WHITESPACE_RE.sub(" ", text).strip()

    return text.lower()


def title_similarity(title1: str, title2: str) -> float:
    """Return similarity ratio between two titles (0.0 to 1.0).

    Uses SequenceMatcher on normalized titles so that minor wording
    differences or extra words don't block a match.
    """
    norm1 = normalize_title(title1)
    norm2 = normalize_title(title2)

    if not norm1 and not norm2:
        return 1.0
    if not norm1 or not norm2:
        return 0.0

    return SequenceMatcher(None, norm1, norm2).ratio()


def title_hash(title: str) -> str:
    """Return MD5 hex digest of the normalized title."""
    return hashlib.md5(normalize_title(title).encode("utf-8")).hexdigest()


def find_similar_articles(
    articles: list[dict[str, Any]],
    threshold: float = 0.8,
) -> list[list[dict[str, Any]]]:
    """Group articles whose titles are >= threshold similar.

    Uses single-pass clustering: each article is compared against the first
    (representative) article in each existing group.  This is O(n * k) where
    k is the number of groups -- acceptable for typical feed sizes (< 1000).

    Returns a list of groups, each group being a list of article dicts.
    Articles with no close match end up in their own single-element group.
    """
    groups: list[list[dict[str, Any]]] = []

    for article in articles:
        matched = False
        for group in groups:
            # Compare against the group representative (first article)
            if title_similarity(article["title"], group[0]["title"]) >= threshold:
                group.append(article)
                matched = True
                break

        if not matched:
            groups.append([article])

    return groups


def fold_similar_titles(articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Fold near-duplicate articles by title similarity.

    For each group of similar articles:
    - Keep the "best" article as primary (longest content, then most recent)
    - Add `similar_count` field (number of similar articles including itself)
    - Set `is_duplicate = False` on the primary
    - Set `is_duplicate = True` on the rest

    Returns the processed list (all articles, not just primaries).
    The caller can filter by `is_duplicate` if only primaries are wanted.
    """
    groups = find_similar_articles(articles)
    result: list[dict[str, Any]] = []

    for group in groups:
        # Sort: prefer longest content, then most recent publish time
        group.sort(
            key=lambda a: (
                len(a.get("content") or ""),
                a.get("published_at") or "",
            ),
            reverse=True,
        )

        primary = group[0]
        primary["similar_count"] = len(group)
        primary["is_duplicate"] = False
        result.append(primary)

        for dup in group[1:]:
            dup["similar_count"] = len(group)
            dup["is_duplicate"] = True
            result.append(dup)

    return result


# ---------------------------------------------------------------------------
# Inline smoke tests
# ---------------------------------------------------------------------------

def _run_tests() -> None:
    # --- normalize_title ---
    assert normalize_title("  Hello,  World!  ") == "hello world"
    assert normalize_title("【快讯】AI大模型新突破") == "ai大模型新突破"
    assert normalize_title("[深度] Some　Title！") == "some title"

    # --- title_similarity ---
    sim1 = title_similarity("AI大模型新突破", "AI大模型取得新突破")
    assert sim1 > 0.8, f"expected > 0.8, got {sim1}"

    sim2 = title_similarity("AI大模型新突破", "游戏行业报告")
    assert sim2 < 0.3, f"expected < 0.3, got {sim2}"

    # Edge cases
    assert title_similarity("", "") == 1.0
    assert title_similarity("abc", "") == 0.0

    # --- title_hash ---
    assert len(title_hash("any title")) == 32
    assert title_hash("Hello!") == title_hash("hello")  # punctuation stripped, lowercased

    # --- find_similar_articles ---
    sample = [
        {"title": "AI大模型新突破", "content": "A" * 50, "published_at": "2026-05-23"},
        {"title": "AI大模型取得新突破", "content": "B" * 30, "published_at": "2026-05-22"},
        {"title": "游戏行业报告", "content": "C" * 20, "published_at": "2026-05-23"},
    ]
    groups = find_similar_articles(sample, threshold=0.8)
    assert len(groups) == 2, f"expected 2 groups, got {len(groups)}"
    # First group should have 2 similar AI articles
    assert len(groups[0]) == 2

    # --- fold_similar_titles ---
    folded = fold_similar_titles(sample)
    # The first AI article (longer content) should be primary
    ai_primary = [a for a in folded if "ai" in normalize_title(a["title"]) and not a["is_duplicate"]][0]
    assert ai_primary["similar_count"] == 2
    assert len(ai_primary["content"]) == 50  # longest content wins

    # The other AI article should be marked duplicate
    ai_dup = [a for a in folded if "ai" in normalize_title(a["title"]) and a["is_duplicate"]][0]
    assert ai_dup["similar_count"] == 2

    # Game report is not a duplicate
    game = [a for a in folded if "游戏" in a["title"]][0]
    assert not game["is_duplicate"]
    assert game["similar_count"] == 1

    print("title_folder: all tests passed")


if __name__ == "__main__":
    _run_tests()
