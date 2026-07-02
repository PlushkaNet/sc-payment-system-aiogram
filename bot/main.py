import os
import asyncio

from aiogram import Bot, Dispatcher
import aiosqlite
import dotenv

from . import variables
from .commands import nonlogin, security, general, trades

async def main():
    async with aiosqlite.connect(variables.DATABASE_NAME) as db:
        await db.execute("CREATE TABLE IF NOT EXISTS USERS(NAME TEXT UNIQUE, PASSWORD TEXT, BALANCE FLOAT)")
        await db.execute("CREATE TABLE IF NOT EXISTS TRADE_IDS(ID TEXT UNIQUE, COST FLOAT, OWNER_NAME TEXT)")
        await db.execute("CREATE TABLE IF NOT EXISTS SUBSCRIPTIONS(NAME TEXT UNIQUE, TRADEPACK BOOLEAN, NOADS BOOLEAN)")

    dotenv.load_dotenv()
    bot = Bot(os.environ["TOKEN"])
    dp = Dispatcher()

    dp.include_routers(nonlogin.router, security.router, general.router, trades.router)
    await dp.start_polling(bot)

def start():
    asyncio.run(main())
