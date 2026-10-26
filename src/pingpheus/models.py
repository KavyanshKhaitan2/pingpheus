from tortoise.fields import BooleanField
from tortoise import fields
from tortoise.models import Model


class PingPhrase(Model):
    # Defining `id` field is optional, it will be defined automatically
    # if you haven't done it yourself
    id = fields.IntField(primary_key=True)
    owner = fields.CharField(max_length=255)
    comma_seperated_words = fields.CharField(max_length=2048)

    whitelisted_conversation_ids:fields.JSONField[list[str]] = fields.JSONField()
    whitelisted_user_ids:fields.JSONField[list[str]] = fields.JSONField()
    
    ping_from_people = BooleanField(db_default=True)
    ping_from_apps = BooleanField(db_default=False)


class PingPhraseTriggered(Model):
    pingphrase = fields.ForeignKey(PingPhrase, "triggers", on_delete=fields.OnDelete.CASCADE)
    message_ts = fields.CharField(max_length=256)
    thread_ts = fields.CharField(max_length=256, default="")
    marked_as_read = fields.BooleanField(default=False)
