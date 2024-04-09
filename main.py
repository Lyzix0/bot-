import asyncio
import logging

from scripts.bot import bot
from scripts.bot import dp


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, filename="logs.lg")
    asyncio.run(main())
