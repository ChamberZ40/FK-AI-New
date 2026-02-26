from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class NewsItem:
    title: str
    url: str
    source: str
    summary: str | None = None
    published_at: datetime | None = None
    collected_at: datetime = field(default_factory=datetime.now)
    tags: list[str] = field(default_factory=list)
