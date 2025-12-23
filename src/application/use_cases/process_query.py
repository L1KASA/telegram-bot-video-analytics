from src.logging import logger
from src.domain.services.nlu_service import NLUService
from src.infrastructure.database.repositories.video_repository import AnalyticsRepository


class ProcessQueryUseCase:
    def __init__(self, nlu_service: NLUService, repository: AnalyticsRepository):
        self.nlu_service = nlu_service
        self.repository = repository

    async def execute(self, user_text: str) -> int:
        try:
            query = await self.nlu_service.parse_query(user_text)
            if not query:
                logger.error(f"Не удалось разобрать запрос: {user_text}")
                return -1

            result = await self.repository.execute_query(query)

            logger.info(f"Запрос обработан: '{user_text}' → {result}")
            return result

        except Exception as e:
            logger.exception(f"Ошибка обработки запроса: {e}")
            return -1
