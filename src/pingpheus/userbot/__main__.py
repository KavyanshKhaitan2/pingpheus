import asyncio

from .hooks import client


async def main():
    await client.connect()


if __name__ == "__main__":
    asyncio.run(main())
