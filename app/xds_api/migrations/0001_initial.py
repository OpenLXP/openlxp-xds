# Generated by Django 3.2.9 on 2021-11-08 20:26
import logging

from django.contrib.auth.management import create_permissions
from django.contrib.contenttypes.management import create_contenttypes
from django.db import migrations

GROUPS = ['System Operator', 'Experience Owner', 'Experience Manager',
          'Experience Facilitator', 'Experience Participant']
MODELS = ['course spotlight', 'experience', 'xds configuration',
          'xdsui configuration', 'search sort option', 'search filter',
          'interest list', 'course information mapping',
          'course detail highlight', 'saved filter', 'interest lists',
          'get spotlight courses', 'get experiences', 'add course to lists',
          'interest lists owned', 'interest lists subscriptions',
          'interest list subscribe', 'interest list unsubscribe',
          'saved filters owned', 'saved filters']
PERMISSIONS = ['view', 'add', 'change', 'delete']


def forwards_func(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Perm = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, verbosity=0)
        app_config.models_module = None

    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_contenttypes(app_config, verbosity=0)
        app_config.models_module = None
    
    for custom in MODELS:
        ContentType.objects.get_or_create(
            app_label='core',
            model=custom.replace(" ", "")
        )

    for group in GROUPS:
        new_group, created = Group.objects.get_or_create(name=group)

        for model in MODELS:
            for permission in PERMISSIONS:
                name = 'Can {} {}'.format(permission, model)
                print("Creating {}".format(name))

                model_comb = model
                value = model_comb.replace(" ", "")
                codename = '{}_{}'.format(permission, value)

                try:
                    content_type = \
                        ContentType.objects.get(model=value)
                    model_add_perm, created = \
                        Perm.objects.get_or_create(codename=codename,
                                                   name=name,
                                                   content_type=
                                                   content_type)
                except Perm.DoesNotExist:
                    logging.warning("Permission not found with name '{}'.".
                                    format(name))
                    continue

                new_group.permissions.add(model_add_perm)

    print("Created default group and permissions.")


def reverse_func(apps, schema_editor):
    # forwards_func() creates two Country instances,
    # so reverse_func() should delete them.
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(
        name__in=GROUPS
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
