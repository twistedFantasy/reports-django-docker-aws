# Generated by Django 2.2.4 on 2019-08-08 16:49

from django.db import migrations
import fernet_fields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('deliveries', '0004_target_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='target',
            name='password',
            field=fernet_fields.fields.EncryptedTextField(blank=True, help_text='For S3, this is your secret', max_length=256, null=True, verbose_name='Password'),
        ),
    ]
