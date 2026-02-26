from datetime import datetime
from models import NewsItem


def test_newsitem_creation():
    item = NewsItem(
        title="Test Title",
        url="https://example.com/test",
        source="test_source",
    )
    assert item.title == "Test Title"
    assert item.url == "https://example.com/test"
    assert item.source == "test_source"
    assert item.summary is None
    assert item.published_at is None
    assert item.tags == []
    assert isinstance(item.collected_at, datetime)


def test_newsitem_with_all_fields():
    now = datetime(2026, 2, 26, 10, 0, 0)
    item = NewsItem(
        title="Full Item",
        url="https://example.com/full",
        source="github",
        summary="A summary",
        published_at=now,
        tags=["LLM", "开源"],
    )
    assert item.summary == "A summary"
    assert item.published_at == now
    assert item.tags == ["LLM", "开源"]
