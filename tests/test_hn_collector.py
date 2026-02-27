from unittest.mock import patch
import httpx
from collectors.hn_collector import HNCollector


def _mock_response(json_data, status_code=200):
    return httpx.Response(status_code, json=json_data, request=httpx.Request("GET", "https://test"))


@patch("collectors.hn_collector.httpx.Client")
def test_hn_collector_filters_ai_stories(mock_client_cls):
    mock_client = mock_client_cls.return_value
    mock_client.__enter__ = lambda s: mock_client
    mock_client.__exit__ = lambda s, *a: None

    # top stories 返回 3 个 ID
    def mock_get(url, **kwargs):
        if "topstories" in url:
            return _mock_response([1, 2, 3])
        elif "/item/1" in url:
            return _mock_response({"id": 1, "title": "New AI Model Released", "url": "https://ai.com/1", "type": "story", "time": 1740000000})
        elif "/item/2" in url:
            return _mock_response({"id": 2, "title": "Python 4.0 Released", "url": "https://python.org/4", "type": "story", "time": 1740000000})
        elif "/item/3" in url:
            return _mock_response({"id": 3, "title": "GPT-5 benchmark results", "url": "https://ai.com/3", "type": "story", "time": 1740000000})

    mock_client.get = mock_get

    collector = HNCollector(keywords=["AI", "GPT"], top_n=3)
    items = collector.collect()
    # 只有 story 1 和 3 匹配 AI/GPT 关键词
    assert len(items) == 2
    assert items[0].title == "New AI Model Released"
    assert items[1].title == "GPT-5 benchmark results"
    assert items[0].source == "hackernews"
