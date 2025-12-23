from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class Video:
    id: UUID
    creator_id: str
    views_count: int = 0
    likes_count: int = 0
    comments_count: int = 0
    reposts_count: int = 0
    video_created_at: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
