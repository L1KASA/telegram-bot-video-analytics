from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.repositories.video_repository import AnalyticsRepository
from src.infrastructure.llm.nlu_impl import OllamaNLUService
from src.infrastructure.llm.ollama_client import OllamaClient, OllamaConfig
from src.domain.services.nlu_service import NLUService
from src.config import settings
from src.logging import logger

router = Router()

def get_nlu_service() -> NLUService:
    ollama_config = OllamaConfig(base_url=settings.LLM_BASE_URL, model=settings.LLM_MODEL)
    client = OllamaClient(ollama_config)
    return OllamaNLUService(client)

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Приветствую! Я Telegram-бот для аналитики по видео на основе задач на естественном языке.\n"
        "Задайте мне вопрос, например:\n"
        "«Сколько всего видео есть в системе?»"
    )

@router.message()
async def handle_analytics_query(message: Message, session: AsyncSession):
    user_text = message.text
    if message.bot:
        await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    if not user_text:
        return

    try:
        nlu_service = get_nlu_service()
        query = await nlu_service.parse_query(user_text)
        
        if not query:
            await message.answer("Извините, я не понял вашу просьбу. Пожалуйста, попробуйте перефразировать.")
            return
        repo = AnalyticsRepository(session)
        result_value = await repo.execute_query(query)
        await message.answer(str(result_value))
        
    except Exception as e:
        logger.exception(f"Сообщение об обработке ошибки: {e}")
        await message.answer("При выполнении запроса произошла ошибка.")

def register_handlers(dp):
    dp.include_router(router)
