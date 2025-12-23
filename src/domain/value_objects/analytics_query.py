from dataclasses import dataclass

from src.domain.value_objects.aggregation_type import AggregationType
from src.domain.value_objects.entity_type import EntityType
from src.domain.value_objects.metric_type import MetricType


@dataclass
class AnalyticsQuery:
    entity: EntityType
    aggregations: AggregationType
    metric: MetricType
    filters: dict
    group_by: str | None

    def __post_init__(self):
        if self.filters is None:
            self.filters = {}
