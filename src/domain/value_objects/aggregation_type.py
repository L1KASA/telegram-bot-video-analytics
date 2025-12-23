from enum import Enum


class AggregationType(Enum):
    """Type of aggregation for metrics"""
    COUNT="count"
    SUM="sum"
    AVG="avg"
    MAX="max"
    MIN="min"
    DISTINCT="distinct"
