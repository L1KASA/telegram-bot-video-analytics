import asyncio
import json
import os
import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import delete

from src.infrastructure.database.models import Video, VideoSnapshot
from src.config import settings
from src.logging import setup_logging, logger

def parse_datetime(dt_str: str) -> datetime:
    # Assuming ISO 8601 format
    return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))

async def seed_data(file_path: str, session: AsyncSession) -> None:
    if not os.path.exists(file_path):
        logger.error(f"File {file_path} not found.")
        return

    logger.info(f"Starting to read file {file_path}...")
    
    try:
        logger.info("Clearing existing data...")
        await session.execute(delete(VideoSnapshot))
        await session.execute(delete(Video))
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        videos_data = data if isinstance(data, list) else data.get("videos", [])
        
        logger.info(f"Found {len(videos_data)} videos. Starting import...")
        
        for i, v_data in enumerate(videos_data):
            video = Video(
                id=uuid.UUID(v_data['id']),
                creator_id=v_data['creator_id'],
                views_count=v_data['views_count'],
                likes_count=v_data['likes_count'],
                comments_count=v_data['comments_count'],
                reports_count=v_data['reports_count'],
                video_created_at=parse_datetime(v_data['video_created_at'])
            )
            
            session.add(video)
            
            snapshots_data = v_data.get('snapshots', [])
            for s_data in snapshots_data:
                snapshot = VideoSnapshot(
                    id=uuid.UUID(s_data['id']),
                    video_id=video.id,
                    views_count=s_data['views_count'],
                    likes_count=s_data['likes_count'],
                    comments_count=s_data['comments_count'],
                    reports_count=s_data['reports_count'],
                    delta_views_count=s_data['delta_views_count'],
                    delta_likes_count=s_data['delta_likes_count'],
                    delta_comments_count=s_data['delta_comments_count'],
                    delta_reports_count=s_data['delta_reports_count'],
                    created_at=parse_datetime(s_data['created_at'])
                )
                session.add(snapshot)
            
            if (i + 1) % 100 == 0:
                await session.commit()
                logger.info(f"Processed {i + 1} videos...")

        await session.commit()
        logger.info("Data import completed successfully.")

    except Exception as e:
        logger.exception(f"Error importing data: {e}")
        await session.rollback()

async def main():
    setup_logging()
    db_url = settings.database_url
    
    engine = create_async_engine(db_url, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        file_path = os.path.join(os.getcwd(), 'videos.json')
        await seed_data(file_path, session)

    await engine.dispose()

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
