import asyncio
import os
import sys

from aiogram import Bot, Dispatcher
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.application.use_cases.process_query import ProcessQueryUseCase
from src.config import settings
from src.infrastructure.database.repositories.video_repository import AnalyticsRepository
from src.infrastructure.llm.factory import LLMServiceFactory
from src.infrastructure.telegram.handlers import register_handlers
from src.infrastructure.telegram.middlewares import DbSessionMiddleware, UseCaseMiddleware
from src.logging import setup_logging, logger


async def main():
    setup_logging(level=settings.LOG_LEVEL)
    logger.info("Запуск бота...")

    nlu_service = await LLMServiceFactory.create_validated_service(
        **settings.llm_config
    )

    if not nlu_service:
        logger.info("LLM сервис не инициализирован")
        sys.exit(1)

    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()

    db_url = settings.database_url
        
    engine = create_async_engine(db_url, echo=False)
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session_maker() as session:
        repository = AnalyticsRepository(session)
        use_case = ProcessQueryUseCase(nlu_service, repository)

        dp.update.middleware(DbSessionMiddleware(async_session_maker))
        dp.update.middleware(UseCaseMiddleware(use_case))

        register_handlers(dp)

        logger.info("Бот запущен и готов принимать сообщения")
        try:
            await dp.start_polling(bot)
        finally:
            await bot.session.close()
            await engine.dispose()


if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
