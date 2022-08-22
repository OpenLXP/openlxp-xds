# Generated by Django 3.2.14 on 2022-07-21 07:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configurations', '0004_xdsconfiguration_default_user_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseinformationmapping',
            name='course_code',
            field=models.CharField(default='Course.CourseCode', help_text='Enter the mapping for the code of the course found in the elasticsearch', max_length=200),
        ),
        migrations.AddField(
            model_name='courseinformationmapping',
            name='course_deliveryMode',
            field=models.CharField(default='Course_Instance.DeliveryMode', help_text='Enter the mapping for the delivery mode of the course found in the elasticsearch', max_length=200),
        ),
        migrations.AddField(
            model_name='courseinformationmapping',
            name='course_endDate',
            field=models.CharField(default='Course_Instance.EndDate', help_text='Enter the mapping for the end date of the course found in the elasticsearch', max_length=200),
        ),
        migrations.AddField(
            model_name='courseinformationmapping',
            name='course_instructor',
            field=models.CharField(default='Course_Instance.Instructor', help_text='Enter the mapping for the instructor of the course found in the elasticsearch', max_length=200),
        ),
        migrations.AddField(
            model_name='courseinformationmapping',
            name='course_provider',
            field=models.CharField(default='Course.CourseProviderName', help_text='Enter the mapping for the provider of the course found in the elasticsearch', max_length=200),
        ),
        migrations.AddField(
            model_name='courseinformationmapping',
            name='course_startDate',
            field=models.CharField(default='Course_Instance.StartDate', help_text='Enter the mapping for the start date of the course found in the elasticsearch', max_length=200),
        ),
        migrations.AddField(
            model_name='courseinformationmapping',
            name='course_thumbnail',
            field=models.CharField(default='Technical_Information.Thumbnail', help_text='Enter the mapping for the thumbnail of the course found in the elasticsearch', max_length=200),
        ),
        migrations.AlterField(
            model_name='courseinformationmapping',
            name='course_description',
            field=models.CharField(default='Course.CourseShortDescription', help_text='Enter the mapping for the description of the course found in the elasticsearch', max_length=200),
        ),
        migrations.AlterField(
            model_name='courseinformationmapping',
            name='course_title',
            field=models.CharField(default='Course.CourseTitle', help_text='Enter the mapping for the title of the course found in the elasticsearch', max_length=200),
        ),
        migrations.AlterField(
            model_name='courseinformationmapping',
            name='course_url',
            field=models.CharField(default='Course.CourseURL', help_text='Enter the mapping for the url of the course found in the elasticsearch', max_length=200),
        ),
    ]