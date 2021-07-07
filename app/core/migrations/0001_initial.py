# Generated by Django 3.1.13 on 2021-07-07 15:01

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseSpotlight',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('course_id', models.CharField(help_text='Enter the unique Search Engine ID of the course', max_length=200)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ReceiverEmailConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_address', models.EmailField(help_text='Enter email personas addresses to send log data', max_length=254, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='SenderEmailConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender_email_address', models.EmailField(default='openlxphost@gmail.com', help_text='Enter sender email address to send log data from', max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='XDSConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('target_xis_metadata_api', models.CharField(default='http://localhost:8080/api/metadata/', help_text='Enter the XIS api endpoint to query metadata', max_length=200)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='XDSUIConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('search_results_per_page', models.IntegerField(default=10, validators=[django.core.validators.MinValueValidator(1, 'results per page should be at least 1')])),
                ('course_img_fallback', models.ImageField(blank=True, null=True, upload_to='images/')),
                ('xds_configuration', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.xdsconfiguration')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SearchSortOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('display_name', models.CharField(help_text='Enter the display name of the sorting option', max_length=200)),
                ('field_name', models.CharField(help_text='Enter the metadata field name as displayed in Elasticsearch e.g. course.title', max_length=200)),
                ('active', models.BooleanField(default=True)),
                ('xds_ui_configuration', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='search_sort_options', to='core.xdsuiconfiguration')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SearchFilter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('display_name', models.CharField(help_text='Enter the display name of the field to filter on', max_length=200)),
                ('field_name', models.CharField(help_text='Enter the metadata field name as displayed in Elasticsearch e.g. course.title', max_length=200)),
                ('filter_type', models.CharField(choices=[('terms', 'Checkbox')], default='terms', max_length=200)),
                ('active', models.BooleanField(default=True)),
                ('xds_ui_configuration', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.xdsuiconfiguration')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CourseInformationMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('course_title', models.CharField(help_text='Enter the title of the coursefound in the elasticsearch', max_length=200)),
                ('course_description', models.CharField(help_text='Enter the description of the course found in the elasticsearch', max_length=200)),
                ('course_url', models.CharField(help_text='Enter the url of the course found in the elasticsearch', max_length=200)),
                ('xds_ui_configuration', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='course_information', to='core.xdsuiconfiguration')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CourseDetailHighlight',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('display_name', models.CharField(help_text='Enter the display name of the sorting option', max_length=200)),
                ('field_name', models.CharField(help_text='Enter the metadata field name as displayed in Elasticsearch e.g. course.title', max_length=200)),
                ('active', models.BooleanField(default=True)),
                ('highlight_icon', models.CharField(choices=[('clock', 'clock'), ('hourglass', 'hourglass'), ('user', 'user'), ('multi_users', 'multi_users'), ('location', 'location'), ('calendar', 'calendar')], default='user', max_length=200)),
                ('rank', models.IntegerField(default=1, help_text='Order in which highlight show on the course detail page (2 items per row)', validators=[django.core.validators.MinValueValidator(1, 'rank shoud be at least 1')])),
                ('xds_ui_configuration', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_highlights', to='core.xdsuiconfiguration')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='XDSUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=200, unique=True)),
                ('first_name', models.CharField(max_length=200)),
                ('last_name', models.CharField(max_length=200)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
        ),
    ]
