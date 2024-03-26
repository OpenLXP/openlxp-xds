from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from notifications.base.models import is_soft_delete
from notifications.models import Notification


class Command(BaseCommand):
    """This command deletes notifications that are older than some limit"""

    def handle(self, *args, **options):
        expiration_delta = settings.NOTIFICATIONS_EXPIRE_AFTER
        if expiration_delta and isinstance(expiration_delta, timedelta):
            curr = timezone.now()
            limit = curr - expiration_delta
            bad_notifications = Notification.objects.all().\
                filter(timestamp__date__lt=limit)
            if is_soft_delete():
                bad_notifications.mark_all_as_deleted()
                self.stdout.write(
                    self.style.SUCCESS(f"{bad_notifications.count()} old"
                                       " notifications marked deleted"))
            else:
                count, _ = bad_notifications.delete()
                self.stdout.write(
                    self.style.SUCCESS(f"{count} old notifications deleted"))
        else:
            self.stdout.write(
                self.style.WARNING(
                    "NOTIFICATIONS_EXPIRE_AFTER must be set to "
                    "a timedelta in settings.py "
                )
            )
