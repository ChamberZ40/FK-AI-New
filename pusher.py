import json
import logging
from collections import defaultdict
from datetime import datetime

import lark_oapi as lark
from lark_oapi.api.im.v1 import CreateMessageRequest, CreateMessageRequestBody

from config import LARK_APP_ID, LARK_APP_SECRET, LARK_RECEIVE_ID, LARK_RECEIVE_ID_TYPE
from models import NewsItem

logger = logging.getLogger(__name__)

# source → 分类名
CATEGORY_MAP = {
    "hackernews": "AI资讯",
    "github": "AI技术",
}
# 默认分类（RSS 博客等）
DEFAULT_CATEGORY = "AI技术"

# 数字 emoji 列表
NUM_EMOJIS = ["1⃣️", "2⃣️", "3⃣️", "4⃣️", "5⃣️", "6⃣️", "7⃣️", "8⃣️", "9⃣️", "🔟"]


class LarkPusher:
    def __init__(self, app_id: str, app_secret: str, receive_id: str, receive_id_type: str = "email"):
        self.receive_id = receive_id
        self.receive_id_type = receive_id_type
        self.client = lark.Client.builder() \
            .app_id(app_id) \
            .app_secret(app_secret) \
            .enable_set_token(True) \
            .domain(lark.FEISHU_DOMAIN) \
            .log_level(lark.LogLevel.WARNING) \
            .build()

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
        if not self.receive_id:
            logger.error("飞书接收者未配置（LARK_RECEIVE_ID）")
            return False

        text = self.format_daily_report(items)
        content = json.dumps({"text": text})

        request = CreateMessageRequest.builder() \
            .receive_id_type(self.receive_id_type) \
            .request_body(CreateMessageRequestBody.builder()
                .receive_id(self.receive_id)
                .msg_type("text")
                .content(content)
                .build()) \
            .build()

        response = self.client.im.v1.message.create(request)
        if response.success():
            logger.info(f"飞书推送成功，共 {len(items)} 条新闻")
            return True
        else:
            logger.error(f"飞书推送失败: code={response.code}, msg={response.msg}")
            return False
