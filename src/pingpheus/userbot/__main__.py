import asyncio
import json
import time

import websockets

from .. import settings
from ..settings import logger
from ..shortcuts import get_channel_list
from .websocket import SlackWebsocketClient

client = SlackWebsocketClient(settings.XOXC_USER_TOKEN, settings.XOXD_USER_TOKEN)

@client.onevent("on_startup")
async def connect_wss(event, websocket):
    start = time.time()
    channel_list = await get_channel_list()
    logger.info(f"Fetched channel list in {time.time() - start} seconds")

    for i, channel in enumerate(channel_list):
        if channel["is_archived"]:
            continue
        data = json.dumps(
            {"channel_id":channel['id'],"type":"temp_channel_sub","id":i}
        )
        await websocket.send(data)
    logger.info("Intial websockets sent")
        


async def main():
    await client.connect()

if __name__ == "__main__":
    asyncio.run(main())
