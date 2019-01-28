from django.test import TestCase
from django.contrib.auth.models import User

from accounts.serializers import UserSerializer


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
