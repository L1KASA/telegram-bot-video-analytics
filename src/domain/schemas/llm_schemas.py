from typing import Optional, Union, Literal
from pydantic import BaseModel, Field, field_validator

class AnalyticsFilter(BaseModel):
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    date_single: Optional[str] = None
    creator_id: Optional[str] = None
    metric_gt: Optional[Union[int, float]] = None
    metric_lt: Optional[Union[int, float]] = None
    metric_eq: Optional[Union[int, float]] = None

class LLMResponseSchema(BaseModel):
    entity: Literal["video", "video_snapshot"]
    aggregation: Literal["count", "sum", "avg", "max", "min", "distinct"]
    metric: str
    filters: AnalyticsFilter = Field(default_factory=AnalyticsFilter)
    group_by: Optional[str] = None

    @field_validator("group_by")
    def validate_group_by(cls, v):
        if v == "null":
            return None
        return v
