from datetime import datetime
from typing import Dict

from sqlalchemy import select, func, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.value_objects.aggregation_type import AggregationType
from src.domain.value_objects.analytics_query import AnalyticsQuery
from src.domain.value_objects.entity_type import EntityType
from src.domain.value_objects.metric_type import MetricType
from src.infrastructure.database.models import Video, VideoSnapshot


class AnalyticsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def execute_query(self, query: AnalyticsQuery) -> int:
        if query.entity == EntityType.VIDEO:
            return await self._execute_video_query(query)
        else:
            return await self._execute_snapshot_query(query)

    def _apply_filters(self, stmt, model, filters: Dict):
        if "date_from" in filters:
            d_from = datetime.fromisoformat(filters["date_from"])
            if model == Video:
                stmt = stmt.where(model.video_created_at >= d_from)
            else:
                stmt = stmt.where(model.created_at >= d_from)

        if "date_to" in filters:
            d_to = datetime.fromisoformat(filters["date_to"])
            if model == Video:
                stmt = stmt.where(model.video_created_at <= d_to)
            else:
                stmt = stmt.where(model.created_at <= d_to)

        if "date_single" in filters:
            d_single = datetime.fromisoformat(filters["date_single"])
            next_day = d_single.replace(day=d_single.day + 1)
            if model == Video:
                stmt = stmt.where(
                    (model.video_created_at >= d_single) &
                    (model.video_created_at < next_day)
                )
            else:
                stmt = stmt.where(
                    (model.created_at >= d_single) &
                    (model.created_at < next_day)
                )

        return stmt

    def _apply_metric_filters(self, stmt, metric_col, filters: Dict):
        if "metric_gt" in filters:
            stmt = stmt.where(metric_col > filters["metric_gt"])
        if "metric_lt" in filters:
            stmt = stmt.where(metric_col < filters["metric_lt"])
        if "metric_eq" in filters:
            stmt = stmt.where(metric_col == filters["metric_eq"])
        return stmt

    def _build_aggregation(self, query: AnalyticsQuery, model, metric_col, base_stmt):
        if query.aggregations == AggregationType.COUNT:
            return select(func.count()).select_from(base_stmt.subquery())

        elif query.aggregations == AggregationType.SUM:
            return select(func.sum(metric_col)).select_from(base_stmt.subquery())

        elif query.aggregations == AggregationType.AVG:
            return select(func.avg(metric_col)).select_from(base_stmt.subquery())

        elif query.aggregations == AggregationType.MAX:
            return select(func.max(metric_col)).select_from(base_stmt.subquery())

        elif query.aggregations == AggregationType.MIN:
            return select(func.min(metric_col)).select_from(base_stmt.subquery())

        elif query.aggregations == AggregationType.DISTINCT:
            if query.metric == MetricType.VIDEO_ID and model == VideoSnapshot:
                return select(func.count(distinct(model.video_id))).select_from(base_stmt.subquery())
            else:
                return select(func.count(distinct(metric_col))).select_from(base_stmt.subquery())

        return select(func.count()).select_from(base_stmt.subquery())

    async def _execute_video_query(self, query: AnalyticsQuery) -> int:
        model = Video
        base_stmt = select(model)
        base_stmt = self._apply_filters(base_stmt, model, query.filters)

        metric_col = getattr(model, query.metric.value, model.views_count)
        base_stmt = self._apply_metric_filters(base_stmt, metric_col, query.filters)

        final_stmt = self._build_aggregation(query, model, metric_col, base_stmt)

        result = await self.session.execute(final_stmt)
        val = result.scalar()
        return val if val is not None else 0

    async def _execute_snapshot_query(self, query: AnalyticsQuery) -> int:
        model = VideoSnapshot

        if query.metric == MetricType.VIDEO_ID:
            metric_col = model.video_id
        else:
            metric_col = getattr(model, query.metric.value, model.delta_views_count)

        base_stmt = select(model)
        base_stmt = self._apply_filters(base_stmt, model, query.filters)
        base_stmt = self._apply_metric_filters(base_stmt, metric_col, query.filters)

        final_stmt = self._build_aggregation(query, model, metric_col, base_stmt)

        result = await self.session.execute(final_stmt)
        val = result.scalar()
        return val if val is not None else 0
