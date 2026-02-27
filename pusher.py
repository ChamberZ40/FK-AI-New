import logging
from collections import defaultdict
from datetime import datetime

import httpx

from config import REQUEST_TIMEOUT
from models import NewsItem

logger = logging.getLogger(__name__)

# source -> 分类名
CATEGORY_MAP = {
    "hackernews": "AI资讯",
    "github": "AI技术",
}
# 默认分类（RSS 博客等）
DEFAULT_CATEGORY = "AI技术"

# 数字 emoji 列表
NUM_EMOJIS = ["1⃣️", "2⃣️", "3⃣️", "4⃣️", "5⃣️", "6⃣️", "7⃣️", "8⃣️", "9⃣️", "🔟"]


class LarkPusher:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def format_daily_report(self, items: list[NewsItem]) -> str:
        today = datetime.now().strftime("%Y%m%d")
        lines = [f"🌟 {today} AI日报🌟", ""]

        if not items:
            lines.append("暂无新闻")
            return "\n".join(lines)

        # 按分类分组
        grouped: dict[str, list[NewsItem]] = defaultdict(list)
        for item in items:
            category = CATEGORY_MAP.get(item.source, DEFAULT_CATEGORY)
            grouped[category].append(item)

        # 按固定顺序输出分类
        for category in ["AI资讯", "AI技术", "AI应用", "其他"]:
            if category not in grouped:
                continue
            lines.append(f"【{category}】")
            for i, item in enumerate(grouped[category]):
                emoji = NUM_EMOJIS[i] if i < len(NUM_EMOJIS) else f"{i+1}."
                lines.append(f"{emoji} {item.title}。{item.url}")
            lines.append("")

        return "\n".join(lines).rstrip()

    def send(self, items: list[NewsItem]) -> bool:
        if not self.webhook_url:
            logger.error("飞书 Webhook URL 未配置")
            return False

        text = self.format_daily_report(items)
        try:
            resp = httpx.post(
                self.webhook_url,
                json={"msg_type": "text", "content": {"text": text}},
                timeout=REQUEST_TIMEOUT,
            )
            resp.raise_for_status()
            logger.info(f"飞书推送成功，共 {len(items)} 条新闻")
            return True
        except Exception as e:
            logger.error(f"飞书推送失败: {e}")
            return False
