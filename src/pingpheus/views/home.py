from ..models import PingPhrase
from ..settings import app


@app.event("app_home_opened")
async def open_app_home(ack, event):
    ack()
    await _open_app_home(event["user"])



async def _open_app_home(user_id):
    inner_blocks: list[dict] = []

    for phrase in await PingPhrase.filter(owner=user_id):
        text = "*" + ", ".join(phrase.comma_seperated_words.split(",")) + "*"
        if phrase.whitelisted_user_ids:
            text += "\nOnly when sent by "
            text += ", ".join([f"<@{x}>" for x in phrase.whitelisted_user_ids])
        else:
            text += "\nWhen sent by any user"
        if phrase.whitelisted_conversation_ids:
            text += "\nOnly when sent in "
            text += ", ".join([f"<#{x}>" for x in phrase.whitelisted_conversation_ids])
        else:
            text += "\nWhen sent in any channel"
        inner_blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text,
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Modify",
                        "emoji": True,
                    },
                    "value": str(phrase.id),
                    "action_id": "apphome_pingphrase_modify",
                },
            },
        )

    if not inner_blocks:
        inner_blocks.append(
            {
                "type": "rich_text",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {
                                "type": "text",
                                "text": "No pingphrases found, create a new one!",
                            }
                        ],
                    }
                ],
            }
        )

    await app.client.views_publish(
        user_id=user_id,
        # A simple view payload for a modal
        view={
            "type": "home",
            "blocks": [
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Create new pingword",
                                "emoji": True,
                            },
                            "action_id": "apphome_new_pingword",
                            "style": "primary",
                        }
                    ],
                },
                {"type": "divider"},
                {
                    "type": "context",
                    "elements": [{"type": "mrkdwn", "text": "Your pingwords"}],
                },
                *inner_blocks,
            ],
        },
    )
