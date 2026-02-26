from unittest.mock import patch, MagicMock
from collectors.rss_collector import RSSCollector


def _fake_feed():
    """构造一个模拟的 feedparser 返回值"""
    feed = MagicMock()
    entry = MagicMock()
    entry.title = "OpenAI announces GPT-5"
    entry.link = "https://openai.com/blog/gpt5"
    entry.get = lambda key, default=None: {
        "summary": "A new model release",
        "published_parsed": (2026, 2, 26, 10, 0, 0, 2, 57, 0),
    }.get(key, default)
    feed.entries = [entry]
    feed.bozo = False
    return feed


@patch("collectors.rss_collector.feedparser.parse")
def test_rss_collector_returns_items(mock_parse):
    mock_parse.return_value = _fake_feed()
    collector = RSSCollector(feeds={"test_blog": "https://test.com/rss"})
    items = collector.collect()
    assert len(items) == 1
    assert items[0].title == "OpenAI announces GPT-5"
    assert items[0].url == "https://openai.com/blog/gpt5"
    assert items[0].source == "test_blog"


@patch("collectors.rss_collector.feedparser.parse")
def test_rss_collector_handles_empty_feed(mock_parse):
    feed = MagicMock()
    feed.entries = []
    feed.bozo = False
    mock_parse.return_value = feed
    collector = RSSCollector(feeds={"empty": "https://empty.com/rss"})
    items = collector.collect()
    assert items == []
