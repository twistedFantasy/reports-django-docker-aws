# Generated by Django 2.2.4 on 2019-08-08 16:45

from django.db import migrations
import fernet_fields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('deliveries', '0003_remove_target__password'),
    ]

    operations = [
        migrations.AddField(
            model_name='target',
            name='password',
            field=fernet_fields.fields.EncryptedTextField(null=True),
        ),
    ]