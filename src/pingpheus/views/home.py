from ..settings import app


@app.event("app_home_opened")
def open_app_home(ack, event):
    ack()
    app.client.views_publish(
        user_id=event["user"],
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
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": "Insert pingword here"},
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Actions",
                            "emoji": True,
                        },
                        "value": "click_me_123",
                        "action_id": "button-action",
                    },
                },
            ],
        },
    )
