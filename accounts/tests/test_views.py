import json

from django.test import TestCase
from django.shortcuts import reverse
from django.contrib.auth import get_user_model

from accounts.serializers import UserSerializer


User = get_user_model()

TEST_USER = {
    'username': 'konni',
    'email': 'test@test.com',
    'password': 'q,1234',
}


class RegisterViewTest(TestCase):
    def test_user_create(self):
        url = reverse('register')
        response = self.client.post(
            url, json.dumps(TEST_USER),
            content_type='application/json')

        self.assertEqual(User.objects.count(), 1)
        # should not return password in response
        self.assertNotIn('password', response.content.decode())

        response_data = json.loads(response.content.decode())
        user = User.objects.get(username=TEST_USER['username'])
        token = user.auth_token.key
        correct_data = dict(
            username=TEST_USER['username'],
            email=TEST_USER['email'],
            token=token)

        self.assertEqual(response_data, correct_data)

    def test_can_not_create_user_with_short_username(self):
        data = TEST_USER.copy()
        data['username'] = 'k'

        url = reverse('register')
        response = self.client.post(
            url, json.dumps(data),
            content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.count(), 0)

    def test_can_not_create_user_with_short_password(self):
        data = TEST_USER.copy()
        data['password'] = 'k'

        url = reverse('register')
        response = self.client.post(
            url, json.dumps(data),
            content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.count(), 0)


class LoginViewTest(TestCase):

    def generate_user(self, data=None):
        if not data:
            data = TEST_USER

        user = UserSerializer(data=data)
        if user.is_valid():
            user.save()

        return user

    def test_user_login_with_correct_password(self):
        self.generate_user()
        url = reverse('login')
        response = self.client.post(
            url, json.dumps(TEST_USER),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content.decode())
        user = User.objects.get(username=TEST_USER['username'])
        token = user.auth_token.key
        correct_data = dict(
            username=TEST_USER['username'],
            email=TEST_USER['email'],
            token=token)

        self.assertEqual(response_data, correct_data)

    def test_user_login_with_incorrect_password(self):
        self.generate_user()
        wrong_data = TEST_USER.copy()
        wrong_data['password'] = 'wrong password'

        url = reverse('login')
        response = self.client.post(
            url, json.dumps(wrong_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
