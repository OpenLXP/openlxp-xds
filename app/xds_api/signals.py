import logging

from django.db.models.signals import post_migrate
from django.dispatch import receiver

logger = logging.getLogger('dict_config_logger')

GROUPS = ['System Operator', 'Experience Owner', 'Experience Manager',
          'Experience Facilitator', 'Experience Participant']
MODELS = ['statement forward', ]
PERMISSIONS = ['view', 'add', 'change', 'delete']


@receiver(post_migrate)
def add_permissions(sender, verbosity, stdout, using, apps, **kwargs):
    Group = apps.get_model('auth', 'Group')
    Perm = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    for custom in MODELS:
        ContentType.objects.get_or_create(
            app_label='xds_api',
            model=custom.replace(" ", "")
        )

    for group in GROUPS:
        new_group, created = Group.objects.get_or_create(name=group)

        for model in MODELS:
            for permission in PERMISSIONS:
                name = 'Can {} {}'.format(permission, model)
                if verbosity > 1:
                    stdout.write(msg="Creating {}".format(name))
                    stdout.flush()

                model_comb = model
                value = model_comb.replace(" ", "")
                codename = '{}_{}'.format(permission, value)

                try:
                    content_type = \
                        ContentType.objects.using(using).get(model=value)
                    model_add_perm, created = \
                        Perm.objects.using(using).get_or_create(
                            codename=codename,
                            name=name,
                            content_type=content_type)
                    if not new_group.permissions.contains(model_add_perm):
                        new_group.permissions.add(model_add_perm)
                except Perm.DoesNotExist:
                    if verbosity > 0:
                        stdout.write(
                            msg="Permission not found with name '{}'.".
                            format(name))
                        stdout.flush()
                    continue
