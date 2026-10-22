import asyncio
import json
import time

import websockets

from .. import settings
from ..settings import app, logger


async def get_channel_list():
    all_channels = []
    cursor = None

    while True:
        # Fetch a page of conversations asynchronously
        try:
            response = await app.client.conversations_list(
                limit=1000,                    # Recommended page size limit
                cursor=cursor,                # Pass the cursor for pagination
                types="public_channel",  # Specify channel types
                exclude_archived=False,
            )
        except Exception as e:
            logger.error(f"Slack API error: {e}, retrying...")
            continue
        
        # Add the retrieved channels to your list
        all_channels.extend(response["channels"])
        
        # Check if there is a next page
        cursor = response.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            break
        logger.info(f"Fetching channel list... ({len(all_channels)})")

    return all_channels

async def connect_wss():
    start = time.time()
    channel_list = await get_channel_list()

    id = 1
    # Publicly trusted secure endpoint
    url = f"wss://wss-primary.slack.com/?token={settings.XOXC_USER_TOKEN}&sync_desync=1&slack_client=desktop&start_args=%3Fagent%3Dclient%26org_wide_aware%3Dtrue%26agent_version%3D1792581458%26eac_cache_ts%3Dtrue%26cache_ts%3D0%26name_tagging%3Dtrue%26only_self_subteams%3Dtrue%26connect_only%3Dtrue%26ms_latest%3Dtrue&no_query_on_subscribe=1&flannel=3&lazy_channels=1&gateway_server=T09V59WQY1E-2&enterprise_id=E09V59WQY1E&batch_presence_aware=1"
    additional_headers: dict[str, str] = {
        "cookie": f"d={settings.XOXD_USER_TOKEN}",
    }
    async with websockets.connect(
        url, additional_headers=additional_headers
    ) as websocket:
        for i, channel in enumerate(channel_list):
            logger.debug(f"Sent WS for channel #{i}")
            if channel["is_archived"]:
                continue
            data = json.dumps(
                {"channel_id":channel['id'],"type":"temp_channel_sub","id":id}
            )
            await websocket.send(data)
            id += 1
        logger.info(f"Subscribed to all channels in {time.time()-start} seconds.")
        while True:
            response = await websocket.recv()
            data = json.loads(response)
            logger.debug(f">>>  {data["type"]} // {data.get("subtype")}")


if __name__ == "__main__":
    asyncio.run(connect_wss())
