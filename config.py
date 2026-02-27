import os

# RSS 源
RSS_FEEDS = {
    "openai_blog": "https://openai.com/blog/rss.xml",
    "anthropic_blog": "https://www.anthropic.com/news.rss",
    "deepmind_blog": "https://deepmind.google/blog/rss.xml",
}

# Hacker News
HN_API_BASE = "https://hacker-news.firebaseio.com/v0"
HN_KEYWORDS = [
    "AI", "LLM", "GPT", "ChatGPT", "Claude", "Gemini",
    "machine learning", "deep learning", "neural network",
    "OpenAI", "Anthropic", "DeepMind", "Mistral",
    "transformer", "diffusion", "generative",
]
HN_TOP_N = 30

# GitHub
GITHUB_API_BASE = "https://api.github.com"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_TOPICS = ["artificial-intelligence", "machine-learning", "llm", "deep-learning"]
GITHUB_TOP_N = 10

# 飞书推送（应用机器人）
LARK_APP_ID = os.environ.get("LARK_APP_ID", "")
LARK_APP_SECRET = os.environ.get("LARK_APP_SECRET", "")
LARK_RECEIVE_ID = os.environ.get("LARK_RECEIVE_ID", "")  # 接收者（邮箱或 chat_id）
LARK_RECEIVE_ID_TYPE = os.environ.get("LARK_RECEIVE_ID_TYPE", "email")  # email / chat_id / open_id

# 数据库
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "news.db")

# HTTP 请求超时（秒）
REQUEST_TIMEOUT = 10
