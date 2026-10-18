from tortoise.models import Model
from tortoise import fields, Tortoise
from .settings import DATABASE_URL

class PingPhrase(Model):
    # Defining `id` field is optional, it will be defined automatically
    # if you haven't done it yourself
    id = fields.IntField(primary_key=True)
    owner = fields.CharField(max_length=255)
    word = fields.CharField(max_length=255)
