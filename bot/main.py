import os
import asyncio

from aiogram import Bot, Dispatcher
import dotenv
from .commands import nonlogin, security, general, trades

async def main():
    dotenv.load_dotenv()
    bot = Bot(os.environ["TOKEN"])
    dp = Dispatcher()

    dp.include_routers(nonlogin.router, security.router, general.router, trades.router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
