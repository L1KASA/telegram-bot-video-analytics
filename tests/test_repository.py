import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from testcontainers.postgres import PostgresContainer
from datetime import datetime

from src.infrastructure.database.models import Base, Video
from src.infrastructure.database.repositories.video_repository import AnalyticsRepository
from src.domain.value_objects.analytics_query import AnalyticsQuery
from src.domain.value_objects.entity_type import EntityType
from src.domain.value_objects.aggregation_type import AggregationType
from src.domain.value_objects.metric_type import MetricType

@pytest_asyncio.fixture(scope="module")
async def postgres_container():
    """Starts a PostgreSQL container for testing."""
    postgres = PostgresContainer("postgres:16-alpine")
    postgres.start()
    
    # Get async driver URL
    url = postgres.get_connection_url().replace("psycopg2", "asyncpg")
    yield url
    postgres.stop()

@pytest_asyncio.fixture()
async def db_session(postgres_container):
    """Creates a database session."""
    engine = create_async_engine(postgres_container, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session
    
    await engine.dispose()

@pytest.mark.asyncio
async def test_repository_execution(db_session):
    """Test the execution of an analytics query."""
    # Prepare data
    video = Video(
        id="e6332496-096e-4402-9ca9-231a40348255",
        creator_id="test_creator",
        views_count=100,
        likes_count=10,
        comments_count=5,
        reports_count=0,
        video_created_at=datetime.now()
    )
    db_session.add(video)
    await db_session.commit()
    
    # Create Query object
    query = AnalyticsQuery(
        entity=EntityType.VIDEO,
        aggregations=AggregationType.COUNT,
        metric=MetricType.VIEWS,
        filters={},
        group_by=None
    )
    
    # Execute
    repo = AnalyticsRepository(db_session)
    result = await repo.execute_query(query)
    
    # Verify
    assert result == 1
    
    # Test sum
    query_sum = AnalyticsQuery(
        entity=EntityType.VIDEO,
        aggregations=AggregationType.SUM,
        metric=MetricType.VIEWS,
        filters={},
        group_by=None
    )
    result_sum = await repo.execute_query(query_sum)
    assert result_sum == 100
