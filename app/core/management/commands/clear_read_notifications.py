from django.core.management.base import BaseCommand
from notifications.base.models import is_soft_delete
from notifications.models import Notification


class Command(BaseCommand):
    """This command deletes notifications that have already been read"""

    def handle(self, *args, **options):
        bad_notifications = Notification.objects.all().read()
        if is_soft_delete():
            bad_notifications.mark_all_as_deleted()
            self.stdout.write(
                self.style.SUCCESS(f"{bad_notifications.count()} read"
                                   " notifications marked deleted"))
        else:
            count, _ = bad_notifications.delete()
            self.stdout.write(
                self.style.SUCCESS(f"{count} read notifications deleted"))
