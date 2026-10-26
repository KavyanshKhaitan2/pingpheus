from tortoise import migrations
from tortoise.migrations import operations as ops
from tortoise.fields.base import OnDelete
from tortoise import fields

class Migration(migrations.Migration):
    dependencies = [('models', '0003_auto_20261020_1915')]

    initial = False

    operations = [
        ops.CreateModel(
            name='PingPhraseTriggered',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('pingphrase', fields.ForeignKeyField('models.PingPhrase', source_field='pingphrase_id', db_constraint=True, to_field='id', related_name='triggers', on_delete=OnDelete.CASCADE)),
                ('message_ts', fields.CharField(max_length=256)),
                ('thread_ts', fields.CharField(default='', max_length=256)),
                ('marked_as_read', fields.BooleanField(default=False)),
            ],
            options={'table': 'pingphrasetriggered', 'app': 'models', 'pk_attr': 'id'},
            bases=['Model'],
        ),
        ops.AddField(
            model_name='PingPhrase',
            name='ping_from_apps',
            field=fields.BooleanField(db_default=False),
        ),
        ops.AddField(
            model_name='PingPhrase',
            name='ping_from_people',
            field=fields.BooleanField(db_default=True),
        ),
    ]
