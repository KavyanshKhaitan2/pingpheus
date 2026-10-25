
def get_message_link(message):
    return f"https://{message['team']}.slack.com/archives/{message['channel']}/p{message['ts'].replace('.', '')}"
