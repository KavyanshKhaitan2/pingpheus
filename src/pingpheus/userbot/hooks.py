import traceback
import anyio
import hashlib
import hmac
import json
import logging
import time

import aiohttp

from .. import settings
from ..settings import logger, app
from ..shortcuts import get_channel_list
from .websocket import SlackWebsocketClient

client = SlackWebsocketClient(settings.XOXC_USER_TOKEN, settings.XOXD_USER_TOKEN)


@client.onevent("hello")
async def connect_wss(event, websocket):
    start = time.time()
    try:
        async with await anyio.open_file('channel_list.json.cache', 'r') as f:
            data = json.loads(await f.read())
            if data['ts'] < time.time() - 3600:
                logger.info("Cache is old, reloading channel list...")
                create_new_list = True
            else:
                create_new_list = False
                channel_list = data["channels"]
    except Exception:
        create_new_list = True
    
    if create_new_list:
        channel_list = await get_channel_list()
    
        async with await anyio.open_file('channel_list.json.cache', 'w') as f:
            raw = json.dumps({"ts": int(time.time()), "channels": channel_list})
            await f.write(raw)
    
    logger.info(f"Fetched channel list in {time.time() - start} seconds")

    for i, channel in enumerate(channel_list):
        if channel["is_archived"]:
            continue
        data = json.dumps(
            {"channel_id": channel["id"], "type": "temp_channel_sub", "id": i}
        )
        await websocket.send(data)
    logger.info("Intial websockets sent")
    logging.getLogger("websockets").setLevel(logging.WARNING)

@client.onevent("message")
async def on_message(event, data):
    try:
        if data.get('hidden', False):
            return
        
        logger.debug("INCOMING: " + str(data))
        auth_test = await app.client.auth_test()
        api_app_id = auth_test['app_id']
        team_id = data.get('team') or data.get('source_team') or auth_test['team_id']
        blocks = data.get("blocks") or data.get("message", {}).get("blocks")

        outgoing = {
            "token": "deprecated!",
            "type": "event_callback",
            "team_id": team_id,
            "team": team_id,
            "api_app_id": api_app_id,
            "event": {
                "type": "message",
                "subtype": data.get("subtype"),
                "team": team_id,
                "channel": data['channel'],
                "user": data.get('user') or data['bot_id'],
                "ts": data['ts'],
                "channel_type": "channel",
                "blocks": blocks,
                "text": data["text"],
                "spoofed": True
            },
            "client_msg_id": data.get("client_msg_id")
        }
        logger.debug("OUTGOING: " + str(outgoing))
        await send_request(outgoing)
    except Exception:
        print(event, data)
        raise

async def send_request(data):
    raw_payload = json.dumps(data)
    timestamp = str(int(time.time()))

    sig_basestring = "v0:" + timestamp + ":" + raw_payload

    signature = (
        "v0="
        + hmac.new(
            settings.SLACK_SIGNING_SECRET.encode("utf-8"),
            sig_basestring.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
    )
    headers = {"X-Slack-Request-Timestamp": timestamp, "X-Slack-Signature": signature, "Content-Type": "application/json", "User-Agent": "Slackbot 1.0 (+https://api.slack.com/robots)"}
    async with aiohttp.ClientSession() as session:  # noqa
        while True:
            try:
                async with session.post(
                    "http://localhost:8000/slack/events",
                    headers=headers,
                    data=raw_payload,
                ) as _:
                    logger.debug("Sent successfully!")
                break
            except Exception: #  noqa
                continue