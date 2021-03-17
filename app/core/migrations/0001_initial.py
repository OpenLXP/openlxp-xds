# Generated by Django 3.1.7 on 2021-03-02 21:42

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='XDSConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('target_xis_es_api', models.CharField(help_text='Enter the XIS api endpoint to query ElasticSearch', max_length=200)),
                ('target_xis_metadata_api', models.CharField(help_text='Enter the XIS api endpoint to query metadata', max_length=200)),
            ],
        ),
    ]
