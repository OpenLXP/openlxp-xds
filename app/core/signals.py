from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from notifications.signals import notify

from .models import InterestList


@receiver(m2m_changed, sender=InterestList.experiences.through)
def interest_list_notify(sender, instance, action, reverse, pk_set, **kwargs):
    if action == 'post_add' and not reverse:
        notify.send(instance, recipient=instance.subscribers.all(),
                    verb='experiences added', added=pk_set,
                    list_name=instance.name)
