import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties


from bot.handlers import register_handlers
from config import BOT_TOKEN

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Функция для настройки и запуска бота
async def main():
    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Регистрация хэндлеров
    dp.include_router(register_handlers(bot))

    # Пропуск накопившихся апдейтов и запуск поллинга
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())