import logging
from datetime import datetime
from calendar import timegm

import feedparser

from collectors.base import BaseCollector
from models import NewsItem

logger = logging.getLogger(__name__)


class RSSCollector(BaseCollector):
    name = "rss"

    def __init__(self, feeds: dict[str, str]):
        self.feeds = feeds  # {"source_name": "feed_url", ...}

    def collect(self) -> list[NewsItem]:
        items = []
        for source_name, feed_url in self.feeds.items():
            try:
                items.extend(self._parse_feed(source_name, feed_url))
            except Exception as e:
                logger.error(f"RSS 采集失败 [{source_name}]: {e}")
        return items

    def _parse_feed(self, source_name: str, feed_url: str) -> list[NewsItem]:
        feed = feedparser.parse(feed_url)
        items = []
        for entry in feed.entries:
            published_at = None
            published_parsed = entry.get("published_parsed")
            if published_parsed:
                published_at = datetime.utcfromtimestamp(timegm(published_parsed))

            items.append(NewsItem(
                title=entry.title,
                url=entry.link,
                source=source_name,
                summary=entry.get("summary", ""),
                published_at=published_at,
            ))
        return items
