from abc import ABC, abstractmethod
from models import NewsItem


class BaseCollector(ABC):
    name: str = "base"

    @abstractmethod
    def collect(self) -> list[NewsItem]:
        """执行采集，返回新闻列表"""
        ...
