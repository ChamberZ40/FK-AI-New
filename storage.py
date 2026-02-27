import json
import sqlite3
from datetime import datetime, timedelta, timezone
from models import NewsItem


class NewsStorage:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                source TEXT NOT NULL,
                summary TEXT,
                published_at TIMESTAMP,
                collected_at TIMESTAMP NOT NULL,
                tags TEXT,
                pushed INTEGER DEFAULT 0
            )
        """)
        self.conn.commit()

    def save_many(self, items: list[NewsItem]) -> int:
        count = 0
        with self.conn:
            for item in items:
                cursor = self.conn.execute(
                    """INSERT OR IGNORE INTO news
                       (title, url, source, summary, published_at, collected_at, tags)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        item.title,
                        item.url,
                        item.source,
                        item.summary,
                        item.published_at.isoformat() if item.published_at else None,
                        item.collected_at.isoformat(),
                        json.dumps(item.tags, ensure_ascii=False),
                    ),
                )
                if cursor.rowcount > 0:
                    count += 1
        return count

    def get_unpushed(self, hours: int = 24) -> list[NewsItem]:
        """获取未推送的新闻，默认只取最近 24 小时内发布的"""
        cutoff = (datetime.now(tz=timezone.utc) - timedelta(hours=hours)).isoformat()
        cursor = self.conn.execute(
            """SELECT title, url, source, summary, published_at, collected_at, tags
               FROM news WHERE pushed = 0 AND published_at >= ?
               ORDER BY published_at DESC""",
            (cutoff,),
        )
        items = []
        for row in cursor:
            items.append(NewsItem(
                title=row[0],
                url=row[1],
                source=row[2],
                summary=row[3],
                published_at=datetime.fromisoformat(row[4]) if row[4] else None,
                collected_at=datetime.fromisoformat(row[5]),
                tags=json.loads(row[6]) if row[6] else [],
            ))
        return items

    def mark_pushed(self, urls: list[str]):
        if not urls:
            return
        placeholders = ",".join("?" for _ in urls)
        self.conn.execute(
            f"UPDATE news SET pushed = 1 WHERE url IN ({placeholders})", urls
        )
        self.conn.commit()

    def close(self):
        self.conn.close()
