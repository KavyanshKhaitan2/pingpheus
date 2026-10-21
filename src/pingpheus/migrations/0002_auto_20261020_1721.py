from tortoise import migrations
from tortoise.migrations import operations as ops
import functools
from json import dumps, loads
from tortoise import fields

class Migration(migrations.Migration):
    dependencies = [('models', '0001_initial')]

    initial = False

    operations = [
        ops.AddField(
            model_name='PingPhrase',
            name='whitelisted_conversation_ids',
            field=fields.JSONField(encoder=functools.partial(dumps, separators=(',', ':')), decoder=loads),
        ),
        ops.AddField(
            model_name='PingPhrase',
            name='whitelisted_user_ids',
            field=fields.JSONField(encoder=functools.partial(dumps, separators=(',', ':')), decoder=loads),
        ),
    ]
