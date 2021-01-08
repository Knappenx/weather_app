from django.test import TestCase, Client

from django.contrib.auth.models import User

from urllib.parse import urlencode


class RbacTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.user.set_password('12345678')
        self.user.save()

    def test_validation_correct(self):
        client = Client()
        login = client.login(username=self.user.username, password='12345678')
        self.assertTrue(login)

    def test_validation_wrong(self):
        client = Client()
        login = client.login(username=self.user.username, password='hdjvbei')
        self.assertFalse(login)

    def test_successfull_login_view(self):
        client = Client()
        response = client.post('/rbac/login/',
                               data=urlencode({"username": self.user.username,
                                               "password": "12345678"}),
                               content_type="application/x-www-form-urlencoded")
        self.assertEqual(302, response.status_code)

    def test_failed_login_view(self):
        client = Client()
        response = client.post('/rbac/login/', data=urlencode({"username": self.user.username,
                                                               "password": "87654321"}),
                               content_type="application/x-www-form-urlencoded")
        self.assertEqual('Incorrect password or user',
                         response.context['user_form'].errors['username'][0])
