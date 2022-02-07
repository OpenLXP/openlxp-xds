# Generated by Django 3.2.9 on 2021-11-08 20:26
import logging

from django.db import migrations

GROUPS = ['System Operator', 'Experience Owner', 'Experience Manager',
          'Experience Facilitator', 'Experience Participant']
MODELS = ['course spotlight', 'experience', 'search sort option',
          'search filter', 'interest list', 'course information mapping',
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

    for custom in MODELS:
        content_type = ContentType.objects.get(
            app_label='core',
            model=custom.replace(" ", "")
        )
        Perm.objects.filter(content_type=content_type).delete()
        content_type.delete()

    for custom in MODELS:
        ct = ContentType.objects.filter(
            app_label='core',
            model=custom.replace(" ", "")
        )
        if ct.exists():
            ct.delete()
        ContentType.objects.get_or_create(
            app_label='xds_api',
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
                        ContentType.objects.get(model=value,
                                                app_label='xds_api')
                    model_add_perm, created = \
                        Perm.objects.get_or_create(codename=codename,
                                                   name=name,
                                                   content_type=content_type)
                except Perm.DoesNotExist:
                    logging.warning("Permission not found with name '{}'.".
                                    format(name))
                    continue

                new_group.permissions.add(model_add_perm)

    print("Moved permissions to xds_api app_label.")


def reverse_func(apps, schema_editor):
    # reverse_func() should delete them.
    Group = apps.get_model('auth', 'Group')
    Perm = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    # get new content types and permissions and delete them
    for custom in MODELS:
        content_type = ContentType.objects.get(
            app_label='xds_api',
            model=custom.replace(" ", "")
        )
        Perm.objects.filter(content_type=content_type).delete()
        content_type.delete()

    # recreate the old content types and permissions
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
                                                   content_type=content_type)
                except Perm.DoesNotExist:
                    logging.warning("Permission not found with name '{}'.".
                                    format(name))
                    continue

                new_group.permissions.add(model_add_perm)


class Migration(migrations.Migration):
    dependencies = [
        ('xds_api', '0002_update_permissions'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
