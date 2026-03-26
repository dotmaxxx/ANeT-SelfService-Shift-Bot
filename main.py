import os
import asyncio
from dotenv import load_dotenv
from anet import Driver
from bot import Bot

load_dotenv()
token = os.getenv("TOKEN")

async def main():
    driver = Driver()
    bot = Bot(token, driver)
    driver.setBot(bot)
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
