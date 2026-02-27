from datetime import datetime
from models import NewsItem
from pusher import LarkPusher


def _make_items():
    return [
        NewsItem(title="AI大模型新突破", url="https://example.com/1", source="hackernews"),
        NewsItem(title="OpenAI发布新功能", url="https://openai.com/blog/new", source="openai_blog"),
        NewsItem(title="owner/cool-ai - Amazing AI tool", url="https://github.com/owner/cool-ai", source="github"),
    ]


def test_format_daily_report():
    pusher = LarkPusher(webhook_url="https://fake.webhook")
    report = pusher.format_daily_report(_make_items())
    # 检查日报标题
    today = datetime.now().strftime("%Y%m%d")
    assert f"🌟 {today} AI日报🌟" in report
    # 检查分类标题存在
    assert "【AI资讯】" in report
    assert "【AI技术】" in report
    # 检查内容包含新闻
    assert "AI大模型新突破" in report
    assert "https://example.com/1" in report


def test_format_empty_report():
    pusher = LarkPusher(webhook_url="https://fake.webhook")
    report = pusher.format_daily_report([])
    today = datetime.now().strftime("%Y%m%d")
    assert f"🌟 {today} AI日报🌟" in report
    assert "暂无新闻" in report
