import json
from typing import Optional
from src.domain.services.nlu_service import NLUService
from src.domain.value_objects.analytics_query import AnalyticsQuery
from src.domain.value_objects.aggregation_type import AggregationType
from src.domain.value_objects.entity_type import EntityType
from src.domain.value_objects.metric_type import MetricType
from src.domain.prompts.analytics_promt import AnalyticsPrompt
from .ollama_client import OllamaClient, OllamaError, extract_json_from_text
from src.logging import logger
from ...domain.schemas.llm_schemas import LLMResponseSchema


class OllamaNLUService(NLUService):
    def __init__(self, ollama_client: OllamaClient):
        self.client = ollama_client
        logger.info(f"Инициализирован OllamaNLUService с моделью: {ollama_client.config.model}")

    async def parse_query(self, user_text: str) -> Optional[AnalyticsQuery]:
        logger.debug(f"Парсинг запроса: {user_text}")

        full_prompt = AnalyticsPrompt.build_full_prompt(user_text)

        try:
            response_text = await self.client.generate(full_prompt, format="json")

            if not response_text:
                logger.error("Пустой ответ от Ollama")
                return None

            json_text = self._clean_and_extract_json(response_text)

            from src.domain.schemas.llm_schemas import LLMResponseSchema
            validated_model = LLMResponseSchema.model_validate_json(json_text)

            analytics_query = self._schema_to_query(validated_model)

            logger.debug(f"Успешно обработанный запрос: {analytics_query}")
            return analytics_query

        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}\nОтвет модели: {response_text}")
            return None
        except OllamaError as e:
            logger.error(f"Ошибка Ollama: {e}")
            return None
        except ValueError as e:
            logger.error(f"Ошибка проверки запроса: {e}")
            return None
        except Exception as e:
            logger.exception(f"Непредвиденная ошибка при разборе запроса: {e}")
            return None

    async def health_check(self) -> bool:
        return await self.client.health_check()

    def _clean_and_extract_json(self, text: str) -> str:
        text = text.replace('```json', '').replace('```', '').strip()
        json_text = extract_json_from_text(text)
        json_text = json_text.replace('\n', ' ').replace('\t', ' ')
        return json_text

    def _schema_to_query(self, schema: 'LLMResponseSchema') -> AnalyticsQuery:
        try:
            entity = EntityType(schema.entity)
            aggregation = AggregationType(schema.aggregation)
            metric = MetricType(schema.metric)

            filters = schema.filters.model_dump(exclude_none=True)
            group_by = schema.group_by

            self._validate_business_rules(entity, aggregation, metric)

            return AnalyticsQuery(
                entity=entity,
                aggregations=aggregation,
                metric=metric,
                filters=filters,
                group_by=group_by
            )

        except (KeyError, ValueError) as e:
            raise ValueError(f"Ошибка при создании AnalyticsQuery: {e}")

    def _validate_business_rules(
        self,
        entity: EntityType,
        aggregation: AggregationType,
        metric: MetricType
    ):

        if entity == EntityType.VIDEO_SNAPSHOT and aggregation == AggregationType.DISTINCT:
            if metric != MetricType.VIDEO_ID:
                logger.warning(f"Для различения в моментальных снимках лучше использовать video_id, полученный: {metric}")

        if entity == EntityType.VIDEO:
            delta_metrics = {MetricType.DELTA_VIEWS, MetricType.DELTA_LIKES,
                             MetricType.DELTA_COMMENTS, MetricType.DELTA_REPORTS}
            if metric in delta_metrics:
                logger.warning(f"Метрика {metric} бычно используется с video_snapshot, а не с видео.")

        if aggregation == AggregationType.COUNT:
            logger.debug(f"Агрегация=count, метрика={metric} - допустимо")
