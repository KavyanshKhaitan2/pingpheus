import asyncio
import json
from dataclasses import dataclass

from .. import models
from ..settings import app
from .home import _open_app_home


@dataclass
class PingwordModalState:
    pingwords: list[str]
    conversation_ids: list[str]
    user_ids: list[str]
    ping_from_people: bool = True
    ping_from_apps: bool = False


def get_state_from_slack_view(
    slack_view, ping_from_people=True, ping_from_apps=False
) -> PingwordModalState:
    slack_state = slack_view["state"]["values"]

    pingwords = [
        x.strip()
        for x in (
            slack_state["apphome_new_pingword-pingwords"]["input"]["value"] or ""
        ).split(",")
    ]
    conversations = slack_state["apphome_new_pingword-conversations"]["input"][
        "selected_conversations"
    ]
    users = slack_state["apphome_new_pingword-users"]["input"]["selected_users"]
    return PingwordModalState(
        pingwords=pingwords,
        conversation_ids=conversations,
        user_ids=users,
        ping_from_people=ping_from_people,
        ping_from_apps=ping_from_apps,
    )


def _draw_pingword_modal(state: PingwordModalState | None = None):
    if state is None:
        state = PingwordModalState([], [], [])

    conversations_select = {
        "type": "section",
        "block_id": "apphome_new_pingword-conversations",
        "text": {
            "type": "mrkdwn",
            "text": "*Select conversations* _(optional)_\nOnly select if you want pingwords to activate in specific conversations",
        },
        "accessory": {
            "type": "multi_conversations_select",
            "placeholder": {
                "type": "plain_text",
                "text": "Select conversations",
                "emoji": True,
            },
            "initial_conversations": state.conversation_ids,
            "action_id": "input",
        },
    }
    if not state.conversation_ids:
        del conversations_select["accessory"]["initial_conversations"]

    users_select = {
        "type": "section",
        "block_id": "apphome_new_pingword-users",
        "text": {
            "type": "mrkdwn",
            "text": "*Select users* _(optional)_\nOnly select if you want pingwords to activate when specific people send messages",
        },
        "accessory": {
            "type": "multi_users_select",
            "placeholder": {
                "type": "plain_text",
                "text": "Select users",
                "emoji": True,
            },
            "initial_users": state.user_ids,
            "action_id": "input",
        },
    }

    if not state.user_ids:
        del users_select["accessory"]["initial_users"]

    return {
        "type": "modal",
        "callback_id": "new_pingword_modal",
        "title": {
            "type": "plain_text",
            "text": "Create new pingword",
            "emoji": True,
        },
        "submit": {"type": "plain_text", "text": "Submit", "emoji": True},
        "close": {"type": "plain_text", "text": "Cancel", "emoji": True},
        "private_metadata": json.dumps(
            {
                "ping_from_people": state.ping_from_people,
                "ping_from_apps": state.ping_from_apps,
            }
        ),
        "blocks": [
            {
                "type": "input",
                "block_id": "apphome_new_pingword-pingwords",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "input",
                    "initial_value": ", ".join(state.pingwords),
                },
                "label": {
                    "type": "plain_text",
                    "text": "Pingwords - seperate by commas!",
                    "emoji": True,
                },
                "optional": False,
            },
            conversations_select,
            users_select,
            {
                "type": "rich_text",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {"type": "text", "text": "Who's allowed to ping?"}
                        ],
                    }
                ],
            },
            {
                "type": "actions",
                "block_id": "apphome_new_pingword-ping_from",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": f"People: {'ON' if state.ping_from_people else 'OFF'}",
                        },
                        "style": "primary" if state.ping_from_people else "danger",
                        "action_id": "apphome_new_pingword-ping_from_people",
                        "value": f"{not state.ping_from_people},{state.ping_from_apps}",
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": f"Apps: {'ON' if state.ping_from_apps else 'OFF'}",
                        },
                        "style": "primary" if state.ping_from_apps else "danger",
                        "action_id": "apphome_new_pingword-ping_from_apps",
                        "value": f"{state.ping_from_people},{not state.ping_from_apps}",
                    },
                ],
            },
        ],
    }


@app.action("apphome_new_pingword")
async def create_new_pingword(ack, body):
    view = _draw_pingword_modal()
    await asyncio.gather(
        app.client.views_open(
            # Pass a valid trigger_id within 3 seconds of receiving it
            trigger_id=body["trigger_id"],
            view=view,
        ),
        ack(),
    )


@app.action({"block_id": "apphome_new_pingword-ping_from"})
async def toggle_ping_buttons(ack, body):
    ack()
    ping_from_people, ping_from_apps = [
        x == "True" for x in body["actions"][0]["value"].split(",")
    ]
    state = get_state_from_slack_view(
        body["view"], ping_from_people=ping_from_people, ping_from_apps=ping_from_apps
    )
    view = _draw_pingword_modal(state)
    await app.client.views_update(view_id=body["view"]["id"], view=view)


@app.view("new_pingword_modal")
async def submit_new_pingword_modal(ack, body, logger):
    await ack()
    slack_view = body["view"]
    metadata = json.loads(slack_view["private_metadata"])
    ping_from_people = metadata["ping_from_people"]
    ping_from_apps = metadata["ping_from_apps"]
    state = get_state_from_slack_view(
        slack_view, ping_from_people=ping_from_people, ping_from_apps=ping_from_apps
    )
    user_id = body['user']['id']
    
    pingphrase = models.PingPhrase(owner=user_id, comma_seperated_words = ','.join(state.pingwords), whitelisted_conversation_ids = state.conversation_ids, whitelisted_user_ids = state.user_ids)
    await pingphrase.save()
    await _open_app_home(user_id)
    logger.info(f"<@{user_id}> has created a new pingphrase: {pingphrase}")
