from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class VideoSnapshot:
    id: UUID
    video_id: UUID
    views_count: int = 0
    likes_count: int = 0
    comments_count: int = 0
    reports_count: int = 0
    delta_views_count: int = 0
    delta_likes_count: int = 0
    delta_comments_count: int = 0
    delta_reports_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
