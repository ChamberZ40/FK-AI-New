import argparse
import logging
import os
import sys

from config import (
    DB_PATH,
    LARK_APP_ID, LARK_APP_SECRET, LARK_RECEIVE_ID, LARK_RECEIVE_ID_TYPE,
    RSS_FEEDS, HN_KEYWORDS, HN_TOP_N,
    GITHUB_TOPICS, GITHUB_TOP_N,
)
from collectors.rss_collector import RSSCollector
from collectors.hn_collector import HNCollector
from collectors.github_collector import GitHubCollector
from storage import NewsStorage
from pusher import LarkPusher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def get_collectors():
    return [
        RSSCollector(feeds=RSS_FEEDS),
        HNCollector(keywords=HN_KEYWORDS, top_n=HN_TOP_N),
        GitHubCollector(topics=GITHUB_TOPICS, top_n=GITHUB_TOP_N),
    ]


def collect_news(storage: NewsStorage) -> int:
    """运行所有采集器，保存新闻到数据库，返回新增条数"""
    total_new = 0
    for collector in get_collectors():
        try:
            logger.info(f"开始采集: {collector.name}")
            items = collector.collect()
            count = storage.save_many(items)
            logger.info(f"  采集到 {len(items)} 条，新增 {count} 条")
            total_new += count
        except Exception as e:
            logger.error(f"  采集器 [{collector.name}] 失败: {e}")
    return total_new


def push_news(storage: NewsStorage) -> bool:
    """推送未推送的新闻到飞书"""
    items = storage.get_unpushed()
    if not items:
        logger.info("没有待推送的新闻")
        return True

    pusher = LarkPusher(
        app_id=LARK_APP_ID,
        app_secret=LARK_APP_SECRET,
        receive_id=LARK_RECEIVE_ID,
        receive_id_type=LARK_RECEIVE_ID_TYPE,
    )
    success = pusher.send(items)
    if success:
        storage.mark_pushed([item.url for item in items])
    return success


def main():
    parser = argparse.ArgumentParser(description="AI 新闻采集与推送")
    parser.add_argument("--collect-only", action="store_true", help="只采集不推送")
    parser.add_argument("--push-only", action="store_true", help="只推送未推送的新闻")
    args = parser.parse_args()

    # 确保数据目录存在
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    storage = NewsStorage(DB_PATH)
    try:
        if not args.push_only:
            new_count = collect_news(storage)
            logger.info(f"采集完成，共新增 {new_count} 条新闻")

        if not args.collect_only:
            if not push_news(storage):
                sys.exit(1)
    finally:
        storage.close()


if __name__ == "__main__":
    main()
