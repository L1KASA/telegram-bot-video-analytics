from enum import Enum


class MetricType(Enum):
    VIEWS = "views_count"
    LIKES = "likes_count"
    COMMENTS = "comments_count"
    REPORTS = "reports_count"

    DELTA_VIEWS = "delta_views_count"
    DELTA_LIKES = "delta_likes_count"
    DELTA_COMMENTS = "delta_comments_count"
    DELTA_REPORTS = "delta_reports_count"

    VIDEO_ID = "video_id"
    CREATOR_ID = "creator_id"
