from rest_framework.test import APITestCase

from core.models import Course, InterestList, XDSUser


class TestSetUp(APITestCase):
    """Class with setup and teardown for tests in XDS"""

    def setUp(self):
        """Function to set up necessary data for testing"""
        self.email = "test@test.com"
        self.password = "test1234"
        self.first_name = "Jill"
        self.last_name = "doe"
        self.userDict = {
            "email": self.email,
            "password": self.password,
            "first_name": self.first_name,
            "last_name": self.last_name
        }
        self.userDict_login = {
            "username": self.email,
            "password": self.password
        }

        self.userDict_login_fail = {
            "username": "test@test.com",
            "password": "test"
        }

        self.user_1 = XDSUser.objects.create_user("test3@test.com",
                                                  "1234",
                                                  first_name="john",
                                                  last_name="doe")
        self.user_2 = XDSUser.objects.create_user('test2@test.com',
                                                  'test1234',
                                                  first_name='Jane',
                                                  last_name='doe')
        self.list_1 = InterestList(owner=self.user_1,
                                   name="list 1",
                                   description='list 1')
        self.list_2 = InterestList(owner=self.user_2,
                                   name="list 2",
                                   description='list 2')
        self.list_3 = InterestList(owner=self.user_2,
                                   name="list 3",
                                   description='list 3')
        self.list_1.save()
        self.list_2.save()
        self.list_3.save()
        self.course_1 = Course('1234')
        self.course_1.save()
        self.list_1.courses.add(self.course_1)
        self.list_2.courses.add(self.course_1)

        return super().setUp()

    def tearDown(self):
        return super().tearDown()
