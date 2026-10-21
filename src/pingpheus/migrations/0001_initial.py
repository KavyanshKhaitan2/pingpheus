from tortoise import migrations
from tortoise.migrations import operations as ops
from tortoise import fields

class Migration(migrations.Migration):
    initial = True

    operations = [
        ops.CreateModel(
            name='PingPhrase',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('owner', fields.CharField(max_length=255)),
                ('word', fields.CharField(max_length=255)),
            ],
            options={'table': 'pingphrase', 'app': 'models', 'pk_attr': 'id'},
            bases=['Model'],
        ),
    ]
