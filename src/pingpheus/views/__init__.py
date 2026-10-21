from . import home, new_pingword
from ..settings import app

@app.message('pingpheus_please_test_views_for_me')
async def handle_message_b(ack, message, say):
    await ack()
    await say(f"Hi <@{message['user']}>!\nClick on the buttons below to test views.")
    await say(
        text="Click to test views.",
        blocks=[
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Open View 1"},
                        "action_id": "test_view1",
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Open View 2"},
                        "action_id": "test_view2",
                    },
                ],
            },
        ],
    )
