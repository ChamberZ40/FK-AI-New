import logging
from datetime import datetime, timedelta, timezone

import httpx

from collectors.base import BaseCollector
from config import GITHUB_API_BASE, GITHUB_TOKEN, REQUEST_TIMEOUT
from models import NewsItem

logger = logging.getLogger(__name__)


class GitHubCollector(BaseCollector):
    name = "github"

    def __init__(self, topics: list[str], top_n: int = 10):
        self.topics = topics
        self.top_n = top_n

    def collect(self) -> list[NewsItem]:
        items = []
        yesterday = (datetime.now(tz=timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
        topic_q = " ".join(f"topic:{t}" for t in self.topics)
        query = f"{topic_q} stars:>100 pushed:>={yesterday}"
        try:
            headers = {"Accept": "application/vnd.github.v3+json"}
            if GITHUB_TOKEN:
                headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
            with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
                resp = client.get(
                    f"{GITHUB_API_BASE}/search/repositories",
                    params={"q": query, "sort": "stars", "order": "desc", "per_page": self.top_n},
                    headers=headers,
                )
                resp.raise_for_status()
                data = resp.json()
                for repo in data.get("items", []):
                    stars = repo.get("stargazers_count", 0)
                    lang = repo.get("language", "")
                    title = f"{repo['full_name']} - {repo.get('description', '')}"
                    summary = f"⭐ {stars} | {lang}" if lang else f"⭐ {stars}"
                    items.append(NewsItem(
                        title=title,
                        url=repo["html_url"],
                        source="github",
                        summary=summary,
                        tags=["开源"],
                    ))
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                logger.error("GitHub API 速率限制，建议设置 GITHUB_TOKEN 环境变量")
            else:
                logger.error(f"GitHub 采集失败: {e}")
        except Exception as e:
            logger.error(f"GitHub 采集失败: {e}")
        return items
