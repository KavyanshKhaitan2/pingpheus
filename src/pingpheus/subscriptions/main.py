import asyncio
from ..settings import app
from ..models import PingPhrase


@app.event("message")
async def message_received(logger, message):
    actions = []
    async for pingphrase in PingPhrase.all():
        active = False
        for phrase in pingphrase.comma_seperated_words.split(','):
            if phrase.strip() in message["text"]:
                active = True
        if not active:
            continue
        actions.append(app.client.chat_postMessage(
            channel=pingphrase.owner,
            text=f"{pingphrase.id} https://{message['team']}.slack.com/archives/{message['channel']}/p{message['ts'].replace('.', '')}",
        ))

    await asyncio.gather(*actions)
