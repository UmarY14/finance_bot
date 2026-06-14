import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from config import Config
from db.connection import Database
from handlers import categories, start, stats, transactions
from services.category_service import CategoryService
from services.transaction_service import TransactionService
from services.user_service import UserService


async def set_commands(bot: Bot) -> None:
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Register / restart"),
            BotCommand(command="add", description="Add a transaction"),
            BotCommand(command="stats", description="This month's stats"),
            BotCommand(command="history", description="Last 10 transactions"),
            BotCommand(command="categories", description="Manage categories"),
            BotCommand(command="report", description="Export this month to CSV"),
            BotCommand(command="limit", description="Set a category limit"),
            BotCommand(command="monthly", description="Last 3 months comparison"),
            BotCommand(command="cancel", description="Cancel current action"),
        ]
    )


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    config = Config.load()

    db = Database(config.dsn)
    await db.connect()
    await db.migrate()

    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dispatcher = Dispatcher()
    dispatcher["user_service"] = UserService(db)
    dispatcher["category_service"] = CategoryService(db)
    dispatcher["transaction_service"] = TransactionService(db)

    dispatcher.include_router(start.router)
    dispatcher.include_router(transactions.router)
    dispatcher.include_router(stats.router)
    dispatcher.include_router(categories.router)

    await set_commands(bot)
    try:
        await dispatcher.start_polling(bot)
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())
