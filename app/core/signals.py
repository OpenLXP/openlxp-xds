import logging

from django.conf import settings
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from notifications.signals import notify
from openlxp_notifications.management.commands.\
    trigger_subscribed_list_update import \
    trigger_update
from openlxp_notifications.models import email

from .models import InterestList

logger = logging.getLogger('dict_config_logger')


@receiver(m2m_changed, sender=InterestList.experiences.through)
def interest_list_notify(sender, instance, action, reverse, pk_set, **kwargs):
    if action == 'post_add' and not reverse:
        notify.send(instance, recipient=instance.subscribers.all(),
                    verb='experiences added', added=pk_set,
                    list_name=instance.name)
        #  setting variables for email request

        recipient_list = list(instance.subscribers.values_list(
            "email", "first_name", 'last_name'))
        owner = instance.owner
        list_name = instance.name

        if settings.LOGIN_REDIRECT_URL:
            list_url = (settings.LOGIN_REDIRECT_URL + "/lists/"
                        + str(instance.id))
        else:
            list_url = "ECC -> Subscribed Lists: " + instance.name

        try:
            email_type = email.objects.get(
                    reference='Subscribed_list_update')

            # trigger email notification
            trigger_update(
                email_type, recipient_list, owner,
                list_name, list_url)
        except email.DoesNotExist:
            logger.error('Email configuration for subscribed list '
                         'updates does not exist. Please add a '
                         '"Subscribed_list_update" email template '
                         'for the email alert. ')
