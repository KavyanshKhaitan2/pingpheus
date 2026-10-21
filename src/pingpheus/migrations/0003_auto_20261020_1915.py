from tortoise import migrations
from tortoise.migrations import operations as ops
from tortoise import fields

class Migration(migrations.Migration):
    dependencies = [('models', '0002_auto_20261020_1721')]

    initial = False

    operations = [
        ops.AddField(
            model_name='PingPhrase',
            name='comma_seperated_words',
            field=fields.CharField(max_length=2048),
        ),
        ops.RemoveField(model_name='PingPhrase', name='word'),
    ]
