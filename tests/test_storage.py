import pytest
from datetime import datetime
from models import NewsItem
from storage import NewsStorage


@pytest.fixture
def db(tmp_path):
    db_path = str(tmp_path / "test.db")
    storage = NewsStorage(db_path)
    yield storage
    storage.close()


def _make_item(title="Test", url="https://example.com", source="test"):
    return NewsItem(title=title, url=url, source=source)


def test_save_and_get_unpushed(db):
    items = [_make_item(url="https://example.com/1"), _make_item(url="https://example.com/2")]
    count = db.save_many(items)
    assert count == 2
    unpushed = db.get_unpushed()
    assert len(unpushed) == 2


def test_dedup_by_url(db):
    item = _make_item(url="https://example.com/dup")
    db.save_many([item])
    db.save_many([item])  # 重复插入
    unpushed = db.get_unpushed()
    assert len(unpushed) == 1


def test_mark_pushed(db):
    items = [_make_item(url="https://example.com/a"), _make_item(url="https://example.com/b")]
    db.save_many(items)
    db.mark_pushed(["https://example.com/a"])
    unpushed = db.get_unpushed()
    assert len(unpushed) == 1
    assert unpushed[0].url == "https://example.com/b"
