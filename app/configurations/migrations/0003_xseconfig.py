# Generated by Django 3.2.12 on 2022-02-08 22:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configurations', '0002_courseinformationmapping'),
    ]

    operations = [
        migrations.AddField(
            model_name='XDSConfiguration',
            name='target_xse_host',
            field=models.CharField(max_length=200, help_text='Enter the XSE Host to search', default='http://localhost:9200'),
        ),
        migrations.AddField(
            model_name='XDSConfiguration',
            name='target_xse_index',
            field=models.CharField(max_length=200, help_text='Enter the XSE Index to search', default='metadata'),
        ),
    ]
