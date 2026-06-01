from app.services.mock_repository import _candidate_content_domains


def test_finance_only_uses_its_own_domain():
    candidates = _candidate_content_domains("finance")

    assert candidates == ["finance"]


def test_gadgets_does_not_borrow_technology_content():
    candidates = _candidate_content_domains("gadgets")

    assert candidates == ["gadgets"]


def test_supported_domain_uses_itself_first():
    candidates = _candidate_content_domains("technology")

    assert candidates[0] == "technology"
