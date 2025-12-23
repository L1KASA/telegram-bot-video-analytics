from src.logging import logger
from typing import Optional
from src.domain.services.nlu_service import NLUService

from src.config import settings
from src.infrastructure.llm.ollama_client import OllamaClient, OllamaConfig
from src.infrastructure.llm.nlu_impl import OllamaNLUService


class LLMServiceFactory:
    @staticmethod
    def create_ollama_service(
        base_url: str | None = None,
        model: str | None = None,
        timeout: int | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None
    ) -> NLUService:
        config = OllamaConfig(
            base_url=base_url or settings.LLM_BASE_URL,
            model=model or settings.LLM_MODEL,
            timeout=timeout or settings.LLM_TIMEOUT,
            temperature=temperature or settings.LLM_TEMPERATURE,
            max_tokens=max_tokens or settings.LLM_MAX_TOKENS,
        )

        client = OllamaClient(config)
        service = OllamaNLUService(client)

        logger.info(f"Создан OllamaNLUService с моделью {model} и доменными промптами")
        return service

    @staticmethod
    async def create_validated_service(**kwargs) -> Optional[NLUService]:
        """
        Создает и валидирует сервис

        Returns:
            Валидный NLUService или None
        """
        try:
            service = LLMServiceFactory.create_ollama_service(**kwargs)

            # Проверяем доступность
            is_healthy = await service.health_check()

            if is_healthy:
                logger.info("LLM сервис успешно создан и валидирован")

                test_query = "Сколько всего видео есть в системе?"
                test_result = await service.parse_query(test_query)

                if test_result:
                    logger.info(f"Тестовый запрос успешно разобран: {test_result}")
                else:
                    logger.warning("Тестовый запрос не разобран, возможны проблемы с промптом")

                return service
            else:
                logger.error("LLM сервис недоступен")
                return None

        except Exception as e:
            logger.exception(f"Ошибка создания LLM сервиса: {e}")
            return None
