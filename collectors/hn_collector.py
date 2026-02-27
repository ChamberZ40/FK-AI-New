import logging
import re
from datetime import datetime, timezone

import httpx

from collectors.base import BaseCollector
from config import HN_API_BASE, REQUEST_TIMEOUT
from models import NewsItem

logger = logging.getLogger(__name__)


class HNCollector(BaseCollector):
    name = "hackernews"

    def __init__(self, keywords: list[str], top_n: int = 30):
        self.keywords = keywords
        self.top_n = top_n
        self._pattern = re.compile(
            "|".join(re.escape(kw) for kw in keywords), re.IGNORECASE
        )

    def collect(self) -> list[NewsItem]:
        items = []
        try:
            with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
                story_ids = client.get(f"{HN_API_BASE}/topstories.json").json()
                for sid in story_ids[: self.top_n]:
                    story = client.get(f"{HN_API_BASE}/item/{sid}.json").json()
                    if not story or story.get("type") != "story":
                        continue
                    title = story.get("title", "")
                    if self._pattern.search(title):
                        url = story.get("url") or f"https://news.ycombinator.com/item?id={sid}"
                        published_at = None
                        if story.get("time"):
                            published_at = datetime.fromtimestamp(story["time"], tz=timezone.utc)
                        items.append(NewsItem(
                            title=title,
                            url=url,
                            source="hackernews",
                            published_at=published_at,
                        ))
        except Exception as e:
            logger.error(f"Hacker News 采集失败: {e}")
        return items
