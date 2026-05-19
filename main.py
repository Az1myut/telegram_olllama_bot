import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import settings
from handlers.chat import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    # No default ParseMode — send plain text to avoid Markdown parse errors
    bot = Bot(token=settings.telegram_bot_token)

    dp = Dispatcher()
    dp.include_router(router)

    logger.info("Starting bot with model: %s", settings.ollama_model)
    logger.info("Ollama URL: %s", settings.ollama_base_url)

    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())