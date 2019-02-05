import json

from django.test import TestCase
from django.shortcuts import reverse

from accounts.serializers import UserSerializer


TEST_USER = {
    'username': 'konni',
    'email': 'test@test.com',
    'password': 'q,1234',
}


class UserViewTest(TestCase):
    def test_user_create(self):
        url = reverse('user_create')
        response = self.client.post(
            url, json.dumps(TEST_USER),
            content_type='application/json')

        self.assertNotIn('password', response.content.decode())
        
        response_data = json.loads(response.content.decode())
        self.assertEqual(response_data['username'], TEST_USER['username'])
        self.assertEqual(response_data['email'], TEST_USER['email'])


class LoginViewTest(TestCase):

    def generate_user(self, data=None):
        if not data:
            data = TEST_USER

        user = UserSerializer(data=data)
        if user.is_valid():
            user.save()

        return user

    def test_user_login(self):
        self.generate_user()
        url = reverse('login')
        response = self.client.post(
            url, json.dumps(TEST_USER),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'token')
