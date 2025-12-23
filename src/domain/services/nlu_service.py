from abc import ABC, abstractmethod
from typing import Optional
from src.domain.value_objects.analytics_query import AnalyticsQuery


class NLUService(ABC):
    @abstractmethod
    async def parse_query(self, user_text: str) -> Optional[AnalyticsQuery]:
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        pass
