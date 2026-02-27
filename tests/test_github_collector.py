from unittest.mock import patch
import httpx
from collectors.github_collector import GitHubCollector


def _mock_response(json_data, status_code=200):
    return httpx.Response(status_code, json=json_data, request=httpx.Request("GET", "https://test"))


@patch("collectors.github_collector.httpx.Client")
def test_github_collector_returns_repos(mock_client_cls):
    mock_client = mock_client_cls.return_value
    mock_client.__enter__ = lambda s: mock_client
    mock_client.__exit__ = lambda s, *a: None

    mock_client.get.return_value = _mock_response({
        "total_count": 2,
        "items": [
            {
                "full_name": "owner/ai-project",
                "html_url": "https://github.com/owner/ai-project",
                "description": "An AI project",
                "stargazers_count": 500,
                "language": "Python",
            },
            {
                "full_name": "owner/ml-lib",
                "html_url": "https://github.com/owner/ml-lib",
                "description": "ML library",
                "stargazers_count": 300,
                "language": "Python",
            },
        ],
    })

    collector = GitHubCollector(topics=["ai"], top_n=10)
    items = collector.collect()
    assert len(items) == 2
    assert items[0].source == "github"
    assert "ai-project" in items[0].title
    assert items[0].url == "https://github.com/owner/ai-project"
