# Generated by Django 2.2.4 on 2019-08-07 17:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0004_auto_20190807_1733'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='uid',
            field=models.CharField(default='', max_length=64, verbose_name='Unique ID'),
            preserve_default=False,
        ),
    ]
