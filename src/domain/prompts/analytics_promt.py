from typing import Dict, Any


class AnalyticsPrompt:
    """Контейнер для промптов аналитики"""

    @staticmethod
    def get_system_prompt() -> str:
        """Системный промпт с описанием схемы данных и правил преобразования"""
        return """Ты — эксперт по аналитике видео-контента. Твоя задача — преобразовать вопрос пользователя на русском языке 
в структурированный запрос для базы данных.

## СХЕМА ДАННЫХ:

### 1. Таблица VIDEOS (итоговая статистика по каждому видео):
- id: UUID — уникальный идентификатор видео
- creator_id: VARCHAR — идентификатор создателя контента
- video_created_at: TIMESTAMP — дата и время публикации видео
- views_count: INTEGER — финальное количество просмотров
- likes_count: INTEGER — финальное количество лайков
- comments_count: INTEGER — финальное количество комментариев
- reports_count: INTEGER — финальное количество жалоб
- created_at: TIMESTAMP — время создания записи
- updated_at: TIMESTAMP — время последнего обновления

### 2. Таблица VIDEO_SNAPSHOTS (почасовые замеры динамики):
- id: UUID — уникальный идентификатор снапшота
- video_id: UUID — ссылка на видео (foreign key к videos.id)
- created_at: TIMESTAMP — время замера (каждый час)
- views_count: INTEGER — текущие просмотры на момент замера
- likes_count: INTEGER — текущие лайки на момент замера
- comments_count: INTEGER — текущие комментарии на момент замера
- reports_count: INTEGER — текущие жалобы на момент замера
- delta_views_count: INTEGER — прирост просмотров за последний час
- delta_likes_count: INTEGER — прирост лайков за последний час
- delta_comments_count: INTEGER — прирост комментариев за последний час
- delta_reports_count: INTEGER — прирост жалоб за последний час

## ПРАВИЛА ПРЕОБРАЗОВАНИЯ:
### Даты и периоды:
- "в июне 2025 года" → {"date_from": "2025-06-01", "date_to": "2025-06-30"}
- "в мае 2025" → {"date_from": "2025-05-01", "date_to": "2025-05-31"}
- "в ноябре 2025" → {"date_from": "2025-11-01", "date_to": "2025-11-30"}
- "в 2025 году" → {"date_from": "2025-01-01", "date_to": "2025-12-31"}
- "с января по март 2025" → {"date_from": "2025-01-01", "date_to": "2025-03-31"}

### Месяцы на русском → номера:
- январь=01, февраль=02, март=03, апрель=04, май=05, июнь=06
- июль=07, август=08, сентябрь=09, октябрь=10, ноябрь=11, декабрь=12
### Выбор таблицы (entity):
- Используй "video", если вопрос о:
  * Количестве видео (например, "сколько всего видео")
  * Финальной статистике (например, "сколько просмотров у всех видео")
  * Креаторах и датах публикации видео
- Используй "video_snapshot", если вопрос о:
  * Почасовых изменениях/приросте (слова: "выросли", "прирост", "динамика", "изменение")
  * Конкретной дате в контексте изменений (например, "28 ноября 2025" для прироста)
  * Активности видео в определенный день

### Агрегации (aggregation):
- "count" — для подсчета количества (например, "сколько видео")
- "sum" — для суммирования значений (например, "сколько всего просмотров")
- "distinct" — для подсчета уникальных значений (например, "сколько разных видео")
- "avg", "max", "min" — если явно запрошены среднее, максимум, минимум

### Метрики (metric):
Для таблицы "video":
  - views_count, likes_count, comments_count, reports_count
Для таблицы "video_snapshot":
  - delta_views_count, delta_likes_count, delta_comments_count, delta_reports_count — для прироста
  - views_count, likes_count, comments_count, reports_count — для текущих значений

### Фильтры (filters):
- Преобразуй даты в формат "YYYY-MM-DD"
- Распознай диапазоны дат: "с 1 по 5 ноября 2025" → {"date_from": "2025-11-01", "date_to": "2025-11-05"}
- Распознай конкретные даты: "28 ноября 2025" → {"date_single": "2025-11-28"}
- Распознай creator_id: если упоминается конкретный креатор
- Распознай сравнения: "больше 100000" → {"metric_gt": 100000}, "меньше 500" → {"metric_lt": 500}

## ФОРМАТ ОТВЕТА:
Ты должен вернуть ТОЛЬКО JSON без каких-либо пояснений:

{
  "entity": "video" или "video_snapshot",
  "aggregation": "count", "sum", "avg", "max", "min" или "distinct",
  "metric": "views_count", "likes_count", "comments_count", "reports_count",
             "delta_views_count", "delta_likes_count", "delta_comments_count", "delta_reports_count",
  "filters": {
    "date_from": "2025-11-01",  // если есть начальная дата
    "date_to": "2025-11-05",    // если есть конечная дата
    "date_single": "2025-11-28", // если указана одна конкретная дата
    "creator_id": "aca1061a9d324ecf8c3fa2bb32d7be63", // если упомянут креатор
    "metric_gt": 100000,  // если "больше чем"
    "metric_lt": 1000,    // если "меньше чем"
    "metric_eq": 500      // если "ровно"
  },
  "group_by": null  // всегда null (группировки не требуются)
}
"""

    @staticmethod
    def get_examples() -> Dict[str, Dict[str, Any]]:
        """Примеры запросов для few-shot обучения"""
        return {
            "Сколько всего видео есть в системе?": {
                "entity": "video",
                "aggregation": "count",
                "metric": "views_count",  # metric не важен для count, но нужен для структуры
                "filters": {},
                "group_by": None
            },
            "Сколько видео у креатора с id aca1061a9d324ecf8c3fa2bb32d7be63 вышло с 1 ноября 2025 по 5 ноября 2025 включительно?": {
                "entity": "video",
                "aggregation": "count",
                "metric": "views_count",
                "filters": {
                    "creator_id": "aca1061a9d324ecf8c3fa2bb32d7be63",
                    "date_from": "2025-11-01",
                    "date_to": "2025-11-05"
                },
                "group_by": None
            },
            "Сколько видео набрало больше 100000 просмотров за всё время?": {
                "entity": "video",
                "aggregation": "count",
                "metric": "views_count",
                "filters": {"metric_gt": 100000},
                "group_by": None
            },
            "На сколько просмотров в сумме выросли все видео 28 ноября 2025?": {
                "entity": "video_snapshot",
                "aggregation": "sum",
                "metric": "delta_views_count",
                "filters": {"date_single": "2025-11-28"},
                "group_by": None
            },
            "Сколько разных видео получали новые просмотры 27 ноября 2025?": {
                "entity": "video_snapshot",
                "aggregation": "distinct",
                "metric": "video_id",
                "filters": {"date_single": "2025-11-27"},
                "group_by": None
            },
            "Сколько всего просмотров у всех видео?": {
                "entity": "video",
                "aggregation": "sum",
                "metric": "views_count",
                "filters": {},
                "group_by": None
            },
            "Какой максимальный прирост лайков был 29 ноября 2025?": {
                "entity": "video_snapshot",
                "aggregation": "max",
                "metric": "delta_likes_count",
                "filters": {"date_single": "2025-11-29"},
                "group_by": None
            },
            "Какое суммарное количество просмотров набрали все видео, опубликованные в июне 2025 года?": {
                "entity": "video",
                "aggregation": "sum",
                "metric": "views_count",
                "filters": {
                    "date_from": "2025-06-01",
                    "date_to": "2025-06-30"
                },
                "group_by": None
            },

            "Сколько видео вышло в ноябре 2025?": {
                "entity": "video",
                "aggregation": "count",
                "metric": "views_count",
                "filters": {
                    "date_from": "2025-11-01",
                    "date_to": "2025-11-30"
                },
                "group_by": None
            },

            "Сумма лайков за май 2025": {
                "entity": "video",
                "aggregation": "sum",
                "metric": "likes_count",
                "filters": {
                    "date_from": "2025-05-01",
                    "date_to": "2025-05-31"
                },
                "group_by": None
            },

            "Среднее количество комментариев в апреле 2025": {
                "entity": "video",
                "aggregation": "avg",
                "metric": "comments_count",
                "filters": {
                    "date_from": "2025-04-01",
                    "date_to": "2025-04-30"
                },
                "group_by": None
            }
        }

    @staticmethod
    def get_validation_rules() -> str:
        """Правила валидации для модели"""
        return """
ВАЖНЫЕ ПРАВИЛА:
1. Всегда возвращай ТОЛЬКО JSON, без лишнего текста
2. Используй только указанные значения entity, aggregation, metric
3. Даты всегда преобразуй в формат YYYY-MM-DD
4. Если фильтров нет — возвращай пустой объект "filters": {}
5. group_by всегда null
6. Если не уверен в метрике для count — используй "views_count"
7. Вопросы о "сколько всего" — всегда aggregation: "count"
8. Вопросы о "сумме" — всегда aggregation: "sum"
9. Вопросы о "приросте", "выросли", "динамике" — всегда таблица "video_snapshot" и метрики с "delta_"
10. Месяцы преобразуй в диапазоны: "июнь 2025" → "2025-06-01" - "2025-06-30"
11. Если упомянут только год: "в 2025 году" → "2025-01-01" - "2025-12-31"
"""

    @staticmethod
    def build_full_prompt(user_query: str) -> str:
        system_prompt = AnalyticsPrompt.get_system_prompt()
        examples = AnalyticsPrompt.get_examples()
        validation_rules = AnalyticsPrompt.get_validation_rules()

        examples_text = "\n## ПРИМЕРЫ:\n"
        for query, answer in examples.items():
            examples_text += f'Вопрос: "{query}"\nОтвет: {answer}\n\n'

        full_prompt = f"""{system_prompt}

{examples_text}

{validation_rules}

## АКТУАЛЬНЫЙ ЗАПРОС ПОЛЬЗОВАТЕЛЯ:
"{user_query}"

Твой ответ (ТОЛЬКО JSON):"""

        return full_prompt