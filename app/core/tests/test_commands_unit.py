from core.models import Experience, InterestList
from django.conf import settings
from django.core.management import call_command
from django.test import tag
from users.models import XDSUser

from .test_setup import TestSetUp


@tag('unit')
class CommandTests(TestSetUp):
    """Test cases for notification commands """

    def test_clear_old_notifications(self):
        """Test that only old notifications are cleared"""
        id = '12345'
        course = Experience(metadata_key_hash=id)
        course.save()
        id_2 = '54321'
        course_2 = Experience(metadata_key_hash=id_2)
        course_2.save()
        user = XDSUser.objects.create_user(self.email,
                                           self.password,
                                           first_name=self.first_name,
                                           last_name=self.last_name)
        list = InterestList(owner=user,
                            name="test list",
                            description="test desc")
        list.save()
        list.subscribers.add(user)
        list.experiences.add(course)
        self.assertEqual(user.notifications.count(), 1)

        expiration_delta = settings.NOTIFICATIONS_EXPIRE_AFTER

        notification_old = user.notifications.first()
        notification_old.timestamp = notification_old.timestamp - \
            expiration_delta - expiration_delta
        notification_old.mark_as_read()

        list.experiences.add(course_2)
        self.assertEqual(user.notifications.count(), 2)

        call_command('clear_old_notifications')
        self.assertEqual(user.notifications.count(), 1)

    def test_clear_read_notifications(self):
        """Test that only read notifications are cleared"""
        id = '12345'
        course = Experience(metadata_key_hash=id)
        course.save()
        id_2 = '54321'
        course_2 = Experience(metadata_key_hash=id_2)
        course_2.save()
        user = XDSUser.objects.create_user(self.email,
                                           self.password,
                                           first_name=self.first_name,
                                           last_name=self.last_name)
        list = InterestList(owner=user,
                            name="test list",
                            description="test desc")
        list.save()
        list.subscribers.add(user)
        list.experiences.add(course)
        self.assertEqual(user.notifications.count(), 1)

        user.notifications.first().mark_as_read()
        list.experiences.add(course_2)
        self.assertEqual(user.notifications.count(), 2)

        call_command('clear_read_notifications')
        self.assertEqual(user.notifications.count(), 1)
