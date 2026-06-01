from datetime import datetime, timedelta

from app.services.mock_repository import LOCAL_TZ, _resolve_digest_window


def test_digest_window_uses_latest_available_before_8am():
    now = datetime(2026, 5, 29, 7, 30, tzinfo=LOCAL_TZ)

    start_at, end_at = _resolve_digest_window("2026-05-29", now)

    assert start_at is None
    assert end_at == "2026-05-28T16:00:00+00:00"


def test_digest_window_uses_today_at_8am():
    now = datetime(2026, 5, 29, 8, 0, tzinfo=LOCAL_TZ)

    start_at, end_at = _resolve_digest_window("2026-05-29", now)

    assert start_at == "2026-05-28T16:00:00+00:00"
    assert end_at == "2026-05-29T16:00:00+00:00"


def test_digest_window_keeps_explicit_past_date():
    now = datetime(2026, 5, 29, 7, 30, tzinfo=LOCAL_TZ)
    yesterday = (now.date() - timedelta(days=1)).isoformat()

    start_at, end_at = _resolve_digest_window(yesterday, now)

    assert start_at == "2026-05-27T16:00:00+00:00"
    assert end_at == "2026-05-28T16:00:00+00:00"
