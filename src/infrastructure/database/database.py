from sqlalchemy.ext.asyncio import (
    create_async_engine, async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase

from src.config import settings

DATABASE_URL = settings.database_url
DATABASE_PARAMS = {
    "echo": False,
    "pool_size": settings.POOL_SIZE,
    "max_overflow": settings.MAX_OVERFLOW,
}

async_engine = create_async_engine(
    DATABASE_URL,
    pool_recycle=3600,
    connect_args={
        "timeout": 30,
        "server_settings": {
            "application_name": settings.APPLICATION_NAME,
            "tcp_keepalives_idle": "30",
            "tcp_keepalives_interval": "10",
            "tcp_keepalives_count": "5",
        },
    },
    **DATABASE_PARAMS,
)
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass
