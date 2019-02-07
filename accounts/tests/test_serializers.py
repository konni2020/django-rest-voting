from django.test import TestCase
from django.contrib.auth import get_user_model

from accounts.serializers import UserSerializer


User = get_user_model()

TEST_USER = {
    'username': 'konni',
    'email': 'test@test.com',
    'password': 'q,1234',
}


class UserSerializerTest(TestCase):

    def test_create_user(self):
        serializer = UserSerializer(data=TEST_USER)
        if serializer.is_valid():
            serializer.save()

        self.assertEqual(User.objects.count(), 1)

    def test_can_not_create_user_with_short_username(self):
        data = TEST_USER.copy()
        data['username'] = 'k'

        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()

        self.assertEqual(User.objects.count(), 0)

    def test_can_not_create_user_with_short_password(self):
        data = TEST_USER.copy()
        data['password'] = 'k'

        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()

        self.assertEqual(User.objects.count(), 0)
