# Generated by Django 3.1.7 on 2021-03-26 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20210323_2053'),
    ]

    operations = [
        migrations.AddField(
            model_name='searchfilter',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
