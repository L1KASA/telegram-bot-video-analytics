import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from src.infrastructure.database.database import Base


class Video(Base):
    __tablename__ = 'videos'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
    )
    creator_id: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
    )
    views_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    likes_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    reports_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    comments_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    video_created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    update_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    snapshots: Mapped[list['VideoSnapshot']] = relationship(
        'VideoSnapshot',
        back_populates='video',
        cascade='all, delete-orphan',
        lazy='selectin',
    )


class VideoSnapshot(Base):
    __tablename__ = 'video_snapshots'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    video_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('videos.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    views_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    likes_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    comments_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reports_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    delta_views_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    delta_likes_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    delta_comments_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    delta_reports_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    video: Mapped['Video'] = relationship('Video', back_populates='snapshots')
