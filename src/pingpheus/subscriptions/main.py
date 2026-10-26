import asyncio

from pingpheus.shortcuts.get_message_link import get_message_link

from ..models import PingPhrase
from ..settings import app


@app.event("message")
async def message_received(logger, message, event, ack):
    ack()
    
    data = {}
    
    if message.get('spoofed', False):
        channels_in = (await app.client.users_conversations())['channels']
        for channel in channels_in:
            if channel['id'] == message['channel']:
                return
    async for pingphrase in PingPhrase.all():
        for phrase in pingphrase.comma_seperated_words.split(","):
            to_match = phrase.lower().strip()
            if to_match in message["text"].lower() or to_match in str(message["blocks"]).lower():
                data.setdefault(pingphrase.owner, [])
                if phrase in data[pingphrase.owner]:
                    continue
                data[pingphrase.owner].append(phrase)

    actions = []
    for user, phrases in data.items():
        actions.append(
            app.client.chat_postMessage(
                channel=user,
                text=", ".join([f"`{x}`" for x in phrases])
                + f"\n\n<{get_message_link(message)}|Message link>",
                mrkdwn=True
            )
        )
    await asyncio.gather(*actions)
